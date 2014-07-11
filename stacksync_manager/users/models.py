from django.db import models
from django_pg.models import UUIDField
from django_pg.models.fields.uuid import UUIDAdapter
from keystoneclient.v2_0 import client
from swiftclient import client as swift
from django.conf import settings
import uuid


def prefix():
    return make_uuid().split('-')[0]


def make_uuid():
    return str(uuid.uuid4())


def create_container(token_id=None, keystone_username=None, swift_url=None, swift_container=None):
    """creates the container in swift with read and write permissions"""
    user_and_tenant = settings.KEYSTONE_TENANT + ':' + keystone_username
    headers = {'x-container-read': user_and_tenant, 'x-container-write': user_and_tenant}
    swift.put_container(swift_url, token_id, swift_container,
                        headers=headers)

def set_container_quota(token_id=None, swift_url=None, swift_container=None, quota_limit=0):
    """sets the physical quota limit on the container"""
    headers = {'X-Container-Meta-Quota-Bytes': quota_limit}
    swift.post_container(swift_url, token_id, swift_container,
                        headers=headers)


class StacksyncUser(models.Model):
    id = UUIDField(auto_add=True, primary_key=True)
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    swift_user = models.CharField(max_length=100, unique=True)
    swift_account = models.CharField(max_length=100)
    quota_limit = models.IntegerField(default=0)
    quota_used = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    # objects = StacksyncUserManager()

    class Meta:
        db_table = settings.USER_TABLE

    def __init__(self, *args, **kwargs):

        keystone = client.Client(username=settings.KEYSTONE_ADMIN_USER,
                                      password=settings.KEYSTONE_ADMIN_PASSWORD,
                                      tenant_name=settings.KEYSTONE_TENANT,
                                      auth_url=settings.KEYSTONE_AUTH_URL)

        self.keystone = kwargs.pop('keystone', keystone)
        self.stacksync_tenant = self.get_keystone_tenant()

        super(StacksyncUser, self).__init__(*args, **kwargs)
        self.swift_account = 'AUTH_' + self.stacksync_tenant.id

    def create_keystone_user(self, keystone_password):
        keystone_username = settings.KEYSTONE_TENANT + '_' + prefix() + '_' + self.name
        keystone_user = self.keystone.users.create(name=keystone_username,
                                                   password=keystone_password,
                                                   tenant_id=self.stacksync_tenant.id)

        return keystone_username

    def save(self, *args, **kwargs):

        keystone_password = 'testpass'
        keystone_username = self.create_keystone_user(keystone_password)
        self.swift_user = keystone_username

        super(StacksyncUser, self).save(*args, **kwargs)

        workspace = StacksyncWorkspace.objects.create_workspace(self)
        membership = StacksyncMembership.objects.create(user=self, workspace=workspace, name='default')
        create_container(self.keystone.get_token('id'), keystone_username, workspace.swift_url,
                         workspace.swift_container)
        set_container_quota(self.keystone.get_token('id'), workspace.swift_url, workspace.swift_container, self.quota_limit)

    def delete(self, using=None):
        keystone_user = self.get_keystone_user()
        if keystone_user:
            keystone_user.delete()
        super(StacksyncUser, self).delete()

    def __unicode__(self):
        return self.email

    def get_keystone_user(self):
        keystone_users = self.keystone.users.list()
        users = [user for user in keystone_users if user.name == self.swift_user]
        if users:
            return users[0]
        else:
            return None

    def get_keystone_tenant(self):
        tenants = self.keystone.tenants.list()
        return [x for x in tenants if x.name == settings.KEYSTONE_TENANT][0]

    def get_workspaces(self):
        return list(StacksyncWorkspace.objects.filter(owner=self))


class StacksyncWorkspaceManager(models.Manager):
    def create_workspace(self, stacksync_user):

        swift_url = settings.SWIFT_URL + '/' + stacksync_user.swift_account
        swift_container = settings.KEYSTONE_TENANT + '_' + prefix() + '_' + stacksync_user.name

        workspace = self.create(owner=stacksync_user,
                                swift_container=swift_container,
                                swift_url=swift_url,
                                is_shared=False)

        return workspace


class StacksyncWorkspace(models.Model):
    id = UUIDField(verbose_name='UUID', auto_add=True, primary_key=True)
    users = models.ManyToManyField(StacksyncUser, through='StacksyncMembership',
                                   related_name='stacksyncworkspace_users')
    latest_revision = models.IntegerField(default=0)
    owner = models.ForeignKey(StacksyncUser)
    is_shared = models.BooleanField(default=False)
    is_encrypted = models.BooleanField(default=False)
    swift_container = models.CharField(max_length=45)
    swift_url = models.CharField(max_length=250)
    created_at = models.DateTimeField(auto_now_add=True)
    objects = StacksyncWorkspaceManager()

    class Meta:
        db_table = settings.WORKSPACE_TABLE

    def __unicode__(self):
        return UUIDAdapter(self.id).getquoted()

    def get_physical_quota(self):
        """
        Gets quota limit of container in bytes

        :return int:
        """
        keystone = client.Client(username=settings.KEYSTONE_ADMIN_USER,
                              password=settings.KEYSTONE_ADMIN_PASSWORD,
                              tenant_name=settings.KEYSTONE_TENANT,
                              auth_url=settings.KEYSTONE_AUTH_URL)

        container_metadata = swift.head_container(self.swift_url, keystone.get_token('id'), self.swift_container)

        return int(container_metadata.get('x-container-meta-quota-bytes', 0))



class StacksyncMembership(models.Model):
    id = UUIDField(auto_add=True, primary_key=True)
    user = models.ForeignKey(StacksyncUser, related_name='stacksyncmembership_user')
    workspace = models.ForeignKey(StacksyncWorkspace)
    name = models.CharField(max_length=200, db_column="workspace_name")
    parent_item_id = models.IntegerField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = settings.MEMBERSHIP_TABLE
        unique_together = (("user", "workspace"),)

class Container():
    def __init__(self):
        self.quota_limit = 0
