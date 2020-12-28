from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('puzzle/', include('puzzle.urls')),
    path('admin/', admin.site.urls),
]