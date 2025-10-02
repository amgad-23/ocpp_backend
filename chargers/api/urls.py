from django.urls import path

from . import views

urlpatterns = [
    path("chargers/", views.list_chargers, name="list_chargers"),
    path("chargers/active/", views.list_active_chargers, name="list_active_chargers"),
    path("transactions/", views.list_transactions, name="list_transactions"),
    path("logs/", views.list_logs, name="list_logs"),
    path("chargers/<str:charger_id>/start/", views.remote_start, name="remote_start"),
    path("chargers/<str:charger_id>/stop/", views.remote_stop, name="remote_stop"),
]
