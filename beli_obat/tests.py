import os
os.environ['DJANGO_SECRET_KEY'] = 'test-secret-key-for-running-tests'
from django.test import TestCase, Client, RequestFactory, override_settings
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.contrib.messages.storage.fallback import FallbackStorage
from django.utils.datastructures import MultiValueDict
from django.contrib.sessions.middleware import SessionMiddleware
from uuid import uuid4
from uuid import UUID
import json, jwt
from decimal import Decimal
import unittest
from unittest.mock import patch, MagicMock, ANY

from beli_obat.models import Obat, TransaksiPembelianObat
from beli_obat.views import (
    test_view, show_page_obat, katalog_obat, detail_obat, 
    show_checkout_page, checkout_obat, otp_view, verify_otp, 
    view_riwayat_pembelian_obat, validate_jwt_and_get_user
)
# At the top of tests.py
import os
os.environ['DJANGO_SECRET_KEY'] = 'test-secret-key'

# Helper functions for tests
def add_session_to_request(request):
    middleware = SessionMiddleware(lambda x: x)
    middleware.process_request(request)
    request.session.save()

def add_message_storage_to_request(request):
    setattr(request, '_messages', FallbackStorage(request))

@override_settings(SECRET_KEY='django-test-insecure-key')
class ObatModelTests(TestCase):
    def setUp(self):
        # Create a test Obat instance
        self.obat = Obat.objects.create(
            nama_obat="Paracetamol",
            deskripsi="Obat pereda nyeri dan demam",
            harga=Decimal('10000.00'),
            aturan_pakai="3x1 setelah makan",
            stok=100
        )
    
    def test_obat_creation(self):
        """Test the creation of an Obat instance"""
        self.assertTrue(isinstance(self.obat, Obat))
        self.assertEqual(self.obat.__str__(), "Paracetamol")
    
    def test_obat_fields(self):
        """Test the fields of an Obat instance"""
        self.assertEqual(self.obat.nama_obat, "Paracetamol")
        self.assertEqual(self.obat.deskripsi, "Obat pereda nyeri dan demam")
        self.assertEqual(self.obat.harga, Decimal('10000.00'))
        self.assertEqual(self.obat.aturan_pakai, "3x1 setelah makan")
        self.assertEqual(self.obat.stok, 100)

@override_settings(SECRET_KEY='django-test-insecure-key')
class TransaksiPembelianObatModelTests(TestCase):
    def setUp(self):
        # Create a test Obat instance
        self.obat = Obat.objects.create(
            nama_obat="Paracetamol",
            deskripsi="Obat pereda nyeri dan demam",
            harga=Decimal('10000.00'),
            aturan_pakai="3x1 setelah makan",
            stok=100
        )
        
        # Create a test TransaksiPembelianObat instance
        self.user_id = uuid4()
        self.transaksi = TransaksiPembelianObat.objects.create(
            user_id=self.user_id,
            obat=self.obat,
            quantity=2,
            total_biaya=20000
        )
    
    def test_transaksi_creation(self):
        """Test the creation of a TransaksiPembelianObat instance"""
        self.assertTrue(isinstance(self.transaksi, TransaksiPembelianObat))
    
    def test_transaksi_fields(self):
        """Test the fields of a TransaksiPembelianObat instance"""
        self.assertEqual(self.transaksi.user_id, self.user_id)
        self.assertEqual(self.transaksi.obat, self.obat)
        self.assertEqual(self.transaksi.quantity, 2)
        self.assertEqual(self.transaksi.total_biaya, 20000)
        self.assertIsNotNone(self.transaksi.waktu_transaksi)

class ViewTestsMixin:
    """Mixin to provide common functionality for view tests"""
    
    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()
        
        # Create test obat
        self.obat = Obat.objects.create(
            nama_obat="Paracetamol",
            deskripsi="Obat pereda nyeri dan demam",
            harga=Decimal('10000.00'),
            aturan_pakai="3x1 setelah makan",
            stok=100
        )
        
        # Mock user data to be returned by validate_jwt_and_get_user
        self.mock_user_data = {
            'id': str(uuid4()),
            'username': 'testuser',
            'email': 'test@example.com',
        }

    def mock_validate_jwt_success(self, token):
        """Mock for successful validation of JWT token"""
        return self.mock_user_data, None
    
    def mock_validate_jwt_failure(self, token):
        """Mock for failed validation of JWT token"""
        return None, HttpResponseForbidden("Token tidak valid. Silakan login.")

