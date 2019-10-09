from unittest.mock import MagicMock
from unittest.mock import patch

from container_scannning.serializers import images
from container_scannning.serializers import vendors
from container_scannning.vendors.anchore_engine import facade
from rest_framework.test import APITestCase

permission = MagicMock(return_value=True)
patch_has_permission = patch(
    'container_scannning.views.images.JWTAPIPermission.has_permission',
    permission
)


class AnchoreTest(APITestCase):

    def setUp(self):
        """setup variables for tests usage."""

        self.config = {'pass': 'password2', 'user': 'user2'}
        self.tag = 'ImageExample1'

        # Serialized vendor configured for anchore
        self.vendor = self.create_vendor_deps('anchore')

        # Serialized image configured for anchore
        self.image = self.create_image_deps()

        # Images image_vendor object configured for anchore
        self.image_vendor = images.ImageVendor.objects.create(
            vendor=self.vendor,
            image=self.image,
            vendor_image_internal_id='name123'
        )
        self.image_vendor.save()

        self.get_image_config = self.image_vendor.vendor.credentials
        self.image_id = self.image_vendor.vendor_image_internal_id

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
    @patch('container_scannning.vendors.anchore_engine.facade.apiexternal')
    def test_get_image(self, mock_anchore):
        """Ensures that we test get_image function without exceptions."""
        mock_anchore.get_image.return_value = {
            'success': True, 'payload': 'venderId'}

        self.assertEqual(facade.get_image(self.image_vendor), 'venderId')
        mock_anchore.get_image.call_args(
            self.get_image_config, image_id=self.image_id)

    @patch_has_permission
    @patch('container_scannning.vendors.anchore_engine.facade.apiexternal')
    def test_fail_get_image(self, mock_anchore):
        """Ensures that we test get_image function with exceptions."""
        mock_anchore.get_image.return_value = {
            'success': False, 'payload': 'venderId'}

        # Checking if was raised any exception
        with self.assertRaises(Exception):
            facade.get_image(self.image_vendor)

    @patch_has_permission
    @patch('container_scannning.vendors.anchore_engine.facade.apiexternal')
    def test_add_image(self, mock_anchore):
        """Ensures that we test add_image function without exceptions."""
        mock_anchore.add_image.return_value = {
            'success': True, 'payload': [{'imageDigest': 'venderId'}]}

        self.assertEqual(facade.add_image(self.config, self.tag), 'venderId')
        mock_anchore.add_image.call_args(self.config, tag=self.tag)

    @patch_has_permission
    @patch('container_scannning.vendors.anchore_engine.facade.apiexternal')
    def test_fail_add_image(self, mock_anchore):
        """Ensures that we test add_image function with exceptions."""
        mock_anchore.add_image.return_value = {
            'success': False, 'payload': [{'imageDigest': 'venderId'}]}

        # Checking if was raised any exception
        with self.assertRaises(Exception):
            facade.add_image(self.config, self.tag)

    @patch_has_permission
    @patch('container_scannning.vendors.anchore_engine.facade.apiexternal')
    def test_get_vuln(self, mock_anchore):
        """Ensures that we test get_vuln function without exceptions."""
        mock_anchore.query_image.return_value = {
            'success': True, 'payload': 'name123'}

        self.assertEqual(facade.get_vuln(self.image_vendor), 'name123')

        mock_anchore.query_image.call_args(
            self.vendor.credentials, imageDigest='name123',
            query_group='vuln', query_type='all', vendor_only=True)

    @patch_has_permission
    @patch('container_scannning.vendors.anchore_engine.facade.apiexternal')
    def test_fail_get_vuln(self, mock_anchore):
        """Ensures that we test get_vuln function with exceptions."""
        mock_anchore.query_image.return_value = {
            'success': False, 'payload': 'name123'}

        # Checking if was raised any exception
        with self.assertRaises(Exception):
            facade.get_vuln(self.image_vendor)
