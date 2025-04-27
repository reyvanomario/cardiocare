import uuid
import jwt
import datetime
from unittest.mock import patch, mock_open, Mock
from django.test import TestCase, RequestFactory, Client
from django.urls import reverse
from django.http import HttpResponse, JsonResponse
from django.contrib.messages.storage.fallback import FallbackStorage
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework import status
import json

from .models import BookKonsultasi, JadwalKonsultasi, Dokter, RumahSakit
from .views import (
    list_dokter, list_rumah_sakit, view_dokter, KonsultasiSayaView, sanitize_input, validate_uuid
)

class HelperFunctionsTest(TestCase):
    def test_sanitize_input_with_valid_string(self):
        result = sanitize_input("Test string")
        self.assertEqual(result, "Test string")

    def test_sanitize_input_with_none(self):
        result = sanitize_input(None)
        self.assertIsNone(result)

    def test_sanitize_input_with_html(self):
        result = sanitize_input("<script>alert('XSS')</script>Test string")
        self.assertEqual(result, "alert('XSS')Test string")

    def test_validate_uuid_with_valid_string(self):
        valid_uuid = str(uuid.uuid4())
        self.assertTrue(validate_uuid(valid_uuid))

    def test_validate_uuid_with_uuid_object(self):
        valid_uuid = uuid.uuid4()
        self.assertTrue(validate_uuid(valid_uuid))

    def test_validate_uuid_with_invalid_string(self):
        self.assertFalse(validate_uuid("not-a-uuid"))

    def test_validate_uuid_with_none(self):
        self.assertFalse(validate_uuid(None))


class ListDokterTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.rumah_sakit = RumahSakit.objects.create(
            id_rumah_sakit=uuid.uuid4(),
            nama_rumah_sakit="Test Hospital"
        )
        self.dokter = Dokter.objects.create(
            id_dokter=uuid.uuid4(),
            nama_dokter="Dr. Test",
            rumah_sakit=self.rumah_sakit
        )
        self.jadwal = JadwalKonsultasi.objects.create(
            id_jdwl_konsultasi=uuid.uuid4(),
            dokter=self.dokter,
            hari="Senin",
            jam_mulai=datetime.time(9, 0),
            jam_selesai=datetime.time(12, 0),
            kuota=10
        )

    def test_list_dokter_success_with_multiple_jadwal(self):
        second_dokter = Dokter.objects.create(
            id_dokter=uuid.uuid4(),
            nama_dokter="Dr. Another",
            rumah_sakit=self.rumah_sakit
        )

        second_jadwal = JadwalKonsultasi.objects.create(
            id_jdwl_konsultasi=uuid.uuid4(),
            dokter=second_dokter,
            hari="Selasa",
            jam_mulai=datetime.time(14, 0),
            jam_selesai=datetime.time(16, 0),
            kuota=8
        )
        
        with patch('book_konsultasi.views.HARI_URUTAN', {'Senin': 0, 'Selasa': 1}):
            request = self.factory.get(reverse('book_konsultasi:list_dokter', args=[self.rumah_sakit.id_rumah_sakit]))
            
            setattr(request, 'session', 'session')
            messages = FallbackStorage(request)
            setattr(request, '_messages', messages)
            
            with patch('book_konsultasi.views.render') as mock_render:
                mock_render.return_value = HttpResponse("Success response", status=200)
                
                response = list_dokter(request, self.rumah_sakit.id_rumah_sakit)
                
                self.assertEqual(response.status_code, 200)
                mock_render.assert_called_once()
                context = mock_render.call_args[0][2]
                
                self.assertEqual(len(context['dokter']), 2)

                doctor_names = [doc['dokter'].nama_dokter for doc in context['dokter']]
                self.assertIn("Dr. Test", doctor_names)
                self.assertIn("Dr. Another", doctor_names)

    def test_list_dokter_success(self):
        request = self.factory.get(reverse('book_konsultasi:list_dokter', args=[self.rumah_sakit.id_rumah_sakit]))
        
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)
        
        with patch('book_konsultasi.views.render') as mock_render:
            mock_render.return_value = HttpResponse("Success", status=200)
            
            with patch('book_konsultasi.views.HARI_URUTAN', {'Senin': 1}):
                response = list_dokter(request, self.rumah_sakit.id_rumah_sakit)
                
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.content.decode(), "Success")
                
                mock_render.assert_called_once()
                context = mock_render.call_args[0][2]
                
                self.assertIn('dokter', context)
                self.assertEqual(len(context['dokter']), 1)
                self.assertEqual(context['dokter'][0]['dokter'].nama_dokter, "Dr. Test")
                self.assertEqual(context['dokter'][0]['jadwal'], self.jadwal)
                self.assertEqual(context['rumah_sakit'], self.rumah_sakit)

    def test_list_dokter_with_valid_id(self):
        with patch('book_konsultasi.views.HARI_URUTAN', {'Senin': 0}):
            request = self.factory.get(reverse('book_konsultasi:list_dokter', args=[self.rumah_sakit.id_rumah_sakit]))
            
            setattr(request, 'session', 'session')
            messages = FallbackStorage(request)
            setattr(request, '_messages', messages)
            
            with patch('book_konsultasi.views.render') as mock_render:
                mock_render.return_value = HttpResponse("Dr. Test", status=200)
                
                response = list_dokter(request, self.rumah_sakit.id_rumah_sakit)
                
                self.assertEqual(response.status_code, 200)
                
                mock_render.assert_called_once()
                context = mock_render.call_args[0][2]
                self.assertIn('dokter', context)
                self.assertEqual(context['dokter'][0]['dokter'].nama_dokter, "Dr. Test")

    def test_list_dokter_with_invalid_id(self):
        request = self.factory.get('/cari-konsultasi/list-dokter/invalid-uuid/')
        
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)
        
        response = list_dokter(request, "invalid-uuid")
        
        self.assertEqual(response.status_code, 302)

    def test_list_dokter_no_dokter_found(self):
        empty_rs = RumahSakit.objects.create(
            id_rumah_sakit=uuid.uuid4(),
            nama_rumah_sakit="Empty Hospital"
        )
        
        request = self.factory.get(reverse('book_konsultasi:list_dokter', args=[empty_rs.id_rumah_sakit]))
        
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)
        
        response = list_dokter(request, empty_rs.id_rumah_sakit)
        
        self.assertEqual(response.status_code, 302)

class ListRumahSakitTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.rs1 = RumahSakit.objects.create(
            id_rumah_sakit=uuid.uuid4(),
            nama_rumah_sakit="Hospital A"
        )
        self.rs2 = RumahSakit.objects.create(
            id_rumah_sakit=uuid.uuid4(),
            nama_rumah_sakit="Hospital B"
        )

    def test_list_rumah_sakit_basic(self):
        request = self.factory.get(reverse('book_konsultasi:list_rumah_sakit'))
        response = list_rumah_sakit(request)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Hospital A")
        self.assertContains(response, "Hospital B")

    def test_list_rumah_sakit_with_search(self):
        with patch('book_konsultasi.views.render') as mock_render:
            mock_render.return_value = HttpResponse('mocked')
            
            request = self.factory.get(reverse('book_konsultasi:list_rumah_sakit') + '?q=Hospital A')
            list_rumah_sakit(request)
            
            context = mock_render.call_args[0][2]
            
            rumah_sakit_list = context['rumah_sakit_list']
            self.assertEqual(len(rumah_sakit_list), 1)
            self.assertEqual(rumah_sakit_list[0].nama_rumah_sakit, "Hospital A")

    def test_list_rumah_sakit_with_pagination(self):
        for i in range(10):
            RumahSakit.objects.create(
                id_rumah_sakit=uuid.uuid4(),
                nama_rumah_sakit=f"Hospital {i}"
            )
        
        request = self.factory.get(reverse('book_konsultasi:list_rumah_sakit') + '?page=2')
        response = list_rumah_sakit(request)
        
        self.assertEqual(response.status_code, 200)

    def test_list_rumah_sakit_ajax_request(self):
        request = self.factory.get(reverse('book_konsultasi:list_rumah_sakit'))
        request.headers = {'x-requested-with': 'XMLHttpRequest'}
        
        response = list_rumah_sakit(request)
        
        self.assertTrue(isinstance(response, JsonResponse))
        
        data = json.loads(response.content.decode('utf-8'))
        
        self.assertIn('data', data)
        self.assertEqual(len(data['data']), 2)

class ViewDokterTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.rumah_sakit = RumahSakit.objects.create(
            id_rumah_sakit=uuid.uuid4(),
            nama_rumah_sakit="Test Hospital"
        )
        self.dokter = Dokter.objects.create(
            id_dokter=uuid.uuid4(),
            nama_dokter="Dr. Test",
            rumah_sakit=self.rumah_sakit
        )

    def test_view_dokter_with_valid_id(self):
        request = self.factory.get(reverse('book_konsultasi:view_dokter', args=[self.dokter.id_dokter]))
        
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)
        
        with patch('book_konsultasi.views.render') as mock_render:
            mock_render.return_value = HttpResponse("Dr. Test")
            
            response = view_dokter(request, self.dokter.id_dokter)
            
            self.assertEqual(response.status_code, 200)
            
            mock_render.assert_called_once()
            context = mock_render.call_args[0][2]
            
            self.assertEqual(context['dokter'], self.dokter)
            self.assertEqual(context['dokter'].nama_dokter, "Dr. Test")

    def test_view_dokter_with_invalid_id(self):
        request = self.factory.get('/cari-konsultasi/invalid-uuid/')
        
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)
        
        response = view_dokter(request, "invalid-uuid")
        
        self.assertEqual(response.status_code, 302)

    def test_view_dokter_not_found(self):
        non_existent_id = uuid.uuid4()
        request = self.factory.get(reverse('book_konsultasi:view_dokter', args=[non_existent_id]))
        
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)
        
        with patch('book_konsultasi.views.logger.error') as mock_logger:
            response = view_dokter(request, non_existent_id)
            
            self.assertEqual(response.status_code, 302)

