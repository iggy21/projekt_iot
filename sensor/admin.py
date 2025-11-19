from django.contrib import admin
from .models import TemperatureReading


@admin.register(TemperatureReading)
class TemperatureReadingAdmin(admin.ModelAdmin):
    list_display = ('sensor_id', 'temperature', 'humidity', 'timestamp')
    list_filter = ('sensor_id', 'timestamp')
    search_fields = ('sensor_id',)
    ordering = ('-timestamp',)

