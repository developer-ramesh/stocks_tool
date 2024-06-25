#!/bin/bash

# Change to your project directory
cd /var/www/html/stocks_tool

# Activate the virtual environment
source virtualenv/bin/activate

# Run your Python script
python script.py


#################################################################################################
# SET it in crontab using crontab -e
  
# 30 9 * * * /bin/bash /var/www/html/stocks_tool/cron.sh >> /var/www/html/stocks_tool/log.log 2>&1
