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

    MODE_CHOICES = (
        ('normal', 'normal'),
        ('reverse', 'reverse'),
        ('random', 'random')
    )

    ALGORITHM_CHOICES = (
        ('bfs', 'bfs'),
        ('dfs', 'dfs'),
        ('a-star', 'a-star'),
        ('b-star', 'b-star'),
        ('c-star', 'c-star')
    )

    SELF_FILLED_CHOICES = (
        ('True', 'True'),
        ('False', 'False')
    )

    with open("brabant_puzzle/settings.txt", "r") as f:
        settings = json.load(f)

    mode = models.CharField(max_length=10, choices=MODE_CHOICES, default=settings["mode"])
    algorithm = models.CharField(max_length=6, choices=ALGORITHM_CHOICES, default=settings["algorithm"])
    timeout = models.TextField(max_length=100, default=settings["timeout"])
    use_self_filled = models.CharField(max_length=10, choices=SELF_FILLED_CHOICES, default=settings["use_self_filled"])


class UpdateCell(models.Model):
    answer = models.CharField(max_length=100)