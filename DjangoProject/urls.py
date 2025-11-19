
from django.contrib import admin
from django.urls import path, include
from sensor.views import login_view, dashboard_view, logout_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('', login_view, name='home'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('sensor/', include('sensor.urls')),
    path('logout/', logout_view, name='logout'),

]
