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
        self.assertEqual(Analysis.objects.get().vendors, None)
        self.assertEqual(Analysis.objects.get().vulnerabilities, None)


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
        self.assertEqual(data['vendors'], None)
        self.assertEqual(data['vulnerabilities'], None)

    def test_get_vendor_success(self):
        """Ensure we can get a analysis with status success."""

        analysis = Analysis.objects.create(
            **{
                'status': 'finished',
                'image': 'image_test',
                'result': 'passed',
                'vendors': {'key': 'value'},
                'vulnerabilities': {'key2': 'value2'},
            }
        )
        url = reverse('container_scanning:analysis-id',
                      kwargs={'analysis_id': analysis.id})
        response = self.client.get(url, format='json')
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data['status'], 'finished')
        self.assertEqual(data['result'], 'passed')
        self.assertDictEqual(data['vendors'], {'key': 'value'})
        self.assertDictEqual(data['vulnerabilities'], {'key2': 'value2'})
