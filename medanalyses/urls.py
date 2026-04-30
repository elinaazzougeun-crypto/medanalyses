from django.contrib import admin
from django.urls import path
from analyses import views

urlpatterns = [
    path('admin/', admin.site.urls),

    # Pages principales
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('analyses/', views.analyses, name='analyses'),
    path('patients/', views.patients, name='patients'),

    # Auth
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]