@override_settings(SECRET_KEY='django-test-insecure-key')
class TestViewTests(ViewTestsMixin, TestCase):
    @patch('psycopg2.connect')
    def test_test_view(self, mock_connect):
        """Test the test_view function"""
        # Setup mock cursor
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [('1', 'Paracetamol', 'Deskripsi', '10000.00', '3x1', 100)]
        
        # Setup mock connection
        mock_connection = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection
        
        # Call the view
        response = self.client.get(reverse('beli_obat:test-view'))
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), "Data obat berhasil diambil.")
        
        # Verify cursor execution
        mock_cursor.execute.assert_called_with("SELECT * FROM public.obat")

@override_settings(SECRET_KEY='django-test-insecure-key')
class ValidateJWTTests(TestCase):
    @patch('requests.get')
    def test_validate_jwt_success(self, mock_get):
        """Test successful validation of JWT"""
        # Mock public key response
        mock_public_key_response = MagicMock()
        mock_public_key_response.json.return_value = {'public_key': 'mock_public_key'}
        mock_public_key_response.raise_for_status = MagicMock()
        
        # Mock user response
        mock_user_response = MagicMock()
        mock_user_data = {'id': str(uuid4()), 'username': 'testuser', 'email': 'test@example.com'}
        mock_user_response.json.return_value = mock_user_data
        
        # Setup mock get to return appropriate responses
        mock_get.side_effect = [mock_public_key_response, mock_user_response]
        
        # Mock jwt.decode to return a valid payload
        with patch('jwt.decode', return_value={'user_id': 'mock_user_id'}):
            user, error = validate_jwt_and_get_user('mock_token')
            
            # Assertions
            self.assertIsNotNone(user)
            self.assertIsNone(error)
            self.assertEqual(user, mock_user_data)
    
    @patch('requests.get')
    def test_validate_jwt_invalid_token(self, mock_get):
        """Test validation with invalid JWT"""
        import jwt
        
        # Mock public key response
        mock_public_key_response = MagicMock()
        mock_public_key_response.json.return_value = {'public_key': 'mock_public_key'}
        mock_public_key_response.raise_for_status = MagicMock()
        
        # Setup mock get
        mock_get.return_value = mock_public_key_response
        
        # Mock jwt.decode to raise an InvalidTokenError
        with patch('jwt.decode', side_effect=jwt.InvalidTokenError("Invalid token")):
            # Check if function returns a tuple or just a HttpResponseForbidden
            result = validate_jwt_and_get_user('mock_token')
            
            if isinstance(result, tuple):
                user, error = result
                self.assertIsNone(user)
                self.assertIsNotNone(error)
                self.assertEqual(error.status_code, 403)
            else:
                # If it returns just the error response
                self.assertEqual(result.status_code, 403)

@override_settings(SECRET_KEY='django-test-insecure-key')
class ShowPageObatTests(ViewTestsMixin, TestCase):
    @patch('beli_obat.views.validate_jwt_and_get_user')
    def test_show_page_obat_authenticated(self, mock_validate):
        """Test show_page_obat with authenticated user"""
        # Setup mock for validate_jwt_and_get_user
        mock_validate.side_effect = self.mock_validate_jwt_success
        
        # Set JWT cookie
        self.client.cookies['jwt'] = 'mock_token'
        
        # Call the view
        response = self.client.get(reverse('beli_obat:show-page-obat'))
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tes-page-obat.html')
        self.assertIn('list_obat', response.context)
        self.assertIn('user_data', response.context)
    
    def test_show_page_obat_no_token(self):
        """Test show_page_obat with no JWT token"""
        # Call the view without setting JWT cookie
        response = self.client.get(reverse('beli_obat:show-page-obat'))
        
        # Assertions
        self.assertEqual(response.status_code, 403)
    
    @patch('beli_obat.views.validate_jwt_and_get_user')
    def test_show_page_obat_invalid_token(self, mock_validate):
        """Test show_page_obat with invalid JWT token"""
        # Setup mock for validate_jwt_and_get_user
        mock_validate.side_effect = self.mock_validate_jwt_failure
        
        # Set JWT cookie
        self.client.cookies['jwt'] = 'invalid_token'
        
        # Call the view
        response = self.client.get(reverse('beli_obat:show-page-obat'))
        
        # Assertions
        self.assertEqual(response.status_code, 403)

