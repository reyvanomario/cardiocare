from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch
from django.http import HttpResponseForbidden
import update_kuota.views as views

from book_konsultasi.models import RumahSakit, Dokter, JadwalKonsultasi
import uuid

views.HttpResponseForbidden = HttpResponseForbidden

class UpdateKuotaViewTests(TestCase):
    def setUp(self):
        self.client = Client()

        self.rs = RumahSakit.objects.create(
            nama_rumah_sakit="RS Test",
            alamat_rumah_sakit="Jalan Sehat",
            no_telp="08123456789"
        )
        self.dokter = Dokter.objects.create(
            nama_dokter="Dr. Sehat",
            rumah_sakit=self.rs
        )
        self.jadwal = JadwalKonsultasi.objects.create(
            dokter=self.dokter,
            hari="Senin",
            jam_mulai="09:00",
            jam_selesai="11:00",
            kuota=10
        )

        self.jwt_token = "dummy.jwt.token"
        self.client.cookies['jwt'] = self.jwt_token  

    @patch("update_kuota.views.validate_jwt_and_get_user")
    def test_redirect_if_token_missing(self, mock_validate):
        # Clearing cookie to simulate missing token
        self.client.cookies.clear()
        response = self.client.get(reverse('update_kuota:list_dokter'))
        self.assertEqual(response.status_code, 302)
        self.assertIn("login", response.url)

    @patch("update_kuota.views.validate_jwt_and_get_user")
    def test_list_dokter_success(self, mock_validate):
        mock_validate.return_value = ({"is_admin": True}, None)
        response = self.client.get(reverse('update_kuota:list_dokter'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Dr. Sehat")

    @patch("update_kuota.views.validate_jwt_and_get_user")
    def test_update_kuota_success(self, mock_validate):
        mock_validate.return_value = ({"is_admin": True}, None)
        url = reverse('update_kuota:update_kuota', args=[str(self.dokter.id_dokter)]) 
        response = self.client.post(
            url,
            data={'kuota': '15'}
        )
        self.assertRedirects(response, reverse('update_kuota:list_dokter'))
        self.jadwal.refresh_from_db()
        self.assertEqual(self.jadwal.kuota, 15)

    @patch("update_kuota.views.validate_jwt_and_get_user")
    def test_update_kuota_invalid_token(self, mock_validate):
        mock_validate.return_value = (None, HttpResponseForbidden("Token invalid"))
        url = reverse('update_kuota:update_kuota', args=[str(self.dokter.id_dokter)]) 
        response = self.client.post(url, data={'kuota': '15'})
        self.assertEqual(response.status_code, 403)

    @patch("update_kuota.views.validate_jwt_and_get_user")
    def test_update_kuota_non_admin_forbidden(self, mock_validate):
        mock_validate.return_value = ({"is_admin": False}, None)
        url = reverse('update_kuota:update_kuota', args=[str(self.dokter.id_dokter)]) 
        response = self.client.post(url, data={'kuota': '15'})
        self.assertEqual(response.status_code, 403)

    @patch("update_kuota.views.validate_jwt_and_get_user")
    def test_update_kuota_invalid_kuota_value(self, mock_validate):
        mock_validate.return_value = ({"is_admin": True}, None)
        url = reverse('update_kuota:update_kuota', args=[str(self.dokter.id_dokter)]) 
        response = self.client.post(url, data={'kuota': '-10'})
        self.jadwal.refresh_from_db()
        self.assertEqual(self.jadwal.kuota, 10) 
        self.assertRedirects(response, reverse('update_kuota:list_dokter'))
