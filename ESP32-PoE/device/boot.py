import network
from machine import Pin
import time

lan = network.LAN(mdc = Pin(23), mdio = Pin(18), power = Pin(12), phy_type = network.PHY_LAN8720, phy_addr=0)
lan.active(True)

while not lan.isconnected():
  pass

time.sleep(10)
print('Connected\n',lan.ifconfig(), '\nSystem start')