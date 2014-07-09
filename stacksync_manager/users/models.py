from django.db import models
from keystoneclient.v2_0 import client
from swiftclient import client as swift
from django.conf import settings
import uuid

def prefix():
    return make_uuid().split('-')[0]


def make_uuid():
    return str(uuid.uuid4())


def create_container(token_id='', keystone_username='', swift_url='', swift_container=''):
    """creates the container in swift with read and write permissions"""
    user_and_tenant = settings.KEYSTONE_TENANT + ':' + keystone_username
    headers = {'x-container-read': user_and_tenant, 'x-container-write': user_and_tenant}
    swift.put_container(swift_url, token_id, swift_container,
                        headers=headers)


class StacksyncUser(models.Model):
    id = models.CharField(max_length=37, primary_key=True, default=make_uuid(), editable=False)
    name = models.CharField(max_length=200)
    email = models.CharField(max_length=200)
    swift_user = models.CharField(max_length=200)
    swift_account = models.CharField(max_length=200)
    quota_limit = models.IntegerField(default=0)
    quota_used = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = settings.USER_TABLE

    def get_keystone_tenant(self):
        tenants = self.keystone.tenants.list()
        return [x for x in tenants if x.name == settings.KEYSTONE_TENANT][0]

    def __init__(self,  *args, **kwargs):

        self.keystone = kwargs.get('keystone', None)
        if not self.keystone:
            self.keystone = client.Client(username=settings.KEYSTONE_ADMIN_USER,
                                      password=settings.KEYSTONE_ADMIN_PASSWORD,
                                      tenant_name=settings.KEYSTONE_TENANT,
                                      auth_url=settings.KEYSTONE_AUTH_URL)
        self.stacksync_tenant = self.get_keystone_tenant()
        super(StacksyncUser, self).__init__(*args, **kwargs)

    def create_keystone_user(self, keystone_password):
        keystone_username = settings.KEYSTONE_TENANT + '_' + prefix() + '_' + self.name
        keystone_user = self.keystone.users.create(name=keystone_username,
                                                   password=keystone_password,
                                                   tenant_id=self.stacksync_tenant.id)

        self.swift_account = 'AUTH_' + self.stacksync_tenant.id
        self.swift_user = keystone_username
        return keystone_username

    def save(self, *args, **kwargs):

        keystone_password = 'testpass'
        keystone_username = self.create_keystone_user(keystone_password)

        super(StacksyncUser, self).save(*args, **kwargs)

        workspace = StacksyncWorkspace.objects.create_workspace(self.name, self.swift_account)
        membership = StacksyncMembership.objects.create(user=self, workspace=workspace, name='default')
        create_container(self.keystone.get_token('id'), keystone_username, workspace.swift_url, workspace.swift_container)

    def delete(self, using=None):
        keystone_user = self.get_keystone_user()
        if keystone_user:
            keystone_user.delete()
        # self.stacksyncworkspace_user.clear()
        super(StacksyncUser, self).delete()

    def __unicode__(self):
        return self.email

    def get_keystone_user(self):
        keystone_users = self.keystone.users.list()
        users = [user for user in keystone_users if user.name == self.swift_user]
        return users[0]

    def get_workspaces(self):
        pass


class StacksyncWorkspaceManager(models.Manager):
    def create_workspace(self, stacksync_username, swift_account):
        workspace = self.create()
        workspace.swift_container = settings.KEYSTONE_TENANT + '_' + prefix() + '_' + stacksync_username
        workspace.swift_url = settings.SWIFT_URL + '/' + swift_account
        workspace.is_shared = False

        return workspace


class StacksyncWorkspace(models.Model):
    id = models.CharField(max_length=37, primary_key=True, default=make_uuid(), editable=False)
    users = models.ManyToManyField(StacksyncUser, through='StacksyncMembership', related_name='stacksyncworkspace_users')
    # name = models.CharField(max_length=200)
    latest_revision = models.IntegerField(default=0)
    is_shared = models.BooleanField(default=False)
    is_encrypted = models.BooleanField(default=False)
    swift_container = models.CharField(max_length=200)
    swift_url = models.CharField(max_length=250)
    created_at = models.DateTimeField(auto_now_add=True)
    objects = StacksyncWorkspaceManager()

    class Meta:
         db_table = settings.WORKSPACE_TABLE

    def __unicode__(self):
        return self.id


class StacksyncMembership(models.Model):
    id = models.CharField(max_length=37, primary_key=True, default=make_uuid(), editable=False)
    user = models.ForeignKey(StacksyncUser, related_name='stacksyncmembership_user')
    workspace = models.ForeignKey(StacksyncWorkspace)
    is_owner = models.BooleanField(default=False)
    name = models.CharField(max_length=200)
    parent_item_id = models.IntegerField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now_add=True)

    class Meta:
         db_table = settings.MEMBERSHIP_TABLE