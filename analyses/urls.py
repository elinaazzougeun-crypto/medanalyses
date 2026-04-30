from django.urls import path
from . import views

urlpatterns = [

    # 🏠
    path('', views.home, name='home'),

    # 🔐 auth
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # 📊 dashboard
    path('dashboard/', views.dashboard, name='dashboard'),

    # 👨‍⚕️ patients
    path('patients/', views.patients, name='patients'),
    path('patients/add/', views.add_patient, name='add_patient'),
    path('patients/edit/<int:id>/', views.edit_patient, name='edit_patient'),
    path('patients/delete/<int:id>/', views.delete_patient, name='delete_patient'),
    path('patients/<int:id>/', views.detail_patient, name='detail_patient'),

    # 🧪 analyses
    path('analyses/', views.analyses, name='analyses'),
    path('analyses/add/', views.add_analyse, name='add_analyse'),
    path('analyses/edit/<int:id>/', views.edit_analyse, name='edit_analyse'),
    path('analyses/delete/<int:id>/', views.delete_analyse, name='delete_analyse'),
]