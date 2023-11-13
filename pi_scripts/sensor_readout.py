import requests
import json

import time
import board
import adafruit_dht
import RPi.GPIO as gpio


def get_temperature_and_humidity(device: adafruit_dht):
    try:
        temperature_c = device.temperature
        temperature_f = temperature_c * (9 / 5) + 32
        humidity = device.humidity
        return temperature_f, humidity
    except RuntimeError as _:
        return None, None, None
    except Exception as _:
        device.exit()
        return False


# The actual POST request function
def post_data(temperature):
    url = 'http://127.0.0.1:8000/api/temperature-update/'
    headers = {'Content-Type': 'application/json'}  # Set the content type to application/json
    data = json.dumps({'temperature': temperature})
    response = requests.post(url, headers=headers, data=data)
    print(response.text)


if __name__ == '__main__':
    dhtDevice = adafruit_dht.DHT22(board.D4, use_pulseio=False)
    for i in range(4):
        temperature_f, humidity = get_temperature_and_humidity(dhtDevice)
        print(f'Temperature: {temperature_f}\nHumidity: {humidity}\n')
        post_data(temperature_f)
        time.sleep(2.0)

    # post_data(temperature, humidity)
    gpio.cleanup()
