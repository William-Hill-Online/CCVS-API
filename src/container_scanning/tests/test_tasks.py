from unittest.mock import patch

from container_scanning.models import Analysis, Vendor
from container_scanning.tasks import scan_image, scan_image_vendor
from django.test.testcases import TestCase


class TasksTest(TestCase):

    @patch('container_scanning.tasks.scan_image_vendor')
    def test_scan_exception(self, scan_image_vendor):
        """Ensure the result/status will return failed if case of some
        exception."""

        # create analysis and vendor
        analysis, _ = self.create_analysis_vendor()

        # exception returned from def scan_image_vendor
        scan_image_vendor.side_effect = Exception('generic error')

        # start scan
        scan_image(analysis_id=analysis.id)

        # tests
        analysis = Analysis.objects.get(id=analysis.id)
        self.assertEqual(analysis.result, 'failed')
        self.assertListEqual(analysis.errors, ['generic error'])
        self.assertEqual(analysis.status, 'finished')

    @patch('container_scanning.tasks.scan_image_vendor')
    def test_scan_failed_with_vulns(self, scan_image_vendor):
        """Ensure the result will return failed if case of analysis with
        vulnerabilities."""

        # create analysis and vendor
        analysis, vendor = self.create_analysis_vendor()

        scan_image_vendor.return_value = ({'high_vulns': [
            {'name': 'CVE1'}
        ]}, 'some_output')

        # start scan
        scan_image(analysis_id=analysis.id)

        # tests
        analysis = Analysis.objects.get(id=analysis.id)
        scan_image_vendor.assert_called_with(analysis, vendor)
        self.assertDictEqual(
            analysis.ccvs_results,
            {'clair': {'high_vulns': [{'name': 'CVE1'}]}}
        )
        self.assertEqual(analysis.vendors, {'clair': 'some_output'})
        self.assertEqual(analysis.result, 'failed')
        self.assertEqual(analysis.status, 'finished')

    @patch('container_scanning.tasks.scan_image_vendor')
    def test_scan_success_without_vulns(self, scan_image_vendor):
        """Ensure the result will return passed if case of analysis with
        vulnerabilities."""

        # create analysis and vendor
        analysis, vendor = self.create_analysis_vendor()

        scan_image_vendor.return_value = ({}, 'output')

        # start scan
        scan_image(analysis_id=analysis.id)

        # tests
        analysis = Analysis.objects.get(id=analysis.id)
        scan_image_vendor.assert_called_with(analysis, vendor)
        self.assertEqual(analysis.ccvs_results, {'clair': {}})
        self.assertEqual(analysis.vendors, {'clair': 'output'})
        self.assertEqual(analysis.result, 'passed')
        self.assertEqual(analysis.status, 'finished')

    @patch('container_scanning.tasks.initialize')
    def test_vendor_functions(self, initialize):
        """Ensure we can create a scan by vendor."""

        initialize = initialize.return_value
        # mocking vendor functions
        initialize.add_image.return_value = 'image_id123'
        initialize.get_vuln.return_value = {'key': 'value'}

        # create analysis and vendor
        analysis, vendor = self.create_analysis_vendor()

        # start scan
        scan_image_vendor(analysis, vendor)

        # tests args passed
        initialize.add_image.assert_called_with(
            config={'user': 'user', 'pass': 'password'},
            tag='registry.com/image:tag'
        )
        initialize.get_vuln.assert_called_with(
            config={'user': 'user', 'pass': 'password'},
            image_id='image_id123'
        )
        initialize.parse_results.assert_called_with(
            results={'key': 'value'},
            whitelist=['CVE1']
        )

    def create_analysis_vendor(self):

        # create analysis
        analysis = Analysis.objects.create(
            image='registry.com/image:tag',
            whitelist={'clair': ['CVE1']}
        )
        vendor = Vendor.objects.create(
            name='clair',
            credentials={'user': 'user', 'pass': 'password'}
        )

        return analysis, vendor
