# GKTodayScrape
Python Script to Scrape GKToday Website to create monthly magazine

This script scrapes the GKToday Website and creates monthly magazines in both .docx and .pdf format



### env is a virtual environment with all the dependencies of the project
### Run the flask server in the background to serve the telegram requests and outputs the log in the ~/gktoday/log/nohup.log file

nohup ~/gktoday/env/bin/python ~/gktoday/app.py >> ~/gktoday/log/nohup.log 2>&1 &

### follow the guide in the following link to get a ssl certificate because telegram only works over https
https://blog.miguelgrinberg.com/post/running-your-flask-application-over-https

### run this command to get the ssl 
sudo certbot certonly --webroot -w ~/gktoday/le -d yourdomain.com

