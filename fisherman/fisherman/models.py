from django.db import models


class SensorModel(models.Model):
    created = models.DateTimeField(auto_now=True)
    temperature = models.FloatField()

    def __str__(self):
        return f"Sensor reading at {self.id} is {self.temperature} degrees"
