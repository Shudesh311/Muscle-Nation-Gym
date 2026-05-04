from django.contrib import admin
from django.http import HttpResponse
from django.urls import path
from .views import login_view
from .views import admin_create
from .views import admin_login
from .views import create_admission
from .views import list_admissions
from .views import delete_admission
from .views import update_admission_photo
from .views import add_gym_fee, list_gym_fees, delete_gym_fee, search_admission
from django.conf import settings
from django.conf.urls.static import static

def home(request):
    return HttpResponse("Backend is running")

urlpatterns = [
    path("", home),
    path("api/login/", login_view),
    path('admin/create/', admin_create),
    path("admin/login/", admin_login),
    path('admin/', admin.site.urls),
    path("admission/create/", create_admission),
    path("admission/list/", list_admissions),
    path("admission/delete/<int:admission_id>/", delete_admission),
    path('admission/update-photo/<int:admission_id>/', update_admission_photo),
    path("fees/add/", add_gym_fee),
    path("fees/list/", list_gym_fees),
    path("fees/delete/<int:fee_id>/", delete_gym_fee),
    path("search-admission/", search_admission, name="search-admission")

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
