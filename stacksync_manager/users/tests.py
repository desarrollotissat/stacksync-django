from django.test import TestCase
from keystoneclient.v2_0.tenants import Tenant
from mock import MagicMock, Mock
from stacksync_manager import settings

from keystoneclient.v2_0 import client


#since i have to mock swift and it is being used inside stacksyncUser, I have to override that import
from swiftclient import client as swift

# swift.put_container = Mock()
from users.models import StacksyncUser, StacksyncWorkspace


class StacksyncUserTests(TestCase):
    """
    This class doesnt actually send requests to keystone or swift, they're mocked.
    This class intends to test only stacksync-functionality.
    """

    def __init__(self, *args, **kwargs):
        self.user_name = "testuser"
        self.keystone = self.get_mock_keystone()
        super(StacksyncUserTests, self).__init__(*args, **kwargs)

    def setUp(self):
        self.testuser = StacksyncUser(name=self.user_name, email="testuser@testuser.com", keystone=self.keystone)
        self.testuser.save()

    def get_mock_stacksync_tenant(self):
        tenant = MagicMock()
        tenant.name = 'stacksync'
        tenant.id = 'id_of_Tenant'
        return tenant

    def get_mock_keystone(self):
        keystone = MagicMock()
        tenant = self.get_mock_stacksync_tenant()
        keystone.tenants.list.return_value = [tenant]
        return keystone

    def test_create_stacksync_user(self):
        testuser = StacksyncUser(name=self.user_name, email="testuser@testuser.com", keystone=self.keystone)
        testuser.save()

        self.assertEqual(testuser.name, self.user_name)
        self.assertNotEquals(testuser.swift_account, u"")
        self.assertIsNotNone(testuser.pk)
        self.assertIsNotNone(testuser.id)

    def get_mock_keystone_user(self):
        keystone_user = MagicMock()
        keystone_user.name = self.testuser.swift_user

        return keystone_user

    def test_delete_stacksync_user(self):
        self.testuser = StacksyncUser(name=self.user_name, email="testuser@testuser.com", keystone=self.keystone)
        self.testuser.save()

        keystone_user = self.get_mock_keystone_user()
        self.testuser.keystone.users.list.return_value = [keystone_user]
        self.testuser.delete()

        self.assertIsNone(self.testuser.id)
        self.assertIsNone(self.testuser.pk)

    def test_add_two_stacksync_users(self):
        testuser1 = StacksyncUser(name=self.user_name, email="testuser@testuser.com", keystone=self.keystone)
        testuser1.save()
        self.assertIsNotNone(testuser1.id)

        testuser2 = StacksyncUser(name=self.user_name, email="testuser@testuser.com", keystone=self.keystone)
        testuser2.save()
        self.assertIsNotNone(testuser2.id)

        self.assertNotEquals(testuser1.id, testuser2.id)

    def test_get_user_logic_quota(self):
        testuser1 = StacksyncUser(name=self.user_name, email="testuser@testuser.com", keystone=self.keystone, quota_limit=100)
        testuser1.save()
        self.assertEquals(100, testuser1.quota_limit)

    def test_user_has_workspaces(self):
        workspaces = self.testuser.get_workspaces()
        number_of_workspaces_for_user = len(workspaces)
        self.assertNotEquals(number_of_workspaces_for_user, 0)


class ContainerTests(TestCase):
    def setUp(self):
        self.testuser1 = StacksyncUser(name="testuser", email="testuser@testuser.com", quota_limit=100)
        self.testuser1.save()

    def tearDown(self):
        self.testuser1.delete()

    def test_get_physical_quota(self):
        workspaces = self.testuser1.get_workspaces()
        workspace = workspaces[0]
        self.assertEquals(100, workspace.get_physical_quota())

    def test_set_physical_quota(self):
        pass










