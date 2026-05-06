from django.urls import path
from . import views

urlpatterns = [

    path('register/', views.RegisterUser.as_view(), name='register'),
    path('login/', views.LoginUser.as_view(), name='loginUser'),
    path('edit-profile/', views.EditProfile.as_view(), name='editProfile'),
    path('logout/', views.LogoutUser.as_view(), name='logout'),
    path('document-status/', views.DocumentStatus.as_view(), name='documentStatus'),
    path('request-document/', views.RequestDocument.as_view(), name='requestDocument'),
    path('user-analytics/', views.UserAnalytics.as_view(), name='userAnalytics'),
    path('dashboard/', views.Dashboard.as_view(), name='dashboard'),
    path('submit-survey/<int:document_id>/', views.SubmitSurvey.as_view(), name='submitSurvey'),
    path('help/', views.HelpFAQ.as_view(), name='helpFAQ'),
    path('book-appointment/', views.BookAppointment.as_view(), name='bookAppointment'),
    path('my-appointments/', views.MyAppointments.as_view(), name='myAppointments'),
    path('appointments-dashboard/', views.AppointmentDashboard.as_view(), name='appointmentDashboard'),
    path('appointment-survey/<int:appointment_id>/',views.SubmitAppointmentSurvey.as_view(),name='appointmentSurvey'),
]