#LaMetric Time display for weewx data

from weecfg.extension import ExtensionInstaller

def loader():
    return LametricInstaller()

class LametricInstaller(ExtensionInstaller):
    def __init__(self):
        super(LametricInstaller, self).__init__(
            version="0.01",
            name='lametric',
            description='Send notifications to Lametric Time.',
            author="Joe Williams",
            author_email="joe@joewilliams.ca",
            restful_services='user.lametric.LaMetric',
            config={
                'StdRESTful': {
                    'LaMetric': {
                        'server_ip': 'INSERT_LAMETRIC_TIME_IP_HERE',
                        'device_key': 'INSERT_LAMETRIC_TIME_API_KEY_HERE',
                        'sound': 'cat',
                        'icon': '43246'}}},
            files=[('bin/user', ['bin/user/lametric.py'])]
            )
