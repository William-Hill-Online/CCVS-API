from unittest.mock import MagicMock
from unittest.mock import patch

from container_scanning.models import Image
from container_scanning.serializers import images
from container_scanning.serializers import vendors
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

permission = MagicMock(return_value=True)
patch_has_permission = patch(
    'container_scanning.views.images.JWTAPIPermission.has_permission',
    permission
)


class ImagesTests(APITestCase):

    def create_image_deps(self, name):
        image = images.ImageSerializer(data={
            'name': name
        })
        image.is_valid()
        image.save()

        return image.instance

    @patch_has_permission
    def test_create_image(self):
        """Ensure we can create a new image object."""
        url = reverse('container_scanning:image-list')
        data = {'name': 'ImageExample'}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Image.objects.count(), 1)
        self.assertEqual(Image.objects.get().name, 'ImageExample')

    @patch_has_permission
    def test_list_one_image(self):
        """Ensure we can list one image objects."""

        self.create_image_deps('ImageExample')
        url = reverse('container_scanning:image-list')
        response = self.client.get(url, format='json')
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['name'], 'ImageExample')

    @patch_has_permission
    def test_list_two_image(self):
        """Ensure we can list two image objects."""
        self.create_image_deps('ImageExample1')
        self.create_image_deps('ImageExample2')
        url = reverse('container_scanning:image-list')
        response = self.client.get(url, format='json')
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['name'], 'ImageExample1')
        self.assertEqual(data[1]['name'], 'ImageExample2')

    @patch_has_permission
    def test_search_image(self):
        """Ensure we can search one image object."""
        url = reverse('container_scanning:image-list')
        url += '?name=ImageExample2'
        self.create_image_deps('ImageExample1')
        self.create_image_deps('ImageExample2')
        self.create_image_deps('ImageExample3')

        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + 'este.teste.teste')
        response = self.client.get(url, format='json')
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['name'], 'ImageExample2')

    @patch_has_permission
    def test_search_empty_image(self):
        """Ensure will return 0 object with no match in search."""
        url = reverse('container_scanning:image-list')
        url += '?name=ImageExample5'
        self.create_image_deps('ImageExample1')
        self.create_image_deps('ImageExample2')
        self.create_image_deps('ImageExample3')

        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + 'test.test.test')
        response = self.client.get(url, format='json')
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data), 0)


class ImageTests(APITestCase):

    def create_image_deps(self, name):
        image = images.ImageSerializer(data={
            'name': name
        })
        image.is_valid()
        image.save()

        return image.instance

    @patch_has_permission
    def test_get_image(self):
        """Ensure we can get a image object."""
        image = self.create_image_deps('ImageExample')

        url = reverse(
            'container_scanning:image',
            kwargs={
                'image_id': image.id,
            }
        )
        response = self.client.get(url, format='json')
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data['name'], 'ImageExample')


class ImageVendorView(APITestCase):

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
    @patch('container_scanning.views.images.add_scan')
    def test_post_image_anchore_engine(self, add_scan):
        """Ensure we can create a scan job."""
        add_scan.delay.return_value.id = 'jobid_123'

        image = self.create_image_deps()
        vendor = self.create_vendor_deps('anchore_engine')

        url = reverse(
            'container_scanning:image-vendor',
            kwargs={
                'image_id': image.id,
                'vendor_id': vendor.id
            }
        )

        response = self.client.post(url, format='json')
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(data['vendor'], str(vendor.id))
        self.assertEqual(data['image'], str(image.id))
        self.assertEqual(data['image_vendor_id'], '')
        self.assertEqual(data['job_id'], 'jobid_123')

        add_scan.delay.assert_called_with(image.id, vendor.id)

        add_scan.reset_mock()  # Reset the mock object

        add_scan.delay.assert_not_called()

    @patch_has_permission
    @patch('container_scanning.views.images.add_scan')
    def test_put_image_anchore_engine(self, add_scan):
        """Ensure we can create(update) a scan job."""
        add_scan.delay.return_value.id = 'jobid_234'

        image = self.create_image_deps()
        vendor = self.create_vendor_deps('anchore_engine')

        image_vendor = images.ImageVendorSerializer(data={
            'vendor': vendor.id,
            'image': image.id,
            'image_vendor_id': 'name234'
        })
        image_vendor.is_valid()
        image_vendor.save()

        url = reverse(
            'container_scanning:image-vendor',
            kwargs={
                'image_id': image.id,
                'vendor_id': vendor.id
            }
        )

        response = self.client.put(url, format='json')
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(data['vendor'], str(vendor.id))
        self.assertEqual(data['image'], str(image.id))
        self.assertEqual(data['image_vendor_id'], 'name234')
        self.assertEqual(data['job_id'], 'jobid_234')

        add_scan.delay.assert_called_with(image.id, vendor.id, force=True)

        add_scan.reset_mock()  # Reset the mock object

        add_scan.delay.assert_not_called()

    @patch_has_permission
    def test_get_image_anchore_engine(self):
        """Ensure we can get image-vendor."""

        image = self.create_image_deps()
        vendor = self.create_vendor_deps('anchore_engine')

        image_vendor = images.ImageVendorSerializer(data={
            'vendor': vendor.id,
            'image': image.id,
            'image_vendor_id': 'name123'
        })
        image_vendor.is_valid()
        image_vendor.save()

        url = reverse(
            'container_scanning:image-vendor',
            kwargs={
                'image_id': image.id,
                'vendor_id': vendor.id
            }
        )
        response = self.client.get(url, format='json')
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data['vendor'], str(vendor.id))
        self.assertEqual(data['image'], str(image.id))
        self.assertEqual(data['image_vendor_id'], 'name123')


class ImageVendorVulnView(APITestCase):

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
    @patch('container_scanning.vendors.clair.facade.get_vuln')
    def test_get_vuln_clair(self, mock_get_vuln):
        """Ensure we can get vuln from clair."""

        mock_get_vuln.return_value = {'data': [1, 2, 3]}

        image = self.create_image_deps()
        vendor = self.create_vendor_deps('clair')
        image_vendor = images.ImageVendorSerializer(data={
            'vendor': vendor.id,
            'image': image.id,
            'image_vendor_id': 'name123'
        })
        image_vendor.is_valid()
        image_vendor.save()

        url = reverse(
            'container_scanning:image-vendor-vuln',
            kwargs={
                'image_id': image.id,
                'vendor_id': vendor.id
            }
        )

        response = self.client.get(url, format='json')
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data, {'data': [1, 2, 3]})

    @patch_has_permission
    @patch('container_scanning.vendors.anchore_engine.facade.get_vuln')
    def test_get_vuln_anchore_engine(self, mock_get_vuln):
        """Ensure we can get vuln from anchore."""
        mock_get_vuln.return_value = {'data': [1, 2, 3]}

        image = self.create_image_deps()
        vendor = self.create_vendor_deps('anchore_engine')
        image_vendor = images.ImageVendorSerializer(data={
            'vendor': vendor.id,
            'image': image.id,
            'image_vendor_id': 'name123'
        })
        image_vendor.is_valid()
        image_vendor.save()

        url = reverse(
            'container_scanning:image-vendor-vuln',
            kwargs={
                'image_id': image.id,
                'vendor_id': vendor.id
            }
        )

        response = self.client.get(url, format='json')
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data, {'data': [1, 2, 3]})
