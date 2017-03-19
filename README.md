#Project Framework Description

This is a website framework which provides a simple UI for your information system. You can simply embed your code and ideas in it, so that they can be visited and used by others from the internet. Let others be proud of your system just like yourself!

Check out the sample that we came up with: https://cs4300.herokuapp.com/pt/

Feel free to make any changes to the framework. You can even totally discard it and establish your own website as long as it will not be a problem for you. Please include your project name and student names in your `project_template/templates/project_template/index.html` file. In the template we provided, a TODO is indicated for you to put in your names. After all, it is your own information retrieval system not the website you have to focus on. Hope you guys enjoy it. Have fun!

Below are several useful tools and important components of the framework. 

## Git & Github
Git is a version control system designed to handle everything for your project. GitHub is a web-based Git repository hosting service where you can share your codes and ideas with your teammate and collaborate with each other. If you have never used that before, you can download Git from https://git-scm.com/downloads. 

Then, it’s time to start up! You have to use the terminal or the command line tools for this part.

NOTE: If you are using Windows, please read the `If you are using Windows` section at the end of this document before starting the tutorial.

- Go to the folder you want to put your project.
```sh
(e.g.) $ cd ~/Document  
```
- Pull the source code of this framework from github to your local machine. Remain in this project directory for all future commands in the tutorial.
```sh
$ git clone https://github.com/CornellNLP/CS4300.git
$ cd CS4300
```
- Sign in to your own github account and create a new repository for this project. The name of the repo's need to start with `cs4300sp2017-`.
- Add `cristiandnm` (Prof. DNM's account name) as a member with admin rights on the git repo. 
- Push the framework to your own github repository.
```sh
$ git remote rename origin upstream
$ git remote add origin URL_TO_GITHUB_REPO
$ git push origin master
```
  You can find this `URL_TO_GITHUB_REPO` on the home page of your new repository, which will be of the form `https://github.com/<Username>/<Repo-Name>.git` (ex: https://github.com/CornellNLP/CS4300.git). The URL you want is in the text box near the `Download ZIP` button on your repo’s homepage.

- Now, everything is on your local machine. You can modify the code and push them to your own remote repository. 

	- Pull the code 
	```sh
	$ git pull
	```
	- Push the code 
	```sh
	$ git add -A
	$ git commit -m "<message about your modification>"
	$ git push
	```
	- If you are unable to successfully push/pull, set the default behavior by doing:
	```
	$ git config branch.master.remote <YOUR-REPO-NAME>
	```

Learn more: 
https://git-scm.com/doc

## Django
Django is a high-level Python Web framework which allows us to easily use python to develop a web application without caring about the http, TCP/IP or socket things. Our framework is developed with Django since python is the language you guys are familiar with. So, you can still use python to realize almost all the parts of your information system.

Good News! In this project, you do not have to use the database at all, which could directly reduce tons of workloads. Just like the previous assignments, your system will take some files as input and provide some result as output. You may form the input data that you will use in your system into JSON files or whatever format you like and put it anywhere your system can get access to.

You may want to run this website on your own computer everytime you make some progress, before depolying it on the remote server. You still have to use terminals to do this.
- First, you have to install django
```sh
$ pip install django
```
- In order to see the CSS styling and pagination of results, make sure to install `whitenoise` and `django-bootstrap-pagination`
```sh
$ pip install whitenoise
$ pip install django-bootstrap-pagination
```
- Go to the project folder and start the web server
```sh
$ cd ~/Documents/CS4300
$ python manage.py runserver
```
  
  At this moment, if the server is running successfully, you should see something in your terminal like this:
```
Performing system checks...

System check identified no issues (0 silenced).
March 13, 2017 - 03:50:58
Django version 1.9.4, using settings 'mysite.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```
- Open your browser and you can have a look at your website at http://127.0.0.1:8000/pt
- Now, the website is running on your local machine. Everytime you make some change, just simply refresh the page to check whether it works or not. Enjoy!

Learn more:
https://docs.djangoproject.com/en/1.9/

## Heroku
Heroku is a platform as a service (PaaS) that enables developers to build and run applications entirely in the cloud. We can easily deploy our python app in minutes on heroku. You still have to use terminals to do this.

- First, install heroku toolbelt from https://toolbelt.heroku.com/
- Create a heroku account.
- Login on your local machine
```sh
$ heroku login
```
- Go to the project folder and revise the requirements.txt file if you use any new packages in your python code
- Create an app on heroku.
```sh
$ heroku create <your_website_name>
```
- Push the project on heroku.
```
$ git push heroku master
```
- The application is now deployed. Ensure that at least one instance of the app is running.
```sh
$ heroku ps:scale web=1
```
- Now, you can visit your website at `https://<your_website_name>.herokuapp.com/pt/`. Sometimes, it may take a while to get response from heroku server, just be patient!

Learn more:
https://devcenter.heroku.com/articles/getting-started-with-python#introduction

## About this framework
Take a look at the `project_template/test.py` file which implement the function that searching for the most similar messages to the query based on their edit difference. You can implement your system accoring to this sample code. Note that you have to make sure that you have imported all the libraries or modules you need for each python file you createed. 

For the input data, I just simply use the JSON file `jsons/kardashian-transcripts.json` and I push it together with the whole project to the heroku. You can put your input data at any place on the internet as long as your web app can get access to the data and the reading process will not hurt its efficiency.

Then take a look at the `project_template/views.py`. You will find out how your code and functions interact with the index page  `project_template/templates/project_template/index.html`. When django get a valid query, it will call the `find_similar` function in `project_template/test.py` and render to show the results at the bottom of the index page. Pagination function also lives in `project_template/views.py` and the output is paginated on `project_template/templates/project_template/index.html`.

To change styling of the app, modify or add stylings in the `mysite/static` folder. You can experiment with Javascript and JQuery too!

Learn more:
https://devcenter.heroku.com/articles/django-assets

## Small Tips
- When you get `Permission Denied`, try to add `sudo` before your last shell command.
- You should have three remote git repositories: 
	- `upstream`, the shared repo for the project template
	- `origin`, your own remote repo on github
	- `heroku`, the repo you deploy on the heroku
  
  You can check it with this command
```sh
$ git remote -v
```
- When you meet some problems with heroku deployment, it should be really helpful to read the build logs.
- The Git repo should be no larger than 300MB. Have a look at this page https://devcenter.heroku.com/articles/limits for more information about the limits of heroku. 

## If you are using Windows
- In order to run the shell commands throughout this tutorial that involve Git and Heroku, you will need to use a shell that recognizes Git. On Windows with Git installed, you should be able to find a program called “Git Shell” by searching your applications. Open this and use it for running all commands throughout the tutorial in the “Git & Github” and “Heroku” sections.

- If you already have configured their Windows Powershell or Command Prompt (CMD) to accept Git commands, but this is not the default setting.

- You need to have the python-Levenshtein package already installed before starting the tutorial. You should have installed this from doing A2, but if you do not, then you will need a Python 2.7 environment active to install the package. Once you’ve activated the Python 2.7 environment, you should simply be able to do “pip install python-Levenshtein”.

- If you normally work in a Python 3 environment, then you will need to use CMD to switch to your Python 2.7 environment (Powershell or Git Shell will not work). If you are unable to do this or the tutorial is not working for you due to python-Levenshtein, post on Piazza and we will post the zip of the package to put directly into your Python installation directory.

- In general, if you are having any other issues with running commands in the “Django” section of the tutorial, try opening a CMD prompt instance (separate from the Git Shell/Powershell you are using for the other sections), navigate to the project directory, and run those commands in CMD.