@override_settings(SECRET_KEY='django-test-insecure-key')
class KatalogObatTests(ViewTestsMixin, TestCase):
    def test_katalog_obat_no_auth(self):
        """Test katalog_obat view without authentication"""
        # Call the view without setting JWT cookie
        response = self.client.get(reverse('beli_obat:katalog_obat'))
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'katalog.html')
        self.assertIn('obat_list', response.context)
        self.assertFalse(response.context['is_authenticated'])
        self.assertIsNone(response.context['user'])
    
    @patch('beli_obat.views.validate_jwt_and_get_user')
    def test_katalog_obat_authenticated(self, mock_validate):
        """Test katalog_obat view with authenticated user"""
        # Setup mock for validate_jwt_and_get_user
        mock_validate.side_effect = self.mock_validate_jwt_success
        
        # Set JWT cookie
        self.client.cookies['jwt'] = 'mock_token'
        
        # Call the view
        response = self.client.get(reverse('beli_obat:katalog_obat'))
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'katalog.html')
        self.assertIn('obat_list', response.context)
        self.assertTrue(response.context['is_authenticated'])
        self.assertEqual(response.context['user'], self.mock_user_data)
    
    def test_katalog_obat_search(self):
        """Test katalog_obat view with search query"""
        # Call the view with search parameter
        response = self.client.get(reverse('beli_obat:katalog_obat') + '?q=para')
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'katalog.html')
        self.assertIn('obat_list', response.context)
        self.assertEqual(response.context['current_query'], 'para')
        
    def test_katalog_obat_sort(self):
        """Test katalog_obat view with sorting"""
        # Call the view with sort parameter
        response = self.client.get(reverse('beli_obat:katalog_obat') + '?sort=price-desc')
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'katalog.html')
        self.assertIn('obat_list', response.context)
        self.assertEqual(response.context['current_sort'], 'price-desc')

@override_settings(SECRET_KEY='django-test-insecure-key')
class DetailObatTests(ViewTestsMixin, TestCase):
    def test_detail_obat_no_auth(self):
        """Test detail_obat view without authentication"""
        # Call the view without setting JWT cookie
        response = self.client.get(reverse('beli_obat:detail_obat', args=[self.obat.id]))
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'detail_obat.html')
        self.assertIn('obat', response.context)
        self.assertFalse(response.context['is_authenticated'])
        self.assertIsNone(response.context['user'])
    
    @patch('beli_obat.views.validate_jwt_and_get_user')
    def test_detail_obat_authenticated(self, mock_validate):
        """Test detail_obat view with authenticated user"""
        # Setup mock for validate_jwt_and_get_user
        mock_validate.side_effect = self.mock_validate_jwt_success
        
        # Set JWT cookie
        self.client.cookies['jwt'] = 'mock_token'
        
        # Call the view
        response = self.client.get(reverse('beli_obat:detail_obat', args=[self.obat.id]))
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'detail_obat.html')
        self.assertIn('obat', response.context)
        self.assertTrue(response.context['is_authenticated'])
        self.assertEqual(response.context['user'], self.mock_user_data)
    
    def test_detail_obat_not_found(self):
        """Test detail_obat view with non-existent obat ID"""
        # Call the view with a non-existent obat ID
        response = self.client.get(reverse('beli_obat:detail_obat', args=[uuid4()]))
        
        # Assertions
        self.assertEqual(response.status_code, 404)

