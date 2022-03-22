import datetime
import random
import requests
import uuid
import socket
import json

service_url = 'https://incomunicando.it/webservice/getdata.php'
last_reading = datetime.datetime.now() - datetime.timedelta(0, 300)  # now - 5 min
next_reading_delta = 5  # seconds


def get_mac():
    return hex(uuid.getnode())


def get_local_ip():
    return socket.gethostbyname(socket.gethostname())


def get_sensor_data():
    """
    :tipo_sensore:
        "temp" -> temperatura |
        "hum" -> umiditò |
        "bpt" -> pressione atmosferica |
        "aqi" -> qualità aria,
    :return:
        {"sensore": tipo_sensore, valore: string, um: string}
    """
    return [
        {"sensore": "temp", "valore": random.randint(-50, 400) / 10, "um": "°C"},
        {"sensore": "hum", "valore": random.randint(100, 950) / 10, "um": "%"},
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
        "timeRilevazione": datetime.datetime.now().strftime("%Y-%m-%d (%H:%M:%S.%f)")
    }


def send_data(data, times):
    if times > 0:
        try:
            response = requests.put(service_url, json=data)
            return response
        except requests.exceptions.Timeout:
            send_data(data, times - 1)
        except requests.exceptions.TooManyRedirects:
            print('error 404')
        except requests.exceptions.RequestException as e:
            print(e)


def main():
    global last_reading
    global next_reading_delta
    error = 0

    while not error:
        # if time from last reading is bigger than delta
        if datetime.datetime.now() > last_reading + datetime.timedelta(0, next_reading_delta):
            response = send_data(get_payload(), 2).text  # todo handle errors
            if response:
                print(response)
                data = json.loads(response)
                last_reading = datetime.datetime.now()
                if data['status']:
                    next_reading_delta = int(data['data']['prossimaRilvazione'])
                else:
                    print('status error')
            else:
                print('error no response')


if __name__ == "__main__":
    main()
