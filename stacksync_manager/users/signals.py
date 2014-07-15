from users.models import StacksyncUser, StacksyncWorkspace
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver





@receiver(pre_save, sender=StacksyncUser)
def create_openstack_user_for_stacksync_user(sender, instance, *args, **kwargs):
    if not instance.id:
        keystone_password = 'testpass'
        keystone_username = instance.openstack_api.create_keystone_user(instance.name,
                                                                        instance.stacksync_tenant,
                                                                        keystone_password)
        instance.swift_user = keystone_username

@receiver(post_save, sender=StacksyncUser)
def create_default_workspace_for_user(sender, instance, created, **kwargs):
    if created:
        StacksyncWorkspace.objects.create_workspace(instance)