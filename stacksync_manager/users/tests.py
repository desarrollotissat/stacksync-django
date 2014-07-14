from django.test import TestCase

from mock import MagicMock, patch
from swiftclient import client as swift
from users.models import StacksyncUser, StacksyncWorkspace, OpenstackClient

class StacksyncTest(TestCase):

    # @patch('users.models.StacksyncWorkspace')
    # @patch('users.models.StacksyncWorkspaceManager')
    @patch.object('users.models.StacksyncWorkspaceManager', 'initialize_container')
    def test_create_user(self):
        """
        This test doesnt actually get to create any container
        :param mock:
        :return:
        """
        testuser = StacksyncUser(name="AAA", email="testuser@testuser.com")
        testuser.openstack_api = MagicMock()
        testuser.openstack_api.keystone = self.get_mock_keystone()
        testuser.openstack_api.create_keystone_user.return_value = "swift_user_mocked"
        # testuser.save.StacksyncWorkspace.initialize_container = MagicMock()

        testuser.save()
        self.testuser = testuser


        self.assertIsNotNone(testuser.id)
        self.assertNotEquals(testuser.swift_account, u"")
        self.assertIsNotNone(testuser.pk)


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

    def get_mock_keystone_user(self):
        keystone_user = MagicMock()
        keystone_user.name = "swift_user_mocked"

        return keystone_user



    # def test_delete_user(self):
    #     testuser = StacksyncUser(name="AAA", email="testuser@testuser.com")
    #     testuser.save()
    #     self.assertIsNotNone(testuser.id)
    #
    #     testuser.delete()
    #     self.assertIsNone(testuser.id)



class FunctionalStacksyncUserTests(TestCase):

    def __init__(self, *args, **kwargs):
        self.user_name = "testuser"
        # self.keystone = self.get_mock_keystone()
        super(FunctionalStacksyncUserTests, self).__init__(*args, **kwargs)

    def setUp(self):
        self.testuser = StacksyncUser(name=self.user_name, email="testuser@testuser.com")
        self.testuser.save()

    def tearDown(self):
        self.testuser.delete()

    def test_add_two_stacksync_users(self):
        testuser1 = StacksyncUser(name=self.user_name, email="testuser@testuser.com")
        testuser1.save()
        self.assertIsNotNone(testuser1.id)

        testuser2 = StacksyncUser(name=self.user_name, email="testuser@testuser.com")
        testuser2.save()
        self.assertIsNotNone(testuser2.id)

        self.assertNotEquals(testuser1.id, testuser2.id)

        #cleanup
        testuser1.delete()
        testuser2.delete()

    def test_get_user_logic_quota(self):
        testuser = StacksyncUser(name=self.user_name, email="testuser@testuser.com", quota_limit=100)
        testuser.save()

        self.assertEquals(100, testuser.quota_limit)

        testuser.delete()

    def test_user_has_workspaces(self):
        workspaces = self.testuser.get_workspaces()
        number_of_workspaces_for_user = len(workspaces)

        self.assertNotEquals(number_of_workspaces_for_user, 0)

    def test_user_container_exists(self):
        workspaces = self.testuser.get_workspaces()
        metadata = None
        for workspace in workspaces:
            metadata = workspace.get_container_metadata()
        self.assertIsNotNone(metadata)

    def test_get_physical_quota(self):
        workspaces = self.testuser.get_workspaces()
        workspace = workspaces[0]
        self.assertEquals(0, workspace.get_physical_quota())