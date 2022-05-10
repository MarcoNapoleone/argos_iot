from itertools import count

import datetime
import random
import requests
import uuid
import socket
import json
import Adafruit_DHT

from config import print_env

DHT_SENSOR = Adafruit_DHT.DHT22
DHT_PIN = 4
SERVICE_URL = 'https://incomunicando.it/webservice/getdata.php'
LAST_READING = datetime.datetime.now() - datetime.timedelta(0, 300)  # now - 5 min
NEXT_READING_DELTA = 5  # seconds


def get_mac():
    return hex(uuid.getnode())


def get_local_ip():
    return socket.gethostbyname(socket.gethostname() + ".local")


def get_sensor_data():
    humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)

    """
    :tipo_sensore:
        "temp" -> temperatura |
        "hum" -> umidita |
        "bpt" -> pressione atmosferica |
        "aqi" -> qualita aria,
    :return:
        {"sensore": tipo_sensore, valore: string, um: string}
    """


    return [
        {"sensore": "temp", "valore": temperature, "um": "C"},
        {"sensore": "hum", "valore": humidity, "um": "%"},
        {"sensore": "bpt", "valore": random.randint(9500, 10300) / 10, "um": "hPa"},
        {"sensore": "aqi", "valore": random.randint(10, 6000) / 10, "um": "AQI"}
    ]


def get_payload():
    return {
        "id": "25555",
        "dispositivo": {
            "mac": get_mac(),
            "ip": get_local_ip()
        },
        "datiRilevazione": get_sensor_data(),
        "tempoRilevazione": datetime.datetime.now().strftime("%Y-%m-%d (%H:%M:%S.%f)")
    }


def send_data(data, times):
    if times > 0:
        try:
            response = requests.put(SERVICE_URL, json=data)
            return response
        except requests.exceptions.Timeout:
            send_data(data, times - 1)
        except requests.exceptions.TooManyRedirects:
            print('error 404')
        except requests.exceptions.RequestException as e:
            print(e)


def main():
    global LAST_READING
    global NEXT_READING_DELTA
    error = 0

    while not error:
        # if time from last reading is bigger than delta
        if datetime.datetime.now() > LAST_READING + datetime.timedelta(0, NEXT_READING_DELTA):
            response = send_data(get_payload(), 2).text  # todo handle errors
            if response is not None:
                print(response)
                data = json.loads(response)
                LAST_READING = datetime.datetime.now()
                if data['status']:
                    NEXT_READING_DELTA = int(data['data']['prossimaRilvazione'])
                else:
                    print('status error')
            else:
                print('error no response')


if __name__ == "__main__":
    print_env()
    main()
