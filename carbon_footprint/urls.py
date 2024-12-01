from django.urls import path
from django.contrib import admin
from django.urls import path 
from .views import signup_view, login_view, logout_view, profile_view, ride_results, record_ride

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Authentication URLs
    path('signup/', signup_view, name='signup'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('profile/', profile_view, name='profile'),
    
    # Carbon Tracker URLs
    path('', record_ride, name='record_ride'),
    path('results/<int:ride_id>/',ride_results, name='ride_results'),
]