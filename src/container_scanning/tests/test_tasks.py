from unittest.mock import patch

from container_scanning.models import Analysis, Vendor
from container_scanning.tasks import scan_image, scan_image_vendor
from django.test.testcases import TestCase


class TasksTest(TestCase):
    @patch('container_scanning.tasks.scan_image_vendors')
    def test_scan_image_error(self, scan_image_vendors):
        """Ensure the result/status will return failed when has some error in
        scan."""

        # values returned from def scan_image_vendors
        scan_image_vendors.return_value = [
            {'error': 'error_a'},
            {'error': None}
        ]

        # create analysis
        analysis = Analysis.objects.create(image='registry.com/image:tag')

        # start scan
        scan_image(analysis_id=analysis.id)
        analysis_finished = Analysis.objects.get(id=analysis.id)

        # tests
        scan_image_vendors.assert_called_with(analysis)
        self.assertEqual(analysis_finished.result, 'failed')
        self.assertEqual(analysis_finished.status, 'failed')

    @patch('container_scanning.tasks.scan_image_vendors')
    def test_scan_exception(self, scan_image_vendors):
        """Ensure the result/status will return failed if case of some
        exception."""

        # exception returned from def scan_image_vendors
        scan_image_vendors.side_effect = Exception('generic error')

        # create analysis
        analysis = Analysis.objects.create(image='registry.com/image:tag')

        # start scan
        scan_image(analysis_id=analysis.id)
        analysis_finished = Analysis.objects.get(id=analysis.id)

        # tests
        scan_image_vendors.assert_called_with(analysis)
        self.assertEqual(analysis_finished.result, 'failed')
        self.assertEqual(analysis_finished.status, 'failed')

    @patch('container_scanning.tasks.scan_image_vendors')
    def test_scan_failed_with_vulns(self, scan_image_vendors):
        """Ensure the result will return failed if case of analysis with
        vulnerabilities."""

        # create analysis
        analysis = Analysis.objects.create(image='registry.com/image:tag')

        # mock vulnerabilities
        analysis.vulnerabilities = {
            'vendor': {'high_vulns': [
                {'name': 'CVE1'}
            ]}
        }
        analysis.save()

        # start scan
        scan_image(analysis_id=analysis.id)
        analysis_finished = Analysis.objects.get(id=analysis.id)

        # tests
        scan_image_vendors.assert_called_with(analysis)
        self.assertEqual(analysis_finished.result, 'failed')
        self.assertEqual(analysis_finished.status, 'finished')

    @patch('container_scanning.tasks.scan_image_vendors')
    def test_scan_success_without_vulns(self, scan_image_vendors):
        """Ensure the result will return passed if case of analysis with
        vulnerabilities."""

        # create analysis
        analysis = Analysis.objects.create(image='registry.com/image:tag')

        # start scan
        scan_image(analysis_id=analysis.id)
        analysis_finished = Analysis.objects.get(id=analysis.id)

        # tests
        scan_image_vendors.assert_called_with(analysis)
        self.assertEqual(analysis_finished.result, 'passed')
        self.assertEqual(analysis_finished.status, 'finished')

    @patch('container_scanning.tasks.initialize')
    def test_scan_image_vendor_failed(self, initialize):
        """Ensure we can create a scan by vendor."""

        # create analysis
        analysis = Analysis.objects.create(
            image='registry.com/image:tag'
        )

        initialize = initialize.return_value
        vendor = Vendor(
            **{
                'name': 'clair',
                'credentials': {'user': 'user', 'pass': 'password'},
            }
        )

        # mocking vendor functions
        initialize.add_image.return_value = 'image_id123'
        initialize.get_vuln.return_value = {'key': 'value'}
        initialize.get_resume.return_value = {
            'high_vulns': [{'vuln': 'CVE1'}]
        }

        # start scan
        scan_image_vendor(analysis, vendor)

        # tests args passed
        initialize.add_image.assert_called_with(
            config={'user': 'user', 'pass': 'password'},
            tag='registry.com/image:tag'
        )
        initialize.get_vuln.assert_called_with(
            config={'user': 'user', 'pass': 'password'}, image_id='image_id123'
        )
        initialize.get_resume.assert_called_with(
            results={'key': 'value'}, whitelist=[])

        # tests values updated in analysis
        self.assertDictEqual(
            analysis.vulnerabilities,
            {'clair': {'high_vulns': [{'vuln': 'CVE1'}]}}
        )
        self.assertDictEqual(
            analysis.vendors,
            {'clair': {'key': 'value'}}
        )

    @patch('container_scanning.tasks.initialize')
    def test_scan_image_vendor_success(self, initialize):
        """Ensure we can create a scan with whitelist by vendor."""

        # create analysis
        analysis = Analysis.objects.create(
            image='registry.com/image:tag',
            whitelist={'clair': ['CVE1']}
        )

        initialize = initialize.return_value
        vendor = Vendor(
            **{
                'name': 'clair',
                'credentials': {'user': 'user', 'pass': 'password'},
            }
        )

        # mocking vendor functions
        initialize.add_image.return_value = 'image_id123'
        initialize.get_vuln.return_value = {'key': 'value'}
        initialize.get_resume.return_value = {
            'high_vulns': [{'vuln': 'CVE1'}]
        }

        # start scan
        scan_image_vendor(analysis, vendor)

        # tests args passed
        initialize.add_image.assert_called_with(
            config={'user': 'user', 'pass': 'password'},
            tag='registry.com/image:tag'
        )
        initialize.get_vuln.assert_called_with(
            config={'user': 'user', 'pass': 'password'}, image_id='image_id123'
        )
        initialize.get_resume.assert_called_with(
            results={'key': 'value'}, whitelist=['CVE1'])

        # tests values updated in analysis
        self.assertDictEqual(
            analysis.vulnerabilities,
            {'clair': {'high_vulns': [{'vuln': 'CVE1'}]}}
        )
        self.assertDictEqual(
            analysis.vendors,
            {'clair': {'key': 'value'}}
        )
