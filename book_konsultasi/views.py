from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from django.db.models import F
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404, render
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.utils import timezone
from django.views.decorators.http import require_http_methods
import bleach
from .models import BookKonsultasi, JadwalKonsultasi, Dokter, RumahSakit
from .serializers import BookKonsultasiSerializer
from .rate_limiting import RateLimitMixin
from uuid import UUID
import logging
from django.db import transaction
from django.http import JsonResponse
import os
import csv

logger = logging.getLogger(__name__)

HARI_URUTAN = {
    'Senin': 1,
    'Selasa': 2,
    'Rabu': 3,
    'Kamis': 4,
    'Jumat': 5,
    'Sabtu': 6,
    'Minggu': 7
}

def sanitize_input(input_string):
    if input_string is None:
        return None
    return bleach.clean(str(input_string), strip=True)

def validate_uuid(uuid_value):
    if isinstance(uuid_value, UUID):
        return True
    if isinstance(uuid_value, str):
        try:
            UUID(uuid_value.strip())
            return True
        except (ValueError, AttributeError, TypeError):
            return False
    return False


@require_http_methods(["GET"])
def list_dokter(request, id_rumah_sakit):
    if not validate_uuid(id_rumah_sakit):
        messages.error(request, 'ID rumah sakit tidak valid')
        return redirect('book_konsultasi:list_rumah_sakit')
        
    try:
        rumah_sakit = get_object_or_404(RumahSakit, id_rumah_sakit=id_rumah_sakit)
        dokter = Dokter.objects.filter(rumah_sakit=rumah_sakit)
        dokter_with_jadwal = []

        for d in dokter:
            jadwal_list = JadwalKonsultasi.objects.filter(dokter=d)
            sorted_jadwal = sorted(
                jadwal_list,
                key=lambda j: (HARI_URUTAN.get(j.hari, 999), j.jam_mulai)
            )
            jadwal = sorted_jadwal[0] if sorted_jadwal else None
            dokter_with_jadwal.append({
                'dokter': d,
                'jadwal': jadwal
            })

        if dokter_with_jadwal:
            context = {
                'dokter': dokter_with_jadwal,
                'rumah_sakit': rumah_sakit,
            }
            return render(request, 'list_dokter.html', context)
        else:
            messages.error(request, f'Tidak ada dokter yang ditemukan di rumah sakit "{rumah_sakit.nama_rumah_sakit}".')
            return redirect('book_konsultasi:list_rumah_sakit')
    except Exception as e:
        logger.error(f"Error in list_dokter: {str(e)}")
        messages.error(request, 'Terjadi kesalahan. Silakan coba lagi nanti.')
        return redirect('book_konsultasi:list_rumah_sakit')


@require_http_methods(["GET"])
def list_rumah_sakit(request):
    try:
        query = sanitize_input(request.GET.get('q', ''))
        
        try:
            page = int(request.GET.get('page', 1))
            if page < 1:
                page = 1
        except (ValueError, TypeError):
            page = 1
        
        rumah_sakit_list = RumahSakit.objects.all().order_by('nama_rumah_sakit')
        
        if query:
            rumah_sakit_list = rumah_sakit_list.filter(nama_rumah_sakit__icontains=query)
        
        paginator = Paginator(rumah_sakit_list, 8)
        
        try:
            rumah_sakit_page = paginator.page(page)
        except PageNotAnInteger:
            rumah_sakit_page = paginator.page(1)
        except EmptyPage:
            rumah_sakit_page = paginator.page(paginator.num_pages)
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            try:
                data = [
                    {
                        'id': str(rs.id_rumah_sakit),
                        'nama': rs.nama_rumah_sakit,
                    }
                    for rs in rumah_sakit_page
                ]
                return JsonResponse({
                    'data': data, 
                    'has_next': rumah_sakit_page.has_next(),
                    'current_page': rumah_sakit_page.number,
                    'total_pages': paginator.num_pages
                })
            except Exception as e:
                logger.error(f"AJAX error in list_rumah_sakit: {str(e)}")
                return JsonResponse({'data': [], 'has_next': False, 'current_page': 1, 'total_pages': 1})
        
        context = {
            'rumah_sakit_list': rumah_sakit_page,
            'query': query,
        }
        
        return render(request, 'list_rumah_sakit.html', context)
    except Exception as e:
        logger.error(f"Error in list_rumah_sakit: {str(e)}")
        messages.error(request, 'Terjadi kesalahan. Silakan coba lagi nanti.')
        return render(request, 'list_rumah_sakit.html', {'rumah_sakit_list': [], 'query': ''})


