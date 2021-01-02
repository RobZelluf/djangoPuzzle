from django.urls import path
from django.views.generic import TemplateView

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('solution/', views.solution, name='index'),
    path('template/', views.template, name='template'),
    path('terminal/', views.terminal, name='terminal'),
    path('heatmap/', views.heatmap, name='heatmap'),
    path('superheatmap/', views.superheatmap, name='superheatmap'),
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
    path('finished_solutions/', views.finished_solutions, name='finished_solutions'),
    path('clear_cells/', views.clear_cells, name='clear_cells'),
]