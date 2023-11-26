#!/usr/bin/env python3
import time
from datetime import datetime

import ntplib

from helpers import turn_off, get_idfs_status, set_connected_user, set_time_configured, set_time_not_configured

# check if time is synchronized using NTP
try:
    ntp_client = ntplib.NTPClient()

    while get_idfs_status() == "on":
        # send request to the server
        response = ntp_client.request("pool.ntp.org")
        timestamp = response.tx_time

        # get international time and user machine time
        reference_datetime = datetime.fromtimestamp(timestamp)
        user_datetime = datetime.now()

        # check if user machine time is synchronized
        time_difference = abs(user_datetime - reference_datetime)
        threshold = 40
        if not time_difference.seconds < threshold:
            # update id1fs status if time is not synchronized
            set_time_not_configured()
            turn_off()
            set_connected_user("system")
        else:
            set_time_configured()
        time.sleep(4)
except:
    set_time_configured()
