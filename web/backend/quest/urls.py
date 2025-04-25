from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, {'lang': 'ru'}, name='index_ru'),
    path('ru/', views.index, {'lang': 'ru'}, name='index_ru'),
    path('en/', views.index, {'lang': 'en'}, name='index_en'),
]