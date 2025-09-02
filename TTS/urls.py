from django.urls import path
from TTS import views
urlpatterns =[
    path('',views.loginpage,name='login'),
    path('register/',views.registerpage,name='register'),
    path('home/',views.home,name='home'),
    path('result/', views.result, name='result'),
    path("result2/", views.result2, name="result2"),



]