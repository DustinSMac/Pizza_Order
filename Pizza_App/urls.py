from django.urls import path
from .views import *


urlpatterns = [
    path('',index),
    path('main',main),
    path('register',register),
    path('login',login),
    path('order',order),
    path('logout',logout),
    path('checkout',checkout),
    path('account',account),
    path('purchase',purchase),
    path('update',update),
    path('reorder',reorder),
    path('cancel',cancel),
    path('submitorder',submitorder),
]