@override_settings(SECRET_KEY='django-test-insecure-key')
class ShowCheckoutPageTests(ViewTestsMixin, TestCase):
    def test_show_checkout_page_no_token(self):
        """Test show_checkout_page with no JWT token"""
        # Call the view without setting JWT cookie
        response = self.client.get(reverse('beli_obat:checkout-page', args=[self.obat.id]))
        
        # Assertions
        self.assertEqual(response.status_code, 302)  # Redirect to login
        self.assertTrue(response.url.startswith('http://localhost:3000/login/'))
    
    @patch('beli_obat.views.validate_jwt_and_get_user')
    def test_show_checkout_page_authenticated(self, mock_validate):
        """Test show_checkout_page with authenticated user"""
        # Setup mock for validate_jwt_and_get_user
        mock_validate.side_effect = self.mock_validate_jwt_success
        
        # Set JWT cookie
        self.client.cookies['jwt'] = 'mock_token'
        
        # Call the view
        response = self.client.get(reverse('beli_obat:checkout-page', args=[self.obat.id]))
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'checkout_page.html')
        self.assertIn('obat', response.context)
        self.assertEqual(response.context['obat'], self.obat)
        self.assertTrue(response.context['is_authenticated'])
        self.assertEqual(response.context['user'], self.mock_user_data)
    
    @patch('beli_obat.views.validate_jwt_and_get_user')
    def test_show_checkout_page_invalid_token(self, mock_validate):
        """Test show_checkout_page with invalid JWT token"""
        # Setup mock for validate_jwt_and_get_user
        mock_validate.side_effect = self.mock_validate_jwt_failure
        
        # Set JWT cookie
        self.client.cookies['jwt'] = 'invalid_token'
        
        # Call the view
        response = self.client.get(reverse('beli_obat:checkout-page', args=[self.obat.id]))
        
        # Assertions
        self.assertEqual(response.status_code, 403)

@override_settings(SECRET_KEY='django-test-insecure-key')
class CheckoutObatTests(ViewTestsMixin, TestCase):
    def test_checkout_obat_no_token(self):
        """Test checkout_obat with no JWT token"""
        # Call the view without setting JWT cookie
        response = self.client.get(reverse('beli_obat:checkout-obat', args=[self.obat.id, 2]))
        
        # Assertions
        self.assertEqual(response.status_code, 302)  # Redirect to login
        self.assertTrue(response.url.startswith('http://localhost:3000/login/'))
    
    @patch('beli_obat.views.validate_jwt_and_get_user')
    def test_checkout_obat_authenticated(self, mock_validate):
        """Test checkout_obat with authenticated user"""
        # Setup mock for validate_jwt_and_get_user
        mock_validate.side_effect = self.mock_validate_jwt_success
        
        # Set JWT cookie
        self.client.cookies['jwt'] = 'mock_token'
        
        # Create request with session
        request = self.factory.get(reverse('beli_obat:checkout-obat', args=[self.obat.id, 2]))
        request.COOKIES = {'jwt': 'mock_token'}
        add_session_to_request(request)
        
        # Call the view
        response = checkout_obat(request, self.obat.id, 2)
        
        # Assertions
        self.assertEqual(response.status_code, 302)  # Redirect to OTP page
        self.assertEqual(response.url, reverse('beli_obat:otp_view'))
        
        # Check if session data is set correctly
        expected_session_data = {
            'obat_id': str(self.obat.id),
            'quantity': 2,
            'total_biaya': float(self.obat.harga) * 2,
        }
        session_data = request.session.get('pending_transaction')
        self.assertIsNotNone(session_data)
        self.assertEqual(session_data['obat_id'], expected_session_data['obat_id'])
        self.assertEqual(session_data['quantity'], expected_session_data['quantity'])
        self.assertEqual(session_data['total_biaya'], expected_session_data['total_biaya'])

@override_settings(SECRET_KEY='django-test-insecure-key')
class OtpViewTests(ViewTestsMixin, TestCase):
    @patch('beli_obat.views.validate_jwt_and_get_user')
    @patch('pyotp.TOTP')
    @patch('beli_obat.views.send_mail')  # Patch the actual module where send_mail is imported
    def test_otp_view_authenticated_with_pending_transaction(self, mock_send_mail, mock_totp, mock_validate):
        """Test otp_view with authenticated user and pending transaction"""
        # Setup mocks
        mock_validate.side_effect = self.mock_validate_jwt_success
        mock_totp_instance = MagicMock()
        mock_totp_instance.now.return_value = '123456'
        mock_totp_instance.secret = 'mock_secret'
        mock_totp.return_value = mock_totp_instance
        mock_send_mail.return_value = 1  # This indicates success
        
        # Set JWT cookie
        self.client.cookies['jwt'] = 'mock_token'
        
        # Setup session with pending transaction
        session = self.client.session
        session['pending_transaction'] = {
            'obat_id': str(self.obat.id),
            'quantity': 2,
            'total_biaya': 20000,
        }
        session.save()
        
        # Call the view
        response = self.client.get(reverse('beli_obat:otp_view'))
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'otp.html')
        
        # Verify email was sent (no need to check exact parameters)
        mock_send_mail.assert_called_once()

