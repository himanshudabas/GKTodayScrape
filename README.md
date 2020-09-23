# GKTodayScrape - Python script to scrape GKToday.in and Telegram Bot to serve those PDFs
Python Script to Scrape GKToday Website to create monthly magazines and Quiz PDFs.
Monthly magazines & Quiz are created in both .docx and .pdf format.

### NOTE :
I have tested this script on Windows & Linux. Although I have only setup the Telegram Bot on Linux. You can follow the Guide till Step 2 on Windows. After that the guide is only for Linux.
## 1. Setup
##### Clone the Project in you Home folder
`>> git clone ~/`

#### 1.1. Install LibreOffice in order to convert the .docx to .pdf
[LibreOffice Download Link](https://www.libreoffice.org/download/download/)
If you are on windows, you need to set add it to the PATH.

##### 1.2. Setup Python Virtual Environment
make a folder named gkdoday in home directory.
`>> mkdir ~/gktoday`
`>> cd ~/gktoday`
Initialize python virtual environment and activate.
`>> python3 -m venv env`
`>> source ./env/bin/activate`
Install the required python libraries.
`(env) >> pip install bs4 requests python-docx`

## 2. Run the Script
`(env) >> python ~/GKTodayScrape/scrape.py`

## 3. Setup of Telegram Bot
Following section will help you setup your own Telegram Bot to serve the converted PDF Magazines on the Bot.
#### 3.1. Create your Telegram Bot and get it's API Key
[How to Build Your First Telegram Bot: A Guide for Absolute Beginners](https://www.process.st/telegram-bot/)
#### 3.2. Get a SSL certificate
Note: Telegram only works over HTTPS if you want to use webhooks. So you need to get an SSL certificate for this to work. Follow this Guide to get a SSL certificate. (Yes, its Free)
[Running Your Flask Application Over HTTPS](https://blog.miguelgrinberg.com/post/running-your-flask-application-over-https)
#### 3.3. Run the Flask Server in the background
`>> nohup ~/gktoday/env/bin/python ~/GKTodayScrape/app.py >> ~/gktoday/log/nohup_app.py.log 2>&1 &`
This will also log the output of nohup in ~/gktoday/log/nohup_app.py.log
In case something Bad happens, you can check this this log file for errors

## 4. Add cronjob
Note : This is not necessary, but you might want to add a cronjob to your linux server to preiodically scrape files from GKToday.in.
##### Open crontab and add the foloowing line and save the crontab
`>> crontab -e`
> 0 */4 * * * ~/gktoday/env/bin/python ~/GKTodayScrape/scrape.py >> ~/gktoday/log/cron_scrape.log 2>&1