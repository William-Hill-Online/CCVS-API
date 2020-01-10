from container_scanning.models import Job
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class JobsTests(APITestCase):

    def test_create_job(self):
        """Ensure we can create a new job object."""

        url = reverse('container_scanning:jobs')
        data = {
            'type': 'scan_image',
            'data': {'image': 'image_test'}
        }
        response = self.client.post(url, data, format='json')

        # Testing if the post works
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(Job.objects.count(), 1)
        self.assertEqual(Job.objects.get().type, 'scan_image')
        self.assertEqual(Job.objects.get().status, 'pending')
        self.assertEqual(Job.objects.get().data, {'image': 'image_test'})
        self.assertEqual(Job.objects.get().result, None)


class JobTests(APITestCase):

    def test_get_vendor_pending(self):
        """Ensure we can get a job with status pending."""

        job = Job.objects.create(**{
            'type': 'scan_image',
            'status': 'pending',
            'data': {'key': 'value'}
        })
        url = reverse('container_scanning:job',
                      kwargs={'job_id': job.id})
        response = self.client.get(url, format='json')
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data['type'], 'scan_image')
        self.assertEqual(data['status'], 'pending')
        self.assertDictEqual(data['data'], {'key': 'value'})
        self.assertEqual(data['result'], None)

    def test_get_vendor_success(self):
        """Ensure we can get a job with status success."""

        job = Job.objects.create(**{
            'type': 'scan_image',
            'status': 'success',
            'data': {'key': 'value'},
            'result': {'key2': 'value2'}
        })
        url = reverse('container_scanning:job',
                      kwargs={'job_id': job.id})
        response = self.client.get(url, format='json')
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data['type'], 'scan_image')
        self.assertEqual(data['status'], 'success')
        self.assertDictEqual(data['data'], {'key': 'value'})
        self.assertEqual(data['result'], {'key2': 'value2'})
