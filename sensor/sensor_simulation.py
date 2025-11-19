import random
import threading
import time
from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()


class TemperatureSensor:
    def __init__(self, interval=600):
        self.interval = interval
        self.running = False
        self.thread = None

    def start(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._simulate, daemon=True)
            self.thread.start()

    def stop(self):
        self.running = False

    def _simulate(self):
        from .models import TemperatureReading

        current_temp = 20.0

        while self.running:
            try:
                change = random.uniform(-0.5, 0.5)
                current_temp += change
                current_temp = max(15.0, min(35.0, current_temp))
                humidity = random.uniform(40, 80)

                TemperatureReading.objects.create(
                    sensor_id='sensor_001',
                    temperature=round(current_temp, 2),
                    humidity=round(humidity, 2)
                )

                time.sleep(self.interval)
            except Exception as e:
                print(f"Błąd symulatora: {e}")
                time.sleep(self.interval)


sensor = TemperatureSensor(interval=600)