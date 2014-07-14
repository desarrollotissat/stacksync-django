from django.test import TestCase

from mock import MagicMock, patch
from swiftclient import client as swift
from users.models import StacksyncUser, StacksyncWorkspace, OpenstackClient

class StacksyncTest(TestCase):

    @patch('users.models.StacksyncWorkspace')
    # @patch('users.models.OpenstackClient')
    def test_mocked_no_openstack(self, mock):
        # swift.put_container.return_value = None
        testuser = StacksyncUser(name="AAA", email="testuser@testuser.com")
        testuser.save()


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