from ninja import NinjaAPI, Schema
from .models import SensorModel

api = NinjaAPI(
    description='<a href="/">Go to Homepage</a>'
)


class SensorData(Schema):
    temperature: float


@api.post("/temperature-update")
def update_sensor_data(request, data: SensorData):
    SensorModel.objects.create(temperature=data.temperature)
    return {"status": "success", "data_received": data.dict()}
