import tweepy
from tweepy import OAuthHandler
import time
import csv
import ConfigParser

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
def get_user_tweets(username):
	name = ""
	tweets = []
	
	for account in api.user_timeline(screen_name = username, count=1):
		name = account.user.name

	if name == "":
		print("User doesn't exist") 
		return 

	tweets_by_user[name] = []
	new_tweets = api.user_timeline(screen_name = username, include_retweets=False, count=200)
	tweets += new_tweets
	oldest = tweets[-1].id - 1

	while len(new_tweets) > 0 and len(tweets) < 10000:
		try: 
			new_tweets = api.user_timeline(screen_name = username, count=200, include_retweets=False, max_id=oldest)
			tweets += new_tweets
			oldest = tweets[-1].id - 1
			print "...%s tweets downloaded so far" % (len(tweets))
		except Error:
			print "Over Capacity Error: Trying again" 
			time.sleep(10)

	print "---- %s tweets downloaded from %s -----" % (len(tweets), name)

	tweets_by_user[name] = [[tweet.id_str, name, tweet.text.encode("utf-8")] for tweet in tweets]

def write_to_csv():
	# writer  = open('user_tweets_2.txt', 'w')
	# current_name = ""
	# writer.write(str(len(tweets_by_user)))
	# for name, tweets in tweets_by_user.items():
	# 	writer.write(name)
	# 	writer.write(str(len(tweets)))
	# 	for tweet in tweets:
	# 		writer.write(tweet) 
	# writer.close()  

	with open('user_tweets.csv', 'wb') as f:
		writer = csv.writer(f)
		writer.writerow(["id","name","text"])
		for name, tweets in tweets_by_user.items():
			writer.writerows(tweets)

if __name__ == "__main__":
	start_time = time.time()

	reader  = open('top_users_handle.txt', 'r')
	for line in reader: 
		get_user_tweets(line[1:])
	reader.close()
	# get_user_tweets("MisterWives")

	write_to_csv()
	print("--- %s seconds ---" % (time.time() - start_time))


	