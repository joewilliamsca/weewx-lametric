#Weewx-lametric connector
#using an existing extension from Matthew Wall (OWN) to build this one

"""
Send notifications to your LaMetric Time from weewx
"""

from __future__ import absolute_import
import six.moves.queue
import base64
import syslog
import six.moves.urllib.request, six.moves.urllib.parse, six.moves.urllib.error
import six.moves.urllib.request, six.moves.urllib.error, six.moves.urllib.parse


import weewx
import weewx.restx
import weewx.units
from weeutil.weeutil import to_bool, accumulateLeaves

VERSION = "0.2"

if weewx.__version__ < "3":
    raise weewx.UnsupportedFeature("weewx 3 is required, found %s" %
                                   weewx.__version__)

def logmsg(level, msg):
    syslog.syslog(level, 'restx: LaM: %s' % msg)

def logdbg(msg):
    logmsg(syslog.LOG_DEBUG, msg)

def loginf(msg):
    logmsg(syslog.LOG_INFO, msg)

def logerr(msg):
    logmsg(syslog.LOG_ERR, msg)

class LaMetric(weewx.restx.StdRESTbase):
    def __init__(self, engine, config_dict):
        """This service recognizes standard restful options plus the following:

           """
        super(LaMetric, self).__init__(engine, config_dict)
        loginf('service version is %s' % VERSION)
        try:
            site_dict = config_dict['StdRESTful']['LaMetric']
            site_dict = accumulateLeaves(site_dict, max_level=1)
            site_dict['server_ip']
            site_dict['device_key']
            site_dict['icon']
            site_dict['sound']
        except KeyError as e:
            logerr("Data will not be posted: Missing option %s" % e)
            return
        site_dict['manager_dict'] = weewx.manager.get_manager_dict(
            config_dict['DataBindings'], config_dict['Databases'], 'wx_binding')

        self.archive_queue = six.moves.queue.Queue()
        self.archive_thread = LaMetricThread(self.archive_queue, **site_dict)
        self.archive_thread.start()
        self.bind(weewx.NEW_ARCHIVE_RECORD, self.new_archive_record)
        loginf("Data will be sent to %s" % site_dict['server_ip'])

    def new_archive_record(self, event):
        self.archive_queue.put(event.record)

class LaMetricThread(weewx.restx.RESTThread):
    """
    """

    _SERVER_URL = 'http://%s:8080/api/v2/device/notifications'
    _DATA_MAP = {
        'wind speed': ('windSpeed',   '%.1f', 0.2777777777, 0.0), # m/s
        'wind gust':  ('windGust',    '%.1f', 0.2777777777, 0.0), # m/s
        'temp':       ('outTemp',     '%.1f', 1.0, 0.0),    # C
        'humidity':   ('outHumidity', '%.0f', 1.0, 0.0),    # percent
        'pressure':   ('barometer',   '%.3f', 1.0, 0.0),    # mbar?
        'rain hr':    ('hourRain',    '%.2f', 10.0, 0.0),   # mm
        'rain 24h':   ('rain24',      '%.2f', 10.0, 0.0),   # mm
        'rain today': ('dayRain',     '%.2f', 10.0, 0.0)   # mm
        }

    def __init__(self, queue,
                 server_ip, device_key, icon, sound, manager_dict,
                 server_url=_SERVER_URL, skip_upload=False,
                 post_interval=None, max_backlog=0, stale=None,
                 log_success=True, log_failure=True,
                 timeout=60, max_tries=3, retry_wait=5):
        super(LaMetricThread, self).__init__(queue,
                                                   protocol_name='LaM',
                                                   manager_dict=manager_dict,
                                                   post_interval=post_interval,
                                                   max_backlog=max_backlog,
                                                   stale=stale,
                                                   log_success=log_success,
                                                   log_failure=log_failure,
                                                   timeout=timeout,
                                                   max_tries=max_tries,
                                                   retry_wait=retry_wait)
        self.server_ip = server_ip
        self.device_key = device_key
        self.icon = icon
        self.sound = sound
        self.server_url = server_url % server_ip
        #logdbg('server url: %s' % self.server_url)
        self.skip_upload = to_bool(skip_upload)

    def process_record(self, record, dbm):
        r = self.get_record(record, dbm)
        data = self.get_data(r)
        if self.skip_upload:
            loginf("skipping upload")
            return
        #logdbg('PR ---- using device_key: %s' % self.device_key)
        #logdbg('PR ---- using server_url: %s' % self.server_url)
        req = six.moves.urllib.request.Request(self.server_url, data)
        req.get_method = lambda: 'POST'
        req.add_header("User-Agent", "weewx/%s" % weewx.__version__)
        b64s = base64.encodestring('%s:%s' % ('dev',self.device_key)).replace('\n', '')
        req.add_header("Authorization", "Basic %s" % b64s)
        req.add_header("Content-Type", "application/json")
        self.post_with_retries(req)

    def get_data(self, in_record):
        # put everything into the right units
        record = weewx.units.to_METRIC(in_record)

        # put data into expected scaling, structure, and format
        values = {}
        for key in self._DATA_MAP:
            rkey = self._DATA_MAP[key][0]
            if rkey in record and record[rkey] is not None:
              #  logdbg('rkey: %s' % rkey)
	      #	logdbg('key: %s' % key)
                v = record[rkey] * self._DATA_MAP[key][2] + self._DATA_MAP[key][3]
 	      #	logdbg('v: %s' % v) 
                values[key] = self._DATA_MAP[key][1] % v
	      #	logdbg('values[key]: %s' % values[key])

       # logdbg('data: %s' % values) 
       # logdbg('Barometer: %s' % values['pressure'])    #20768
       # logdbg('Temp: %s' % values['temp'])		#2497
       # logdbg('Wind: %s' % values['wind speed'])	#1153
       # logdbg('Rain: %s' % values['rain today'])	#72
       # logdbg('Humidity: %s' % values['humidity'])	#2423

        #return values
        return " { \"model\": { \"frames\": [{\"icon\": \"%s\", \"text\": \"WeeWx Data\"}, { \"icon\":\"2497\", \"text\":\"%s\"}, { \"icon\":\"20768\", \"text\":\"%s\"}, { \"icon\":\"1153\", \"text\":\"%s\"}, { \"icon\":\"72\", \"text\":\"%s\"}, { \"icon\":\"2423\", \"text\":\"%s\"} ],\"sound\": {\"category\":\"notifications\",\"id\":\"%s\"} } }" % (self.icon, values['temp'], values['pressure'], values['wind speed'], values['rain today'], values['humidity'],  self.sound)
