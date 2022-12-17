import time
from datetime import datetime
import logging 

#name of file to execute repeatedly:
executeble_file = 'code.py'
time_interval = 3600

#log file setup
logging.basicConfig(filename="code.log",  format='%(asctime)s %(message)s',  filemode='w') 
logger=logging.getLogger() 
logger.setLevel(logging.DEBUG) 

#main
while(1):
    now = datetime.now(tz=pytz.timezone('Asia/Tehran')) 

    for i in range(10):
        logger.info(f"Openned {now}") 

        try:
            #execfile( executeble_file )
            update_regions_online_traffic(regions, API_url, API_key, output_file_address)

            logger.info("Success") 
        except Exception as e:
            logger.error(f"Error: {e}") 

    time.sleep( time_interval )