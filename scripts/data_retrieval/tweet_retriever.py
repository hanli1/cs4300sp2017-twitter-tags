import tweepy
from tweepy import OAuthHandler
import time
import csv
import ConfigParser
import os.path
import sys

#Constants
WAIT_NUM = 20

config = ConfigParser.ConfigParser()
config.read("../../config.py")
consumer_key = config.get("keys", "consumer_key")
consumer_secret = config.get("keys", "consumer_secret")
access_token = config.get("keys", "access_token")
access_secret = config.get("keys", "access_secret")

# print consumer_key
# print consumer_secret
# print access_token
# print access_secret

auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_secret)
api = tweepy.API(auth)
raw_directory = "../../data/raw_tweets"

def get_user_tweets(username, id):
  tweets_by_user = {}
  name = ""
  tweets = []
  
  for account in api.user_timeline(screen_name = username, count=1):
    name = account.user.name

  if name == "":
    print("User doesn't exist") 
    return 

  tweets_by_user[name] = []
  new_tweets = api.user_timeline(screen_name = username, include_rts=False, count=200)
  tweets += new_tweets
  oldest = tweets[-1].id - 1

  while len(new_tweets) > 0 and len(tweets) < 10000:
    try: 
      new_tweets = api.user_timeline(screen_name = username, count=200, include_rts=False, max_id=oldest)
      tweets += new_tweets
      oldest = tweets[-1].id - 1
      print "...%s tweets downloaded so far" % (len(tweets))
    except:
      print "Over Capacity Error: Trying again" 
      time.sleep(60)

  print "---- %s tweets downloaded from %s ID = %s ----" % (len(tweets), name, id)

  tweets_by_user[name] = [[unicode(tweet.id_str).encode("utf-8"), unicode(name).encode("utf-8"), \
    unicode(tweet.created_at).encode("utf-8"), unicode(str(tweet.favorite_count)).encode("utf-8"), \
    unicode(tweet.text).encode("utf-8")] for i, tweet in enumerate(tweets)]
  return tweets_by_user

def get_untagged_users_handles():
  """
  Returns a list of the handles of users who have not been tagged yet
  """
  people = []
  with open('top_users_handle.txt', 'r') as f:
    lines = f.readlines()
    for line in lines: 
      people.append(line[1:])
  return people

def get_tagged_users_handles_dict():
  """
  Returns a dictionary mapping each tag to the users of that tag
  """
  tagged_users_dict = {}
  with open('tagged_users_handle.txt', 'r') as f:
    lines = f.readlines()
    current_tag = ""
    current_user_list = []
    for line in lines:
      colon_index = line.find(":") 
      if colon_index >= 0:
        if len(current_user_list) > 0:
          tagged_users_dict[current_tag] = current_user_list
        current_tag = line[:colon_index].lower()
        current_user_list = []
      elif len(line) > 0 and line != "\n" and line != "":
        current_user_list.append(line[1:])
    if len(current_user_list) > 0:
      tagged_users_dict[current_tag] = current_user_list
  return tagged_users_dict


def write_to_csv(tweets_by_user, csv_file, tagged=False):
  if tagged:
    file_location = os.path.join(raw_directory, "tagged", csv_file)
  else:
    file_location = os.path.join(raw_directory, csv_file)
  if os.path.isfile(file_location):
    with open(file_location, 'a') as f:
      writer = csv.writer(f)
      for name, tweets in tweets_by_user.items():
        writer.writerows(tweets)
  else:
    with open(file_location, 'wb') as f:
      writer = csv.writer(f)
      writer.writerow(["id","name","date","favorites","text"])
      for name, tweets in tweets_by_user.items():
        writer.writerows(tweets)

if __name__ == "__main__":
  start_time = time.time()

  user_type = sys.argv[1]

  if user_type == "untagged_users":
    #start and end argument
    start = int(sys.argv[2])
    end = int(sys.argv[3])

    #Get list of people
    people = get_untagged_users_handles()

    #Adjust start and end
    start = max(0, start)
    end = min(len(people), end)

    #Depends on the section #, retrieve tweets from subset of users
    for i in range(start, end):
      tweets_by_user = get_user_tweets(people[i], i + 1)
      write_to_csv(tweets_by_user, "user_tweets.csv")
      #Wait for a minute before getting more tweets
      if i > 1 and i%WAIT_NUM == 0:
        print("\n---- Retrieved from " + str(i + 1) + " people, waiting for 30 seconds before continuing ----\n")
        time.sleep(30)
  elif user_type == "tagged_users":
    tag_to_people_dict = get_tagged_users_handles_dict()
    i = 0
    for tag in tag_to_people_dict:
      tag_people_list = tag_to_people_dict[tag]
      for person in tag_people_list:
        user_tweets = get_user_tweets(person, i + 1)
        write_to_csv(user_tweets, tag.replace(" ", "_") + ".csv", tagged=True)
        #Wait for a minute before getting more tweets
        if i > 1 and i%WAIT_NUM == 0:
          print("\n---- Retrieved from " + str(i + 1) + " people, waiting for 30 seconds before continuing ----\n")
          time.sleep(30)
  print("--- %s seconds ---" % (time.time() - start_time))


  