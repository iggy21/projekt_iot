from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .models import TemperatureReading
from datetime import datetime


class TemperatureReadingModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
    
    def test_create_temperature_reading(self):
        reading = TemperatureReading.objects.create(
            sensor_id='sensor_001',
            temperature=25.5,
            humidity=60.0,
            device=self.user
        )
        self.assertEqual(reading.temperature, 25.5)
        self.assertEqual(reading.humidity, 60.0)
        self.assertEqual(reading.sensor_id, 'sensor_001')
        self.assertEqual(reading.device, self.user)
    
    def test_temperature_reading_without_humidity(self):
        reading = TemperatureReading.objects.create(
            sensor_id='sensor_002',
            temperature=20.0
        )
        self.assertIsNone(reading.humidity)
        self.assertIsNotNone(reading.timestamp)
    
    def test_temperature_reading_str(self):
        reading = TemperatureReading.objects.create(
            sensor_id='sensor_001',
            temperature=22.5
        )
        self.assertIn('Temp:', str(reading))
        self.assertIn('°C', str(reading))
    
    def test_temperature_reading_ordering(self):
        reading1 = TemperatureReading.objects.create(
            sensor_id='sensor_001',
            temperature=20.0
        )
        reading2 = TemperatureReading.objects.create(
            sensor_id='sensor_001',
            temperature=21.0
        )
        
        readings = list(TemperatureReading.objects.all())
        self.assertEqual(readings[0], reading2)  # Najnowszy pierwszy


class LoginViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
    
    def test_login_page_loads(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')
    
    def test_successful_login(self):
        response = self.client.post('/', {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertRedirects(response, '/dashboard/')
        self.assertTrue(response.wsgi_request.user.is_authenticated)
    
    def test_login_with_wrong_password(self):
        response = self.client.post('/', {
            'username': 'testuser',
            'password': 'wrongpass'
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        self.assertIn('error', response.context)
    
    def test_login_with_empty_fields(self):
        response = self.client.post('/', {
            'username': '',
            'password': ''
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('error', response.context)
    
    def test_redirect_if_already_logged_in(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/')
        self.assertRedirects(response, '/dashboard/')


class DashboardViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
    
    def test_dashboard_requires_login(self):
        response = self.client.get('/dashboard/')
        self.assertRedirects(response, '/?next=/dashboard/')
    
    def test_dashboard_loads_when_logged_in(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/dashboard/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard.html')
        self.assertEqual(response.context['user'], self.user)


class LogoutViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
    
    def test_logout(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/logout/')
        self.assertRedirects(response, '/')
        self.assertFalse(response.wsgi_request.user.is_authenticated)


class TemperatureViewSetTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        TemperatureReading.objects.create(
            sensor_id='sensor_001',
            temperature=20.0,
            humidity=50.0,
            device=self.user
        )
        TemperatureReading.objects.create(
            sensor_id='sensor_001',
            temperature=25.0,
            humidity=60.0,
            device=self.user
        )
        TemperatureReading.objects.create(
            sensor_id='sensor_001',
            temperature=30.0,
            humidity=70.0,
            device=self.user
        )
    
    def test_list_readings(self):
        response = self.client.get('/sensor/api/readings/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
    
    def test_create_reading(self):
        data = {
            'sensor_id': 'sensor_002',
            'temperature': 22.5,
            'humidity': 55.0
        }
        response = self.client.post('/sensor/api/readings/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['temperature'], 22.5)
        reading = TemperatureReading.objects.get(id=response.data['id'])
        self.assertEqual(reading.device, self.user)
    
    def test_retrieve_reading(self):
        reading = TemperatureReading.objects.first()
        response = self.client.get(f'/sensor/api/readings/{reading.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], reading.id)
    
    def test_update_reading(self):
        reading = TemperatureReading.objects.first()
        data = {
            'sensor_id': reading.sensor_id,
            'temperature': 28.0,
            'humidity': 65.0
        }
        response = self.client.put(f'/sensor/api/readings/{reading.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['temperature'], 28.0)
    
    def test_delete_reading(self):
        reading = TemperatureReading.objects.first()
        response = self.client.delete(f'/sensor/api/readings/{reading.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(TemperatureReading.objects.filter(id=reading.id).exists())
    
    def test_latest_action(self):
        response = self.client.get('/sensor/api/readings/latest/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('temperature', response.data)
        self.assertIn('timestamp', response.data)
    
    def test_latest_action_no_data(self):
        TemperatureReading.objects.all().delete()
        response = self.client.get('/sensor/api/readings/latest/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)
    
    def test_average_action(self):
        response = self.client.get('/sensor/api/readings/average/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('average_temperature', response.data)
        self.assertEqual(response.data['average_temperature'], 25.0)
    
    def test_average_action_no_data(self):
        TemperatureReading.objects.all().delete()
        response = self.client.get('/sensor/api/readings/average/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['average_temperature'], 0)
    
    def test_statistics_action(self):
        response = self.client.get('/sensor/api/readings/statistics/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('min', response.data)
        self.assertIn('max', response.data)
        self.assertIn('avg', response.data)
        self.assertIn('count', response.data)
        self.assertEqual(response.data['min'], 20.0)
        self.assertEqual(response.data['max'], 30.0)
        self.assertEqual(response.data['count'], 3)
    
    def test_statistics_action_no_data(self):
        TemperatureReading.objects.all().delete()
        response = self.client.get('/sensor/api/readings/statistics/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)
    
    def test_requires_authentication(self):
        self.client.force_authenticate(user=None)
        response = self.client.get('/sensor/api/readings/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TemperatureReadingSerializerTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
    
    def test_serialize_reading(self):
        reading = TemperatureReading.objects.create(
            sensor_id='sensor_001',
            temperature=25.5,
            humidity=60.0,
            device=self.user
        )
        from .serializers import TemperatureReadingSerializer
        serializer = TemperatureReadingSerializer(reading)
        data = serializer.data
        
        self.assertEqual(data['sensor_id'], 'sensor_001')
        self.assertEqual(data['temperature'], 25.5)
        self.assertEqual(data['humidity'], 60.0)
        self.assertIn('id', data)
        self.assertIn('timestamp', data)
    
    def test_deserialize_reading(self):
        from .serializers import TemperatureReadingSerializer
        data = {
            'sensor_id': 'sensor_002',
            'temperature': 22.0,
            'humidity': 55.0
        }
        serializer = TemperatureReadingSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        reading = serializer.save(device=self.user)
        self.assertEqual(reading.temperature, 22.0)
        self.assertEqual(reading.device, self.user)


