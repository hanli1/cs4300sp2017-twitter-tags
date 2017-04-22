# Twitter Similarity
This project allows the user to select a top 1000 Twitter user along with some tags such as (food-lover, gamer, etc), and returns a ranked list of other Twitter users similar to them using machine learning for tag-generation and TF-IDF from tweets for information ranking and retrieval. 

CS 4300 Information Retrieval, Cornell University, Spring 2017
## Requirements
PostgresSQL
Python 2.7
## Setup
Clone the repository into a directory
```
git clone https://github.com/hanli1/cs4300sp2017-twitter-tags.git
```
Install the Python requirements
```
pip install -r requirements.txt
```
Create a localsettings.py file in /mysite that is based on the settings.py file with PostgreSQL database credentials

Perform Django migrations to build your database models

Prepopulate database with tagged users
```
python prepopulate.py
```
Run the Django server
```
python manage.py runserver
```
Open in browser at http://127.0.0.1:8000








