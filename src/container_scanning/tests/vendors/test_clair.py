from unittest.mock import MagicMock, patch

from container_scanning import exceptions
from container_scanning.serializers import vendors
from container_scanning.vendors.clair import facade
from django.test.testcases import TestCase
from rest_framework import status


class ClairTest(TestCase):
    def setUp(self):
        """setup variables for tests usage."""

        self.config = {'pass': 'password2', 'user': 'user2'}
        self.tag = 'ImageExample1'

        # Serialized vendor configured for clair
        self.vendor = self.create_vendor_deps('clair')

    def create_vendor_deps(self, name):
        vendor = vendors.VendorSerializer(
            data={'name': name, 'credentials': {'user': 'user2', 'pass': 'password2'}}
        )
        vendor.is_valid()
        vendor.save()

        return vendor.instance

    @patch('container_scanning.vendors.clair.facade.PaClair')
    def test_add_image(self, mock_paclair):
        """Ensures that we test add_image function without exceptions."""
        paclair_value = mock_paclair.return_value
        paclair_value.analyse.return_value = '{"ancestry": {"name":"test"}}'

        self.assertEqual(facade.add_image(self.config, self.tag), 'test')

        # Checking if the values of the paclair push and analise mock are
        # correct
        paclair_value.push.assert_called_with('Docker', self.tag)
        paclair_value.analyse.assert_called_with('Docker', self.tag)

    @patch('container_scanning.vendors.clair.facade.PaClair')
    def test_fail_add_image(self, mock_paclair):
        """Ensures that we test add_image function with error exceptions."""
        # Creating and error exception: TypeError("int object is not callable")
        mock_paclair.return_value.analyse = status.HTTP_400_BAD_REQUEST

        # Checking if was raised any exception
        with self.assertRaises(exceptions.VendorException):
            facade.add_image(self.config, self.tag)

    @patch('container_scanning.vendors.clair.facade.PaClair')
    def test_get_vuln(self, mock_paclair):
        """Ensures that we test get_vuln function without error exceptions."""

        # Mocking docker to add to paclair plugins and adding the return value
        mock_docker = MagicMock()
        mock_docker.clair.get_ancestry.return_value = {'name': 'Image123'}

        # Moking paclair plugins with docker mock
        mock_paclair.return_value._plugins = {'Docker': mock_docker}

        self.assertEqual(
            facade.get_vuln(self.config, 'sha256:test'), {'name': 'Image123'}
        )

        # Checking if the values of the paclair push and analise mock are
        # correct
        mock_paclair.return_value._plugins[
            'Docker'
        ].clair.get_ancestry.assert_called_with('sha256:test')

    @patch('container_scanning.vendors.clair.facade.PaClair')
    def test_fail_get_vuln(self, mock_paclair):
        """Ensures that we test get_vuln function with error exceptions."""
        # Creating and error exception: TypeError("int object is not callable")
        mock_paclair.return_value._plugins = status.HTTP_400_BAD_REQUEST

        # Checking if was raised any exception
        with self.assertRaises(exceptions.VendorException):
            facade.get_vuln(self.config, 'image_test')
