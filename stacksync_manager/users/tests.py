from django.test import TestCase
from keystoneclient.v2_0.tenants import Tenant
from mock import MagicMock, Mock
from stacksync_manager import settings

from keystoneclient.v2_0 import client


#since i have to mock swift and it is being used inside stacksyncUser, I have to override that import
from swiftclient import client as swift

swift.put_container = Mock()
from users.models import StacksyncUser

class StacksyncUserTests(TestCase):
    def create_stacksync_tenant(self):
        tenant = MagicMock()
        tenant.name = 'stacksync'
        return tenant

    def setUp(self):
        self.user_name = "testuser"
        keystone = MagicMock()
        tenant = self.create_stacksync_tenant()
        keystone.tenants.list.return_value = [tenant]
        self.testuser = StacksyncUser.objects.create(name=self.user_name, email="testuser@testuser.com", keystone=keystone)

    def test_create_stacksync_user(self):
        # testuser = StacksyncUser.objects.get(name=self.user_name, email="testuser@testuser.com")
        self.assertEqual(self.testuser.name, self.user_name)

    def create_keystone_user(self):
        keystone_user = MagicMock()
        keystone_user.name = self.testuser.swift_user
        return keystone_user

    def test_delete_stacksync_user(self):
        keystone_user = self.create_keystone_user()
        self.testuser.keystone.users.list.return_value = [keystone_user]

        self.testuser.delete()
        self.assertIsNone(self.testuser.id)

