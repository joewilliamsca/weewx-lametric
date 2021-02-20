Weewx extension to post weather data to your LaMetric Time

Here are the steps to run the plugin

1) download the extension:

  wget -O weewx-lametric.zip https://github.com/joewilliamsca/weewx-lametric/archive/main.zip
  
2) run the installer:

 wee_extension --install weewx-lametric.zip
 
3) modify your weewx.conf file.  search for LaMetric in the StdRESTful section:



Setting up.

You will need to set up your account over at  https://developer.lametric.com,  if you havent already done so
 
You will also need to get your api_key from the following location.  https://developer.lametric.com/user/devices   -  this will become your device_key in weewx.conf
 
 You will also need to get the ip address of your LaMetric Time,  by looking at the device info in your phone app. this will become your server_ip in weewx.conf
    


Properties

   device_key  -  this is from https://developer.lametric.com/user/devices   (api for your device)
   
   server_ip - this is your ip address for your LaMetric Time
   
   sound - (default is cat)  - Sound that your LaMetric Time will make for the notification 
 
   Other options for sounds can be found here - https://lametric-documentation.readthedocs.io/en/latest/reference-docs/device-notifications.html
           
   icon -  (default is 43246) - icon displayed in the notification  
   
   You can also change this value to another icon value,  see the link  https://developer.lametric.com/icons
    
   
