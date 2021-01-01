from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('puzzle/', include('puzzle.urls')),
    path('puzzle2/', include('puzzle2.urls')),
    path('admin/', admin.site.urls),
]