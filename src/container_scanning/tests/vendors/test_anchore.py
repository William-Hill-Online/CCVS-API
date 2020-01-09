from unittest.mock import patch

from container_scanning.serializers import vendors
from container_scanning.vendors.anchore_engine import facade
from rest_framework.test import APITestCase


class AnchoreTest(APITestCase):

    def setUp(self):
        """setup variables for tests usage."""

        self.config = {'pass': 'password2', 'user': 'user2'}
        self.tag = 'ImageExample1'

        # Serialized vendor configured for anchore
        self.vendor = self.create_vendor_deps('anchore')

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

    @patch('container_scanning.vendors.anchore_engine.facade.apiexternal')
    def test_add_image(self, mock_anchore):
        """Ensures that we test add_image function without exceptions."""
        mock_anchore.add_image.return_value = {
            'success': True, 'payload': [{'imageDigest': 'venderId'}]}

        self.assertEqual(facade.add_image(self.config, self.tag), 'venderId')
        mock_anchore.add_image.call_args(self.config, tag=self.tag)

    @patch('container_scanning.vendors.anchore_engine.facade.apiexternal')
    def test_fail_add_image(self, mock_anchore):
        """Ensures that we test add_image function with exceptions."""
        mock_anchore.add_image.return_value = {
            'success': False, 'payload': [{'imageDigest': 'venderId'}]}

        # Checking if was raised any exception
        with self.assertRaises(Exception):
            facade.add_image(self.config, self.tag)

    @patch('container_scanning.vendors.anchore_engine.facade.apiexternal')
    def test_get_vuln_success(self, mock_anchore):
        """Ensures that we test get_vuln function without exceptions."""

        result_vuln = {
            'success': True, 'httpcode': 200,
            'payload': {
                'imageDigest': 'sha256:test',
                'vulnerabilities': [],
                'vulnerability_type': 'all'
            }, 'error': {}}

        mock_anchore.query_image.return_value = result_vuln

        self.assertEqual(facade.get_vuln(
            self.config, 'sha256:test'), result_vuln['payload'])

        mock_anchore.query_image.call_args(
            self.config,  imageDigest='sha256:test', query_group='vuln',
            query_type='all', vendor_only=True
        )

    @patch('container_scanning.vendors.anchore_engine.facade.apiexternal')
    def test_fail_get_vuln(self, mock_anchore):
        """Ensures that we test get_vuln function with exceptions."""
        mock_anchore.query_image.return_value = {
            'success': False, 'payload': 'error'}

        # Checking if was raised any exception
        with self.assertRaises(Exception):
            facade.get_vuln(self.config, 'sha256:test')