@override_settings(SECRET_KEY='django-test-insecure-key')
class VerifyOtpTests(ViewTestsMixin, TestCase):
    @patch('beli_obat.views.validate_jwt_and_get_user')
    @patch('pyotp.TOTP')
    def test_verify_otp_valid(self, mock_totp, mock_validate):
        """Test verify_otp with a valid OTP"""
        # Setup mocks
        mock_validate.side_effect = self.mock_validate_jwt_success
        mock_totp_instance = MagicMock()
        mock_totp_instance.verify.return_value = True
        mock_totp.return_value = mock_totp_instance
        
        # Create request with session and post data
        request = self.factory.post(reverse('beli_obat:verify_otp'), {
            'otp1': '1', 'otp2': '2', 'otp3': '3', 'otp4': '4', 'otp5': '5', 'otp6': '6'
        })
        request.COOKIES = {'jwt': 'mock_token'}
        add_session_to_request(request)
        add_message_storage_to_request(request)
        
        # Setup session data
        request.session['pending_transaction'] = {
            'obat_id': str(self.obat.id),
            'quantity': 2,
            'total_biaya': 20000,
        }
        request.session['otp_secret_key'] = 'mock_secret'
        
        # Set OTP valid time (5 minutes from now)
        from datetime import datetime, timedelta
        valid_time = datetime.now() + timedelta(minutes=5)
        request.session['otp_valid_time'] = str(valid_time)
        
        # Call the view
        response = verify_otp(request)
        
        # Assertions
        self.assertEqual(response.status_code, 302)  # Redirect to home
        self.assertEqual(response.url, reverse('main:home'))
        
        # Check if TransaksiPembelianObat was created
        self.assertEqual(TransaksiPembelianObat.objects.count(), 1)
        transaksi = TransaksiPembelianObat.objects.first()
        self.assertEqual(transaksi.user_id, UUID(self.mock_user_data['id']))
        self.assertEqual(transaksi.obat, self.obat)
        self.assertEqual(transaksi.quantity, 2)
        self.assertEqual(transaksi.total_biaya, 20000)
        
        # Check if Obat stok was updated
        self.obat.refresh_from_db()
        self.assertEqual(self.obat.stok, 98)  # 100 - 2
        
        # Check if session data was cleared
        self.assertNotIn('pending_transaction', request.session)
        self.assertNotIn('otp_secret_key', request.session)
        self.assertNotIn('otp_valid_time', request.session)

@override_settings(SECRET_KEY='django-test-insecure-key')
class ViewRiwayatPembelianObatTests(ViewTestsMixin, TestCase):
    @patch('beli_obat.views.validate_jwt_and_get_user')
    def test_view_riwayat_pembelian_obat_authenticated(self, mock_validate):
        """Test view_riwayat_pembelian_obat with authenticated user"""
        # Setup mock for validate_jwt_and_get_user
        user_id = uuid4()
        mock_user_data = {
            'id': str(user_id),
            'username': 'testuser',
            'email': 'test@example.com',
        }
        mock_validate.return_value = (mock_user_data, None)
        
        # Create test transaksi for the user
        TransaksiPembelianObat.objects.create(
            user_id=user_id,
            obat=self.obat,
            quantity=2,
            total_biaya=20000
        )
        
        # Set JWT cookie
        self.client.cookies['jwt'] = 'mock_token'
        
        # Call the view
        response = self.client.get(reverse('beli_obat:view_riwayat_pembelian_obat'))
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'riwayat_pembelian_obat.html')
        self.assertIn('list_transaksi', response.context)
        self.assertEqual(len(response.context['list_transaksi']), 1)
        self.assertTrue(response.context['is_authenticated'])
        self.assertEqual(response.context['user'], mock_user_data)