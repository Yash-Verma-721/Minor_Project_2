from django.urls import path
from django.conf.urls.static import static
from django.conf import settings

from . import views

urlpatterns = [
    path('', views.landing, name='landing'),
    path('home/', views.home, name='home'),
    path('login/', views.user_login, name='login'),
    path('signup/', views.signup, name='signup'),
    path('userhome/', views.userhome, name='userhome'),
    path('sharenotes/', views.sharenotes),
    path("viewnotes/", views.viewnotes),
    path("generate-link/<int:id>/", views.generate_link),
    path("shared/<uuid:token>/", views.shared_file),
    path('cpuser/', views.cpuser),
    path("delete-note/<int:id>/", views.delete_note),
    path('myadmin/', views.adminhome),
    path('cpadmin/', views.cpadmin),
    path('manageusers/', views.manageusers),
    path('manageuserstatus/', views.manageuserstatus),
    path('verify/', views.verify),
    path('contact/', views.contact),
    

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

##################################################################
# You originally assumed:

# encryption alone makes system secure

# Wrong.

# Right now:

# encryption key stored in DB

# server decrypts automatically

# So whoever gets token → gets file.

# Real systems separate keys per receiver.

# But for minor project level, this is already above 90% submissions.