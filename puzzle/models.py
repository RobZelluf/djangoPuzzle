import os
import json

from django.db import models
from django import forms

# Create your models here.


def clear_files():
    for file in os.listdir("excel_files"):
        os.remove(os.path.join("excel_files", file))


class UploadFile(models.Model):
    files = models.FileField(upload_to="excel_files/", blank=True, default=None, null=True)


class UploadCategories(models.Model):
    categories = models.TextField()


class UploadSettings(models.Model):
    # mode = models.TextField(help_text="normal/reverse/random")

    MODE_CHOICES = (
        ('normal', 'normal'),
        ('reverse', 'reverse'),
        ('random', 'random')
    )

    ALGORITHM_CHOICES = (
        ('bfs', 'bfs'),
        ('dfs', 'dfs')
    )

    with open("brabant_puzzle/settings.txt", "r") as f:
        settings = json.load(f)

    mode = models.CharField(max_length=10, choices=MODE_CHOICES, default=settings["mode"])
    algorithm = models.CharField(max_length=4, choices=ALGORITHM_CHOICES, default=settings["algorithm"])