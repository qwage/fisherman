# api.py

from ninja import NinjaAPI
from ninja import Schema

api = NinjaAPI()

class SensorData(Schema):
    temperature: float
    humidity: float

@api.post("/sensor-update")
def update_sensor_data(request, data: SensorData):
    # Save or process your data here...
    # You might want to save the data to your model
    # SensorModel.objects.create(temperature=data.temperature, humidity=data.humidity)
    return {"status": "success", "data_received": data.dict()}
