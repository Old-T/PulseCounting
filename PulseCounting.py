#!/usr/bin/env python

import time
import json
import urllib2
import threading
import logging
import logging.handlers
import os
from gpiozero import DigitalInputDevice

ELEC_DELTA = 0
ELEC_GPIO =
ELEC_COUNTER_LOCK = threading.Lock()
ELEC_LAST_TIME = 0
ELEC_POST_TIME = 0


def elec_intr():
    tme = time.time()
    global ELEC_DELTA
    global ELEC_LAST_TIME
    global ELEC_POST_TIME
    with ELEC_COUNTER_LOCK:
        ELEC_LAST_TIME = tme
        if ELEC_POST_TIME == 0:
            ELEC_POST_TIME = ELEC_LAST_TIME
        else:
            ELEC_DELTA += 1
    logging.debug('Electricity counter tick: %d' % ELEC_DELTA)


def main():
    global ELEC_DELTA
    global ELEC_LAST_TIME
    global ELEC_POST_TIME
    global ELEC_COUNTER

    syslog = logging.handlers.SysLogHandler(address='/dev/log', facility='local1')
    syslog.setFormatter(logging.Formatter('local_sensors.py: %(levelname)s %(message)s'))
    logging.getLogger().addHandler(syslog)
    logging.getLogger().setLevel(logging.INFO)

    while True:
        try:
            #res = json.load(urllib2.urlopen(GET_URL % ELEC_IDX))
            if res['status'] != 'OK':
                raise Exception('Domoticz json error')
            break
        except Exception as e:
            logging.warning(e)
        time.sleep(30.0)

    ELEC_COUNTER = int(float(res['result'][0]['Data'][:-4]) * 1000)
    #    ELEC_COUNTER = <Your initial count here * 1000, don't forget to remove after Domoticz updated!>
    logging.info('Current electricity counter is: %d' % ELEC_COUNTER)

    elecSensor = DigitalInputDevice(ELEC_GPIO, pull_up=True)
    elecSensor.when_deactivated = elec_intr

    os.nice(-20)

    logging.info('Polling loop starting')

    while True:
        time.sleep(60)

        with ELEC_COUNTER_LOCK:
            if ELEC_LAST_TIME > ELEC_POST_TIME:
                ELEC_LOAD = ELEC_DELTA * 3600 / (ELEC_LAST_TIME - ELEC_POST_TIME)
            else:
                ELEC_LOAD = 0

            ELEC_COUNTER += ELEC_DELTA

            ELEC_DELTA = 0
            ELEC_POST_TIME = ELEC_LAST_TIME

        if ELEC_LOAD != 0:
            try:
                #res = json.load(urllib2.urlopen((SET_URL + ';%d') % (ELEC_IDX, int(ELEC_LOAD), ELEC_COUNTER)))
                if res['status'] != 'OK':
                    raise Exception('Domoticz json error')
                logging.info('Elec load %.2f counter %d' % (ELEC_LOAD, ELEC_COUNTER))
            except Exception as e:
                logging.warning(e)


if __name__ == "__main__":
    main()