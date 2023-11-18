from django.db import models


class SensorModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)  # use auto_now_add for the creation timestamp
    temperature = models.FloatField()

    def __str__(self):
        return f"Sensor reading at {self.id} is {self.temperature} degrees"

    class Meta:  # 'Meta' should be capitalized
        db_table = 'sensor_data'
