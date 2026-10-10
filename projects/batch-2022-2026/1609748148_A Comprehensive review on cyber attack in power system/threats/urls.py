from django.urls import path
from . import views

app_name = 'threats'

urlpatterns = [
    path('', views.threat_list, name='list'),
    path('<int:pk>/', views.threat_detail, name='detail'),
    path('vulnerabilities/', views.vulnerability_list, name='vulnerabilities'),
    path('assets/', views.asset_list, name='assets'),
    path('asset-risk/', views.asset_risk_overview, name='asset_risk'),
]