class BookKonsultasiViewTest(APITestCase):
    def setUp(self):
        self.rumah_sakit = RumahSakit.objects.create(
            id_rumah_sakit=uuid.uuid4(),
            nama_rumah_sakit="Test Hospital"
        )
        self.dokter = Dokter.objects.create(
            id_dokter=uuid.uuid4(),
            nama_dokter="Dr. Test",
            rumah_sakit=self.rumah_sakit
        )
        self.jadwal = JadwalKonsultasi.objects.create(
            id_jdwl_konsultasi=uuid.uuid4(),
            dokter=self.dokter,
            hari="Senin",
            jam_mulai=datetime.time(9, 0),
            jam_selesai=datetime.time(12, 0),
            kuota=10
        )
        
        self.user_id = str(uuid.uuid4())
        self.jwt_token = "fake.jwt.token"
        self.url = reverse('book_konsultasi:book_konsultasi', args=[self.jadwal.id_jdwl_konsultasi])
        self.mock_public_key = "-----BEGIN PUBLIC KEY-----\nMIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCxxx\n-----END PUBLIC KEY-----"

    @patch('book_konsultasi.views.BookKonsultasiView.get_user_from_jwt')
    def test_get_bookings_authenticated(self, mock_get_user):
        mock_get_user.return_value = {'id': self.user_id}
        
        BookKonsultasi.objects.create(
            id_book_konsultasi=uuid.uuid4(),
            jadwal=self.jadwal,
            id_pasien=self.user_id,
            tanggal_pemesanan=timezone.now().date()
        )
        
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 1)

    @patch('book_konsultasi.views.BookKonsultasiView.get_user_from_jwt')
    def test_get_bookings_not_authenticated(self, mock_get_user):
        mock_get_user.return_value = None
        
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @patch('book_konsultasi.views.BookKonsultasiView.get_user_from_jwt')
    def test_post_booking_success(self, mock_get_user):
        mock_get_user.return_value = {'id': self.user_id}
        
        data = {}
        
        response = self.client.post(self.url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(BookKonsultasi.objects.count(), 1)
        
        self.jadwal.refresh_from_db()
        self.assertEqual(self.jadwal.kuota, 9)

    @patch('book_konsultasi.views.BookKonsultasiView.get_user_from_jwt')
    def test_post_booking_no_kuota(self, mock_get_user):
        mock_get_user.return_value = {'id': self.user_id}
        
        self.jadwal.kuota = 0
        self.jadwal.save()
        
        data = {}
        
        response = self.client.post(self.url, data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('kuota', response.data['error'].lower())

    @patch('book_konsultasi.views.BookKonsultasiView.get_user_from_jwt')
    def test_post_booking_already_booked(self, mock_get_user):
        mock_get_user.return_value = {'id': self.user_id}
        
        BookKonsultasi.objects.create(
            id_book_konsultasi=uuid.uuid4(),
            jadwal=self.jadwal,
            id_pasien=self.user_id,
            tanggal_pemesanan=timezone.now().date()
        )
        
        data = {}
        
        response = self.client.post(self.url, data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('sudah memesan', response.data['error'])

    @patch('book_konsultasi.views.BookKonsultasiView.get_user_from_jwt')
    def test_post_booking_invalid_jadwal(self, mock_get_user):
        mock_get_user.return_value = {'id': self.user_id}
        
        invalid_jadwal_id = uuid.uuid4()
        invalid_url = reverse('book_konsultasi:book_konsultasi', args=[invalid_jadwal_id])
        
        response = self.client.post(invalid_url, {})
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    @patch('book_konsultasi.views.BookKonsultasiView.get_user_from_jwt')
    @patch('book_konsultasi.views.JadwalKonsultasi.objects.get')
    def test_post_booking_transaction_error(self, mock_jadwal_get, mock_get_user):
        mock_get_user.return_value = {'id': self.user_id}
        
        mock_jadwal = Mock()
        mock_jadwal.kuota = -1
        mock_jadwal.refresh_from_db = lambda: None
        mock_jadwal_get.return_value = mock_jadwal
        
        with patch('book_konsultasi.views.transaction.atomic'), \
             patch('book_konsultasi.views.BookKonsultasi.objects.filter') as mock_filter, \
             patch('book_konsultasi.views.BookKonsultasi.objects.create') as mock_create:
            
            mock_filter.return_value = Mock()
            mock_filter.return_value.exists.return_value = False
            mock_create.return_value = Mock()
            
            response = self.client.post(self.url, {})
            
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn('Kuota konsultasi penuh', response.data['error'])
    
    @patch('book_konsultasi.views.BookKonsultasiView.get_user_from_jwt')
    def test_book_konsultasi_post_success(self, mock_get_user):
        mock_get_user.return_value = {'id': self.user_id}
        
        response = self.client.post(self.url, {})
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('data', response.data)
        self.assertIn('message', response.data)
        self.assertEqual(response.data['message'], "Konsultasi berhasil dipesan")
        
        self.assertEqual(BookKonsultasi.objects.count(), 1)
        booking = BookKonsultasi.objects.first()
        self.assertEqual(str(booking.id_pasien), self.user_id)
        self.assertEqual(booking.jadwal, self.jadwal)
        
        self.jadwal.refresh_from_db()
        self.assertEqual(self.jadwal.kuota, 9)

class KonsultasiSayaViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.rumah_sakit = RumahSakit.objects.create(
            id_rumah_sakit=uuid.uuid4(),
            nama_rumah_sakit="Test Hospital"
        )
        self.dokter = Dokter.objects.create(
            id_dokter=uuid.uuid4(),
            nama_dokter="Dr. Test",
            rumah_sakit=self.rumah_sakit
        )
        self.jadwal = JadwalKonsultasi.objects.create(
            id_jdwl_konsultasi=uuid.uuid4(),
            dokter=self.dokter,
            hari="Senin",
            jam_mulai=datetime.time(9, 0),
            jam_selesai=datetime.time(12, 0),
            kuota=10
        )
        
        self.user_id = str(uuid.uuid4())
        self.booking = BookKonsultasi.objects.create(
            id_book_konsultasi=uuid.uuid4(),
            jadwal=self.jadwal,
            id_pasien=self.user_id,
            tanggal_pemesanan=timezone.now().date()
        )
        
        self.jwt_token = "fake.jwt.token"
        self.mock_public_key = "-----BEGIN PUBLIC KEY-----\nMIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCxxx\n-----END PUBLIC KEY-----"

    @patch('builtins.open', new_callable=mock_open, read_data="public key data")
    @patch('jwt.decode')
    def test_konsultasi_saya_valid_jwt(self, mock_jwt_decode, mock_file):
        mock_jwt_decode.return_value = {'id': self.user_id}
        
        request = self.factory.get(reverse('book_konsultasi:konsultasi_saya'))
        request.COOKIES = {'jwt': self.jwt_token}
        
        view = KonsultasiSayaView.as_view()
        response = view(request)
        
        self.assertEqual(response.status_code, 200)

    @patch('builtins.open', new_callable=mock_open, read_data="public key data")
    @patch('jwt.decode')
    @patch('requests.get')
    def test_konsultasi_saya_no_jwt(self, mock_get, mock_jwt_decode, mock_file):
        client = Client()
        
        response = client.get(reverse('book_konsultasi:konsultasi_saya'))
        
        self.assertTrue(hasattr(response, 'context'))

        self.assertIn('error_message', response.context)
        self.assertEqual(response.context['error_message'], 'Anda belum login')

    @patch('builtins.open', new_callable=mock_open, read_data="public key data")
    @patch('jwt.decode')
    @patch('requests.get')
    def test_konsultasi_saya_expired_token(self, mock_get, mock_jwt_decode, mock_file):
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {'public_key': self.mock_public_key}
        mock_get.return_value = mock_response
        
        mock_jwt_decode.side_effect = jwt.ExpiredSignatureError()
        
        self.client.cookies['jwt'] = self.jwt_token
        response = self.client.get(reverse('book_konsultasi:konsultasi_saya'))
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('Sesi', response.context['error_message'])

    @patch('book_konsultasi.views.requests.get')
    @patch('jwt.decode')
    def test_konsultasi_saya_success_request(self, mock_jwt_decode, mock_get):
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {'public_key': 'mock_key'}
        mock_get.return_value = mock_response
        
        mock_jwt_decode.return_value = {'id': self.user_id}

        client = Client()
        client.cookies['jwt'] = self.jwt_token

        response = client.get(reverse('book_konsultasi:konsultasi_saya'))

        self.assertEqual(response.status_code, 200)
        self.assertIn('bookings', response.context)
        self.assertEqual(len(response.context['bookings']), 1)
        
        booking_data = response.context['bookings'][0]
        self.assertEqual(booking_data['id'], str(self.booking.id_book_konsultasi))
        self.assertEqual(booking_data['nama_dokter'], "Dr. Test")
    