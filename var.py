import os
import time

VER = '1.0.1'

LOG_PATH = os.getcwd() + os.sep + "temp_log" + os.sep
LOG_NAME = str(int(time.time())) + "_temp.log"


PPPOE_ACCOUNT = ''
PPPOE_PASSWORD = ''

WIFI_SSID = 'coconuts_test_tools'
WIFI_PASSWORD = '12345678'

HOST = '192.168.31.1'
WEB_USERNAME = 'admin'
WEB_PWD = '12345678'
WEB_KEY = 'a2ffa5c9be07488bbb04a3a47d3c5f6a'
IV = '64175472480004614961023454661220'
# uci export account
ACCOUNT_DEFAULT_PWD = 'b3a4190199d9ee7fe73ef9a4942a69fece39a771'