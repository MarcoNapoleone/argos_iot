import os
import dht
import urequests
import ntptime
import json
from time import *
import random

sensor = dht.DHT22(Pin(4))
ntptime.host = "1.europe.pool.ntp.org"

DATA_URL = 'https://argos-iot.com/webservice/getdata.php'
CHECK_URL = 'https://incomunicando.it/webservice/checkdata.php'
LAST_READING = mktime((2000, 1, 1, 0, 0, 0, 0, 0))
NEXT_READING_DELTA = 5


def sync_rtc():
    try:
        ntptime.settime()
    except:
        print("Error syncing time")


def add_time_delta(date, delta_hours=0, delta_minutes=0, delta_seconds=0, delta_mseconds=0):
    return mktime((
        date[0],
        date[1],
        date[2],
        date[3] + delta_hours,
        date[4] + delta_minutes,
        date[5] + delta_seconds,
        date[6] + delta_mseconds,
        0
    ))


def get_sensor_data():
    sensor.measure()

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
        {"sensore": "temp", "valore": sensor.temperature(), "um": "C"},
        {"sensore": "hum", "valore": sensor.humidity(), "um": "%"},
        {"sensore": "bpt", "valore": random.randint(9500, 10300) / 10, "um": "hPa"},
        {"sensore": "aqi", "valore": random.randint(10, 6000) / 10, "um": "AQI"}
    ]


def get_payload():
    return {
        "id": "25555",
        "dispositivo": {
            "mac": '0000.0000.0000.0000',
            "ip": lan.ifconfig()[0]
        },
        "datiRilevazione": get_sensor_data(),
        "tempoRilevazione": mktime(localtime()),
    }


def core_loop():
    global LAST_READING
    global NEXT_READING_DELTA

    tries = 3
    success = False

    if mktime(localtime()) > add_time_delta(localtime(LAST_READING), delta_seconds=NEXT_READING_DELTA):
        while not success and tries > 0:
            try:
                r = urequests.post(DATA_URL, json=get_payload())
                if r.status_code in [200, 201]:
                    print(r.json())
                    data = json.loads(r.text)
                    LAST_READING = mktime(localtime())
                    NEXT_READING_DELTA = int(data['data']['prossimaRilvazione'])
                    success = True
                else:
                    print('HTTP request failed: {} {}'.format(r.status_code, r.reason))
            except OSError as e:
                print('network error: {}'.format(e.errno))
                tries -= 1
                pass
    else:
        print('Awaiting...')
        sleep(int(NEXT_READING_DELTA / 3))


def main():
    sync_rtc()
    while 1:
        core_loop()


main()