@require_http_methods(["GET"])
def view_dokter(request, id_dokter):
    try:
        if not validate_uuid(id_dokter):
            messages.error(request, 'ID dokter tidak valid')
            return redirect('book_konsultasi:list_rumah_sakit')
            
        dokter = get_object_or_404(Dokter, id_dokter=id_dokter)

        context = {
            'dokter': dokter,
        }
        return render(request, 'view_dokter.html', context)
    except Exception as e:
        logger.error(f"Error in view_dokter: {str(e)}")
        messages.error(request, 'Terjadi kesalahan. Silakan coba lagi nanti.')
        return redirect('book_konsultasi:list_rumah_sakit')
    

@require_http_methods(["GET"])
def view_rumah_sakit(request, id_rumah_sakit):
    try:
        if not validate_uuid(id_rumah_sakit):
            messages.error(request, 'ID rumah sakit tidak valid')
            return redirect('book_konsultasi:list_rumah_sakit')
            
        rumah_sakit = get_object_or_404(RumahSakit, id_rumah_sakit=id_rumah_sakit)

        context = {
            'rumah_sakit': rumah_sakit,
        }
        return render(request, 'view_rumah_sakit.html', context)
    except Exception as e:
        logger.error(f"Error in view_rumah_sakit: {str(e)}")
        messages.error(request, 'Terjadi kesalahan. Silakan coba lagi nanti.')
        return redirect('book_konsultasi:list_rumah_sakit')

@method_decorator(csrf_protect, name='dispatch')
class BookKonsultasiView(RateLimitMixin, GenericAPIView):
    serializer_class = BookKonsultasiSerializer
    permission_classes = [IsAuthenticated]
    rate = '10/m'

    def get_queryset(self):
        return BookKonsultasi.objects.filter(id_pasien=self.request.user.id)

    def get(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            return Response({"data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error in BookKonsultasiView GET: {str(e)}")
            return Response(
                {"error": "Terjadi kesalahan. Silakan coba lagi nanti."}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def post(self, request, id_jadwal=None, *args, **kwargs):
        try:
            user = request.user

            if hasattr(user, 'role') and user.role != 'Pasien':
                return Response(
                    {"error": "Hanya pasien yang dapat booking konsultasi"}, 
                    status=status.HTTP_403_FORBIDDEN
                )

            jadwal_id = id_jadwal or request.data.get('jadwal')
            if not jadwal_id:
                return Response(
                    {"error": "ID jadwal diperlukan"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            if not validate_uuid(str(jadwal_id)):
                return Response(
                    {"error": "Format ID jadwal tidak valid"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            try:
                jadwal = JadwalKonsultasi.objects.get(id_jdwl_konsultasi=jadwal_id)
            except JadwalKonsultasi.DoesNotExist:
                return Response(
                    {"error": "Jadwal tidak ditemukan"}, 
                    status=status.HTTP_404_NOT_FOUND
                )

            if jadwal.kuota <= 0:
                return Response(
                    {"error": "Kuota konsultasi penuh"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            if BookKonsultasi.objects.filter(jadwal=jadwal, id_pasien=user.id).exists():
                return Response(
                    {"error": "Anda sudah memesan jadwal ini"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            with transaction.atomic():
                booking = BookKonsultasi.objects.create(
                    jadwal=jadwal,
                    id_pasien=user.id,
                    tanggal_pemesanan=timezone.now().date()
                )

                jadwal.kuota = F('kuota') - 1
                jadwal.save()
                jadwal.refresh_from_db()
                
                if jadwal.kuota < 0:
                    transaction.set_rollback(True)
                    return Response(
                        {"error": "Kuota konsultasi telah habis"}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )

            serializer = self.get_serializer(booking)
            return Response({
                "data": serializer.data, 
                "message": "Konsultasi berhasil dipesan"
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Error in BookKonsultasiView POST: {str(e)}")
            return Response(
                {"error": "Terjadi kesalahan. Silakan coba lagi nanti."}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        

def import_csv_rumahsakit():
    with open('dataset/rs.csv', mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            RumahSakit.objects.create(
                nama_rumah_sakit=row['nama_rumah_sakit'],          
                alamat_rumah_sakit=row['alamat'],
                no_telp=row['nomor_telepon'],
            )

def import_csv_dokter():
    with open('dataset/dokter.csv', mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            rumah_sakit = RumahSakit.objects.get(nama_rumah_sakit=row['nama_rumah_sakit'])
            Dokter.objects.create(         
                nama_dokter=row['nama_dokter'],
                rumah_sakit=rumah_sakit,
            )



# def import_csv_jadwal():
#     with open('dataset/jadwal.csv', mode='r', encoding='utf-8') as file:
#         reader = csv.DictReader(file)
#         for row in reader:
#             nama_dokter = Dokter.objects.get(nama_rumah_sakit=row['nama_dokter'])
#             JadwalKonsultasi.objects.create(         
#                 nama_dokter=row['nama_dokter'],
#                 rumah_sakit=rumah_sakit,
#             )