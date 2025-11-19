from rest_framework import serializers
from .models import TemperatureReading

class TemperatureReadingSerializer(serializers.ModelSerializer):
    class Meta:
        model = TemperatureReading
        fields = ['id', 'sensor_id', 'temperature', 'humidity', 'timestamp']
        read_only_fields = ['id', 'timestamp']