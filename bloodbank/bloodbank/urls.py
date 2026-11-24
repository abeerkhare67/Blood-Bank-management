
from django.contrib import admin
from django.urls import path

from bank.views import (
    home,
    queue_view,
    add_request,
    dequeue_request,
    peek_request,
    stock_view,
    donation_history,
    donation_form,
    record_donation,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('queue/', queue_view, name='queue'),
    path('request/', add_request, name='add_request'),
    path('dequeue/', dequeue_request, name='dequeue'),
    path('peek/', peek_request, name='peek'),
    path('stock/', stock_view, name='stock'),

    # New donation features
    path('donations/', donation_history, name='donation_history'),
    path('donations/add/', donation_form, name='donation_form'),
    path('donations/record/', record_donation, name='record_donation'),
]
