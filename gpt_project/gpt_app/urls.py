from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns =[
    path("", views.home, name='home'),
    path("home/", views.home, name='home'),
    path("login/", views.login_view, name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('logout_template/', views.logout_template_view, name='logout_template'),
    path("chatbot/", views.chatbot, name='chatbot'),
    path('upload_csv/', views.upload_csv, name='upload_csv'),
]