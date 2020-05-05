from container_scanning.models import Analysis
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class AnalysesTests(APITestCase):
    def test_create_analysis(self):
        """Ensure we can create a new analysis object."""

        url = reverse('container_scanning:analysis')
        data = {'image': 'image_test'}
        response = self.client.post(url, data, format='json')

        # Testing if the post works
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(Analysis.objects.count(), 1)
        self.assertEqual(Analysis.objects.get().status, 'pending')
        self.assertEqual(Analysis.objects.get().image, 'image_test')
        self.assertEqual(Analysis.objects.get().result, 'pending')
        self.assertEqual(Analysis.objects.get().vendors, {})
        self.assertEqual(Analysis.objects.get().ccvs_results, {})
        self.assertEqual(Analysis.objects.get().whitelist, {})

    def test_create_analysis_whitelist(self):
        """Ensure we can create a new analysis object with whitelist."""

        url = reverse('container_scanning:analysis')
        data = {
            'image': 'image_test',
            'whitelist': {'anchore': ['CVE1']}
        }
        response = self.client.post(url, data, format='json')

        # Testing if the post works
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(Analysis.objects.count(), 1)
        self.assertEqual(Analysis.objects.get().status, 'pending')
        self.assertEqual(Analysis.objects.get().image, 'image_test')
        self.assertEqual(Analysis.objects.get().result, 'pending')
        self.assertEqual(Analysis.objects.get().vendors, {})
        self.assertEqual(Analysis.objects.get().ccvs_results, {})
        self.assertEqual(Analysis.objects.get().whitelist,
                         {'anchore': ['CVE1']})


class AnalysisTests(APITestCase):
    def test_get_vendor_pending(self):
        """Ensure we can get a analysis with status pending."""

        analysis = Analysis.objects.create(**{'image': 'image_test'})
        url = reverse('container_scanning:analysis-id',
                      kwargs={'analysis_id': analysis.id})
        response = self.client.get(url, format='json')
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data['status'], 'pending')
        self.assertEqual(data['image'], 'image_test')
        self.assertEqual(data['result'], 'pending')
        self.assertEqual(data['vendors'], {})
        self.assertEqual(data['ccvs_results'], {})
        self.assertEqual(data['whitelist'], {})

    def test_get_vendor_pending_whitelist(self):
        """Ensure we can get an analysis pending with a whitelist."""

        analysis = Analysis.objects.create(**{'image': 'image_test'})
        url = reverse('container_scanning:analysis-id',
                      kwargs={'analysis_id': analysis.id})
        response = self.client.get(url, format='json')
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data['status'], 'pending')
        self.assertEqual(data['image'], 'image_test')
        self.assertEqual(data['result'], 'pending')
        self.assertEqual(data['vendors'], {})
        self.assertEqual(data['ccvs_results'], {})
        self.assertEqual(data['whitelist'], {})

    def test_get_vendor_success(self):
        """Ensure we can get a analysis with status success."""

        analysis = Analysis.objects.create(
            **{
                'status': 'finished',
                'image': 'image_test',
                'result': 'passed',
                'vendors': {'anchore': 'result'},
                'ccvs_results': {'anchore': 'vulnerabilities'},
                'whitelist': {'anchore': ['CVE1']},
            }
        )
        url = reverse('container_scanning:analysis-id',
                      kwargs={'analysis_id': analysis.id})
        response = self.client.get(url, format='json')
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data['status'], 'finished')
        self.assertEqual(data['result'], 'passed')
        self.assertDictEqual(data['vendors'], {'anchore': 'result'})
        self.assertDictEqual(data['ccvs_results'], {
                             'anchore': 'vulnerabilities'})
        self.assertDictEqual(data['whitelist'], {'anchore': ['CVE1']})
