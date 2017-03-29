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
config.read("../config.py")
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

tweets_by_user = {}
def get_user_tweets(username, id):
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

  print "---- %s tweets downloaded from %s ----" % (len(tweets), name)

  tweets_by_user[name] = [[unicode(tweet.id_str).encode("utf-8"), unicode(name).encode("utf-8"), 
                      unicode(tweet.text)c.encode("utf-8")] for i, tweet in enumerate(tweets)]

def get_handles():
  people = []
  reader  = open('top_users_handle.txt', 'r')
  for line in reader: 
    people.append(line[1:])
  reader.close()
  return people

def write_to_csv():
  if os.path.isfile('user_tweets.csv'):
    with open('user_tweets.csv', 'a') as f:
      writer = csv.writer(f)
      for name, tweets in tweets_by_user.items():
        writer.writerows(tweets)
  else:
    with open('user_tweets.csv', 'wb') as f:
      writer = csv.writer(f)
      writer.writerow(["id","name","text"])
      for name, tweets in tweets_by_user.items():
        writer.writerows(tweets)

if __name__ == "__main__":
  start_time = time.time()

  #start and end argument
  start = int(sys.argv[1])
  end = int(sys.argv[2])

  #Get list of people
  people = get_handles()

  #Adjust start and end
  start = max(0, start)
  end = min(len(people), end)

  #Depends on the section #, retrieve tweets from subset of users
  for i in range(start, end):
    get_user_tweets(people[i], i + 1)
    #Wait for a minute before getting more tweets
    if i > 1 and i%WAIT_NUM == 0:
      print("\n---- Retrieved " + str(i + 1) + " waiting for 30 seconds to continue ----\n")
      time.sleep(30)

  #Create and write to CSV file
  write_to_csv()

  print("--- %s seconds ---" % (time.time() - start_time))


  