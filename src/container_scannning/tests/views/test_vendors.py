from unittest.mock import MagicMock
from unittest.mock import patch

from container_scannning.models import Vendor
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class VendorsTests(APITestCase):
    permission = MagicMock(return_value=True)
    patch_has_permission = patch(
        'container_scannning.views.vendors.JWTAPIPermission.has_permission',
        permission
    )

    @patch_has_permission
    def test_create_vendor(self):
        """Ensure we can create a new vendor object."""

        url = reverse('container_scannning:vendor-list')
        data = {
            'name': 'VendorExample',
            'credentials': {
                'user': 'user1',
                'pass': 'password1',
            }
        }
        self.client.force_authenticate(None)
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Vendor.objects.count(), 1)
        self.assertEqual(Vendor.objects.get().name, 'VendorExample')
        self.assertEqual(Vendor.objects.get().credentials, {
            'user': 'user1',
            'pass': 'password1',
        })

    @patch_has_permission
    def test_list_one_vendor(self):
        """Ensure we can list one vendor objects."""

        url = reverse('container_scannning:vendor-list')
        Vendor.objects.create(**{
            'name': 'VendorExample2',
            'credentials': {
                'user': 'user2',
                'pass': 'password2',
            }
        })
        self.client.force_authenticate(None)
        response = self.client.get(url, format='json')
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['name'], 'VendorExample2')
        self.assertEqual(data[0]['credentials'], {
            'user': 'user2',
            'pass': 'password2',
        })

    @patch_has_permission
    def test_list_two_vendor(self):
        """Ensure we can list two vendor objects."""
        url = reverse('container_scannning:vendor-list')
        Vendor.objects.create(**{
            'name': 'VendorExample2',
            'credentials': {
                'user': 'user2',
                'pass': 'password2',
            }
        })
        Vendor.objects.create(**{
            'name': 'VendorExample3',
            'credentials': {
                'user': 'user3',
                'pass': 'password3',
            }
        })

        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + 'este.teste.teste')
        response = self.client.get(url, format='json')
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['name'], 'VendorExample2')
        self.assertEqual(data[0]['credentials'], {
            'user': 'user2',
            'pass': 'password2',
        })
        self.assertEqual(data[1]['name'], 'VendorExample3')
        self.assertEqual(data[1]['credentials'], {
            'user': 'user3',
            'pass': 'password3',
        })

    @patch_has_permission
    def test_search_vendor(self):
        """Ensure we can search one vendor object."""
        url = reverse('container_scannning:vendor-list')
        url += '?name=VendorExample3'
        Vendor.objects.create(**{
            'name': 'VendorExample2',
            'credentials': {
                'user': 'user2',
                'pass': 'password2',
            }
        })
        Vendor.objects.create(**{
            'name': 'VendorExample3',
            'credentials': {
                'user': 'user3',
                'pass': 'password3',
            }
        })

        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + 'este.teste.teste')
        response = self.client.get(url, format='json')
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['name'], 'VendorExample3')
        self.assertEqual(data[0]['credentials'], {
            'user': 'user3',
            'pass': 'password3',
        })

    @patch_has_permission
    def test_search_empty_vendor(self):
        """Ensure will return 0 object with no match in search."""
        url = reverse('container_scannning:vendor-list')
        url += '?name=VendorExample4'
        Vendor.objects.create(**{
            'name': 'VendorExample2',
            'credentials': {
                'user': 'user2',
                'pass': 'password2',
            }
        })
        Vendor.objects.create(**{
            'name': 'VendorExample3',
            'credentials': {
                'user': 'user3',
                'pass': 'password3',
            }
        })

        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + 'este.teste.teste')
        response = self.client.get(url, format='json')
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data), 0)


class VendorTests(APITestCase):
    permission = MagicMock(return_value=True)
    patch_has_permission = patch(
        'container_scannning.views.vendors.JWTAPIPermission.has_permission',
        permission
    )

    @patch_has_permission
    def test_get_vendor(self):
        """Ensure we can get a vendor object."""
        vendor = Vendor.objects.create(**{
            'name': 'VendorExample2',
            'credentials': {
                'user': 'user2',
                'pass': 'password2',
            }
        })
        url = reverse('container_scannning:vendor',
                      kwargs={'vendor_id': vendor.id})
        self.client.force_authenticate(None)
        response = self.client.get(url, format='json')
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data['name'], 'VendorExample2')
        self.assertEqual(data['credentials'], {
            'user': 'user2',
            'pass': 'password2',
        })

    @patch_has_permission
    def test_put_vendor(self):
        """Ensure we can put a vendor object."""

        vendor = Vendor.objects.create(**{
            'name': 'VendorExample2',
            'credentials': {
                'user': 'user2',
                'pass': 'password2',
            }
        })
        url = reverse('container_scannning:vendor',
                      kwargs={'vendor_id': vendor.id})
        data = {
            'name': 'VendorExample1',
            'credentials': {
                'user': 'user1',
                'pass': 'password1',
            }
        }
        self.client.put(url, data, format='json')
        self.client.force_authenticate(None)
        response = self.client.get(url, format='json')
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data['name'], 'VendorExample1')
        self.assertEqual(data['credentials'], {
            'user': 'user1',
            'pass': 'password1',
        })

    @patch_has_permission
    def test_delete_vendor(self):
        """Ensure we can delete a vendor object."""
        vendor = Vendor.objects.create(**{
            'name': 'VendorExample2',
            'credentials': {
                'user': 'user2',
                'pass': 'password2',
            }
        })
        url = reverse('container_scannning:vendor',
                      kwargs={'vendor_id': vendor.id})
        self.client.force_authenticate(None)
        response = self.client.delete(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
