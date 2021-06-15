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
    path('post',post),
    path('comment/<int:id>',comment),
    path('like/<int:id>',like),
    path('partialpost/<int:id>',partialpost),
    path('thewall',thewall),
]
