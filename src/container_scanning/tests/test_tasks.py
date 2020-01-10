from unittest.mock import patch

from container_scanning.models import Job
from container_scanning.models import Vendor
from container_scanning.tasks import scan_image
from container_scanning.tasks import scan_image_vendor
from container_scanning.tasks import scan_image_vendors
from django.test.testcases import TestCase


class TasksTest(TestCase):

    @patch('container_scanning.tasks.scan_image_vendors')
    def test_scan_image_success(self, scan_image_vendors):
        """Ensure we can create a scan."""
        scan_image_vendors.return_value = [
            ('anchore', {'result': 'anchore_result'}),
            ('clair', {'result': 'clair_result'}),
        ]
        job = Job.objects.create(
            data={'image': 'image_tag'},
            type='scan_image'
        )

        scan_image(job_id=job.id, data={'image': 'image_tag'})

        job_finished = Job.objects.get(id=job.id)
        scan_image_vendors.assert_called_with('image_tag')
        self.assertDictEqual(job_finished.result, {
            'clair': {'result': 'clair_result'},
            'anchore': {'result': 'anchore_result'}})

    @patch('container_scanning.tasks.initialize')
    def test_scan_image_vendor_success(self, initialize):
        """Ensure we can create a scan by vendor."""
        initialize = initialize.return_value
        vendor = Vendor(**{
            'name': 'VendorExample',
            'credentials': {
                'user': 'user',
                'pass': 'password'
            }
        })

        initialize.add_image.return_value = 'image_id'
        initialize.get_vuln.return_value = {'key': 'value'}

        result = scan_image_vendor('image_tag', vendor)

        initialize.add_image.assert_called_with({
            'user': 'user',
            'pass': 'password'}, tag='image_tag')
        initialize.get_vuln.assert_called_with({
            'user': 'user',
            'pass': 'password'}, image_id='image_id')

        self.assertDictEqual(result, {'key': 'value'})

    @patch('container_scanning.tasks.scan_image_vendor')
    def test_scan_image_vendors_success(self, scan_image_vendor):
        """Ensure we can create a scan in all vendors."""

        from nose.tools import set_trace
        set_trace()
        vendor1 = Vendor.objects.create(**{
            'name': 'VendorExample1',
            'credentials': {
                'user': 'user1',
                'pass': 'password1'
            }})

        vendor2 = Vendor.objects.create(**{
            'name': 'VendorExample2',
            'credentials': {
                'user': 'user2',
                'pass': 'password2'
            }})

        scan_image_vendor.side_effect = ['result1', 'result2']

        results = scan_image_vendors('image_tag')

        result = next(results)
        scan_image_vendor.assert_called_with('image_tag', vendor1)
        self.assertEqual(result[0], 'VendorExample1')
        self.assertEqual(result[1], 'result1')

        result = next(results)
        scan_image_vendor.assert_called_with('image_tag', vendor2)
        self.assertEqual(result[0], 'VendorExample2')
        self.assertEqual(result[1], 'result2')
