from django.db import models
from django.contrib.auth.models import User

class TemperatureReading(models.Model):
    sensor_id = models.CharField(max_length=100, default='sensor_001')
    temperature = models.FloatField()
    humidity = models.FloatField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    device = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"Temp: {self.temperature}°C at {self.timestamp}"