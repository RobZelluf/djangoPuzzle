from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('solution/', views.solution, name='index'),
    path('upload/', views.upload, name='upload'),
    path('categories/', views.categories, name='categories'),
    path('categories/<int:category_id>/', views.results),
    path('answers/', views.answers, name='answers'),
    path('answers/<str:answer>/', views.answer_results),
    path('tool/', views.tool, name='tool'),
]