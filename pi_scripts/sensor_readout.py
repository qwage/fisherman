import requests
import json

import time
import board
import adafruit_dht
import RPi.GPIO as gpio

dhtDevice = adafruit_dht.DHT11(board.D4, use_pulseio=False)
print(dhtDevice)
for i in range(4):
    try:
        # Print the values to the serial port
        temperature_c = dhtDevice.temperature
        temperature_f = temperature_c * (9 / 5) + 32
        humidity = dhtDevice.humidity
        print(
            "Temp: {:.1f} F / {:.1f} C    Humidity: {}% ".format(
                temperature_f, temperature_c, humidity
            )
        )
    except RuntimeError as error:
        # Errors happen fairly often, DHT's are hard to read, just             #        keep going
        print(error.args[0])
        time.sleep(2.0)
        continue
    except Exception as error:
        dhtDevice.exit()
        raise error

    time.sleep(2.0)

gpio.cleanup()

#
# # The actual POST request function
# def post_data(temperature, humidity):
#     url = 'http://your-django-app.com/api/sensor-update/'
#     headers = {'Content-Type': 'application/json'}  # Set the content type to application/json
#     data = json.dumps({'temperature': temperature, 'humidity': humidity})
#     response = requests.post(url, headers=headers, data=data)
#     print(response.text)
#
#
# if __name__ == '__main__':
#     temperature, humidity = read_temperature_and_humidity()
#     post_data(temperature, humidity)
