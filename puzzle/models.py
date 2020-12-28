import os

from django.db import models

# Create your models here.
def clear_files():
    for file in os.listdir("excel_files"):
        os.remove(os.path.join("excel_files", file))


class UploadFile(models.Model):
    files = models.FileField(upload_to="excel_files/", blank=True, default=None, null=True)


class UploadCategories(models.Model):
    categories = models.TextField()