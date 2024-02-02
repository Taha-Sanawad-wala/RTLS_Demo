from django.contrib import admin
from django.urls import path
from rtlsapp.views import materialRequestScreen, index,deliveryStatusTracker,start_background,stop_background,kPI
urlpatterns = [
    path('',index),
    path('materialrequestscreen/',materialRequestScreen),
    path('deliverystatustracker/',deliveryStatusTracker),
    path('startbackground/',start_background),
    path('stopbackground/',stop_background),
    path('kpi/',kPI),
]