from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [
    path("",               views.index,            name="index"),
    path("user/",          views.user_dashboard,   name="user_dashboard"),
    path("admin/",         views.admin_dashboard,  name="admin_dashboard"),
    path("users/",         views.user_management,  name="user_management"),
    path("users/<int:user_id>/toggle/", views.toggle_user_status, name="toggle_user"),
    path("users/<int:user_id>/role/",   views.change_user_role,   name="change_role"),
    path("monitor/",       views.system_monitor,   name="system_monitor"),
    path("performance/",   views.model_performance, name="model_performance"),
]
