from django.urls import path
from . import views

app_name = "datasets"

urlpatterns = [
    path("",                  views.dataset_list,   name="list"),
    path("<int:pk>/",         views.dataset_detail, name="detail"),
    path("upload/",           views.dataset_upload, name="upload"),
    path("<int:pk>/delete/",  views.dataset_delete, name="delete"),
]
