from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('report/<str:topic>/', views.generate_report, name='report'),
    path('pdf/<str:topic>/', views.generate_pdf_report, name='generate_pdf'),
]
