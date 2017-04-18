# Twitter Similarity
This project allows the user to select a top 1000 Twitter user along with some tags such as (food-lover, gamer, etc), and returns a ranked list of other Twitter users similar to them using machine learning for tag-generation and TF-IDF from tweets for information ranking and retrieval. 

Created by: for CS 4300 at Cornell University
## Setup
```
-git clone https://github.com/hanli1/cs4300sp2017-twitter-tags.git
-pip install -r requirements.txt
-Create a localsettings.py file in mysite that is based on the settings.py file, but with things filled in
-Perform Django migrations to build your database models
-Prepopulate data using the prepopulate.py script
-python manage.py runserver
```
Open in browser: http://127.0.0.1:8000


## About this framework
Take a look at the `project_template/test.py` file which implement the function that searching for the most similar messages to the query based on their edit difference. You can implement your system accoring to this sample code. Note that you have to make sure that you have imported all the libraries or modules you need for each python file you createed. 

For the input data, I just simply use the JSON file `jsons/kardashian-transcripts.json` and I push it together with the whole project to the heroku. You can put your input data at any place on the internet as long as your web app can get access to the data and the reading process will not hurt its efficiency.

Then take a look at the `project_template/views.py`. You will find out how your code and functions interact with the index page  `project_template/templates/project_template/index.html`. When django get a valid query, it will call the `find_similar` function in `project_template/test.py` and render to show the results at the bottom of the index page. Pagination function also lives in `project_template/views.py` and the output is paginated on `project_template/templates/project_template/index.html`.

To change styling of the app, modify or add stylings in the `mysite/static` folder.



