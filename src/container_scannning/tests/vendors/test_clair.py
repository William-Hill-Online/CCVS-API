from unittest.mock import MagicMock
from unittest.mock import patch

from container_scannning import exceptions
from container_scannning.serializers import images
from container_scannning.serializers import vendors
from container_scannning.vendors.clair import facade
from rest_framework import status
from rest_framework.test import APITestCase

permission = MagicMock(return_value=True)
patch_has_permission = patch(
    'container_scannning.views.images.JWTAPIPermission.has_permission',
    permission
)


class ClairTest(APITestCase):

    def setUp(self):
        """setup variables for tests usage."""

        self.config = {'pass': 'password2', 'user': 'user2'}
        self.tag = 'ImageExample1'

        # Serialized vendor configured for clair
        self.vendor = self.create_vendor_deps('clair')

        # Serialized image configured for clair
        self.image = self.create_image_deps()

        # image_vendor configured for clair
        self.image_vendor = images.ImageVendor.objects.create(
            vendor=self.vendor,
            image=self.image,
            vendor_image_internal_id='name123'
        )
        self.image_vendor.save()

    def create_image_deps(self):
        image = images.ImageSerializer(data={
            'name': 'ImageExample1'
        })
        image.is_valid()
        image.save()

        return image.instance

    def create_vendor_deps(self, name):
        vendor = vendors.VendorSerializer(data={
            'name': name,
            'credentials': {
                'user': 'user2',
                'pass': 'password2'
            }
        })
        vendor.is_valid()
        vendor.save()

        return vendor.instance

    @patch_has_permission
    @patch('container_scannning.vendors.clair.facade.PaClair')
    def test_add_image(self, mock_paclair):
        """Ensures that we test add_image function without exceptions."""
        paclair_value = mock_paclair.return_value
        paclair_value.analyse.return_value = '{"ancestry": {"name":"test"}}'

        self.assertEqual(facade.add_image(self.config, self.tag), 'test')

        # Checking if the values of the paclair push and analise mock are
        # correct
        paclair_value.push.call_args('Docker', self.tag)
        paclair_value.analyse.call_args('Docker', self.tag)

    @patch_has_permission
    @patch('container_scannning.vendors.clair.facade.PaClair')
    def test_fail_add_image(self, mock_paclair):
        """Ensures that we test add_image function with error exceptions."""
        # Creating and error exception: TypeError("int object is not callable")
        mock_paclair.return_value.analyse = status.HTTP_400_BAD_REQUEST

        # Checking if was raised any exception
        with self.assertRaises(exceptions.VendorException):
            facade.add_image(self.config, self.tag)

    @patch_has_permission
    @patch('container_scannning.vendors.clair.facade.PaClair')
    def test_get_vuln(self, mock_paclair):
        """Ensures that we test get_vuln function without error exceptions."""

        # Mocking docker to add to paclair plugins and adding the return value
        mock_docker = MagicMock()
        mock_docker.clair.get_ancestry.return_value = {'name': 'Image123'}

        # Moking paclair plugins with docker mock
        mock_paclair.return_value._plugins = {'Docker': mock_docker}

        self.assertEqual(facade.get_vuln(
            self.image_vendor), {'name': 'Image123'})

        # Checking if the values of the paclair push and analise mock are
        # correct
        mock_paclair.return_value._plugins['Docker'].clair\
            .get_ancestry.call_args('name123')

    @patch_has_permission
    @patch('container_scannning.vendors.clair.facade.PaClair')
    def test_fail_get_vuln(self, mock_paclair):
        """Ensures that we test get_vuln function with error exceptions."""
        # Creating and error exception: TypeError("int object is not callable")
        mock_paclair.return_value._plugins = status.HTTP_400_BAD_REQUEST

        # Checking if was raised any exception
        with self.assertRaises(exceptions.VendorException):
            facade.get_vuln(self.image_vendor)
