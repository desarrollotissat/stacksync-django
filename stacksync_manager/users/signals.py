from django.conf import settings
from users.models import StacksyncUser, StacksyncWorkspace, prefix
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

@receiver(pre_save, sender=StacksyncUser)
def create_openstack_user_for_stacksync_user(sender, instance, *args, **kwargs):
    if not instance.id:
        keystone_password = 'testpass'
        keystone_username = settings.KEYSTONE_TENANT + '_' + prefix() + '_' + instance.name

        instance.swift_user = keystone_username
        instance.keystone.users.create(name=keystone_username,
                                       password=keystone_password,
                                       tenant_id=instance.stacksync_tenant.id)

@receiver(post_save, sender=StacksyncUser)
def create_default_workspace_for_user(sender, instance, created, **kwargs):
    if created:
        StacksyncWorkspace.objects.create_workspace(instance)