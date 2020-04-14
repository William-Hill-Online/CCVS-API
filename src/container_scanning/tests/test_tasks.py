from unittest.mock import patch

from container_scanning.models import Analysis, Vendor
from container_scanning.tasks import scan_image, scan_image_vendor, scan_image_vendors
from django.test.testcases import TestCase


class TasksTest(TestCase):
    @patch('container_scanning.tasks.scan_image_vendors')
    def test_scan_image_success(self, scan_image_vendors):
        """Ensure we can create a scan."""
        scan_image_vendors.return_value = [
            (
                'anchore',
                {'result': 'anchore_result'},
                {'low': [{'key': 'value'}]}
            ), (
                'clair',
                {'result': 'clair_result'},
                {}
            ),
        ]
        analysis = Analysis.objects.create(image='image_tag')

        scan_image(analysis_id=analysis.id, image='image_tag')

        analysis_finished = Analysis.objects.get(id=analysis.id)
        scan_image_vendors.assert_called_with('image_tag')
        self.assertDictEqual(
            analysis_finished.vendors,
            {
                'clair': {'result': 'clair_result'},
                'anchore': {'result': 'anchore_result'},
            },
        )
        self.assertDictEqual(
            analysis_finished.vulnerabilities,
            {
                'clair': {},
                'anchore': {'low': [{'key': 'value'}]},
            },
        )
        self.assertEqual(analysis_finished.result, 'failed')

    @patch('container_scanning.tasks.initialize')
    def test_scan_image_vendor_success(self, initialize):
        """Ensure we can create a scan by vendor."""
        initialize = initialize.return_value
        vendor = Vendor(
            **{
                'name': 'VendorExample',
                'credentials': {'user': 'user', 'pass': 'password'},
            }
        )

        initialize.add_image.return_value = 'image_id'
        initialize.get_vuln.return_value = {'key': 'value'}
        initialize.get_resume.return_value = {'key2': 'value2'}

        result = scan_image_vendor('image_tag', vendor)

        initialize.add_image.assert_called_with(
            {'user': 'user', 'pass': 'password'},
            tag='image_tag'
        )
        initialize.get_vuln.assert_called_with({
            'user': 'user', 'pass': 'password'
        }, image_id='image_id'
        )
        initialize.get_resume.assert_called_with({'key': 'value'})

        self.assertTupleEqual(result, ({'key': 'value'}, {'key2': 'value2'}))

    @patch('container_scanning.tasks.scan_image_vendor')
    def test_scan_image_vendors_success(self, scan_image_vendor):
        """Ensure we can create a scan in all vendors."""

        vendor1 = Vendor.objects.create(
            **{
                'name': 'VendorExample1',
                'credentials': {'user': 'user1', 'pass': 'password1'},
            }
        )

        vendor2 = Vendor.objects.create(
            **{
                'name': 'VendorExample2',
                'credentials': {'user': 'user2', 'pass': 'password2'},
            }
        )

        scan_image_vendor.side_effect = [
            ({'key': 'value'}, {'key2': 'value2'}),
            ({'key3': 'value3'}, {'key4': 'value4'})
        ]

        results = scan_image_vendors('image_tag')

        result = next(results)
        scan_image_vendor.assert_called_with('image_tag', vendor1)
        self.assertEqual(result[0], 'VendorExample1')
        self.assertDictEqual(result[1], {'key': 'value'})
        self.assertDictEqual(result[2], {'key2': 'value2'})

        result = next(results)
        scan_image_vendor.assert_called_with('image_tag', vendor2)
        self.assertEqual(result[0], 'VendorExample2')
        self.assertDictEqual(result[1], {'key3': 'value3'})
        self.assertDictEqual(result[2], {'key4': 'value4'})
