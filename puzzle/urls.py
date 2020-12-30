from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('solution/', views.solution, name='index'),
    path('template/', views.template, name='template'),
    path('restart/', views.restart, name='restart'),
    path('upload/', views.upload, name='upload'),
    path('categories/', views.categories, name='categories'),
    path('categories/<int:category_id>/', views.results),
    path('answers/', views.answers, name='answers'),
    path('answers/<str:answer>/', views.answer_results),
    path('tool/', views.tool, name='tool'),
    path('settings/', views.settings, name='settings'),
    path('cells/', views.cells, name='cells'),
    path('cells/<int:cell_id>/', views.cell),
    path('old_solutions/', views.old_solutions, name='old_solutions'),
]