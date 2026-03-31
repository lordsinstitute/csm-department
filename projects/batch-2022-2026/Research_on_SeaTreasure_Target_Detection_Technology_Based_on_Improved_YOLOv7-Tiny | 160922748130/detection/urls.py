from django.urls import path
from . import views

app_name = "detection"

urlpatterns = [
    path("live/",                  views.live_view,      name="live"),
    path("video_feed/",            views.video_feed,     name="video_feed"),
    path("video_frame/",           views.video_frame,    name="video_frame"),
    path("benchmark_live_frame/",  views.benchmark_live_frame, name="benchmark_live_frame"),
    path("upload/",                 views.upload_view,    name="upload"),
    path("process/<int:job_id>/",   views.process_view,   name="process"),
    path("result/<int:job_id>/",    views.result_view,    name="result"),
    path("history/",                views.history_view,   name="history"),
    path("metrics/",                views.metrics_view,   name="metrics"),
    path("download/<int:job_id>/",  views.download_result, name="download"),
    path("delete/<int:job_id>/",    views.delete_job,     name="delete"),
]
