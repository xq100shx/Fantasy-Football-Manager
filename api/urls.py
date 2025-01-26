from django.urls import path
from .views import save_squad, check_existing_squad

urlpatterns = [
    path('save_squad/', save_squad, name='save_squad'),
    path('check_existing_squad/', check_existing_squad, name='check_existing_squad'),
    # other paths
]