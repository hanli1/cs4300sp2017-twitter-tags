"""
Performs preprocessing of tweets of csv files in data/raw_tweets 
"""
import re
import sys
import csv
import os
import stop_words
import nltk
from langdetect import detect
import argparse

emoji_pattern = re.compile(
    u"(\ud83d[\ude00-\ude4f])|"  # emoticons
    u"(\ud83c[\udf00-\uffff])|"  # symbols & pictographs (1 of 2)
    u"(\ud83d[\u0000-\uddff])|"  # symbols & pictographs (2 of 2)
    u"(\ud83d[\ude80-\udeff])|"  # transport & map symbols
    u"(\ud83c[\udde0-\uddff])"  # flags (iOS)
    "+", flags=re.UNICODE)
raw_directory = "../../data/raw_tweets"
processed_directory = "../../data/processed_tweets"
stop_word_list = stop_words.get_stop_words('en')
p_stemmer = nltk.stem.porter.PorterStemmer()
english_vocab = set(w.lower() for w in nltk.corpus.words.words())

def tweet_is_english(content, tokens):
    """
    Check if the tweet represented by the given content and tokens is in english
    """
    num_english_tokens = 0
    num_tokens = 0
    for token in tokens:
        if token in english_vocab:
            num_english_tokens = num_english_tokens + 1
    return ((float(num_english_tokens) / len(tokens)) >= 0.6 or detect(content) == "en")


def preprocess_file(file_name, stemming=True, english_check=True, tagged=True):
    """
    One version of preprocessing that removes links, emojis, punctuation, and stop words, 
    as well as potentially performing stemming and checking for english tweets depending
    on the arguments of stemming, english_check
    """
    file_text = []
    if tagged:
        file_location = os.path.join(raw_directory, "tagged", file_name)
    else:
        file_location = os.path.join(raw_directory, file_name)
    with open(file_location, 'rb') as f:
        reader = csv.reader(f)
        current_user_tweets = []
        current_user = ""
        current_user_english_tweets = 0
        current_user_total_tweets = 0
        for line in reader:
            if tagged:
                tweet_id, name, date, favorites, text = line
            else:
                # tweet_id, name, text = line
                try:
                    tweet_id, name, date, favorites, text = line
                except Exception as e:
                    pass
            try:
                if current_user != name:
                    if current_user != "":
                        if english_check:
                            english_tweet_ratio = float(current_user_english_tweets) / \
                            current_user_total_tweets
                            if len(current_user_tweets) > 500 and english_tweet_ratio > 0.6:
                                file_text = file_text + current_user_tweets
                            print current_user + ", " + str(current_user_english_tweets) + \
                            " english, " + str(current_user_total_tweets) + " total tweets"
                        else:
                            print current_user + ", " + str(current_user_total_tweets) + \
                            " total tweets"
                            file_text = file_text + current_user_tweets
                    current_user = name
                    current_user_tweets = []
                    current_user_english_tweets = 0
                    current_user_total_tweets = 0
                current_user_total_tweets = current_user_total_tweets + 1
                # remove links
                content =  re.sub(r'http\S+', '', text, flags=re.MULTILINE)
                content = content.decode('utf-8')
                # remove emojis
                content = re.sub(emoji_pattern, "", content)
                content = content.lower()
                initial_tokens = re.findall(r"[\w']+|[.,!?;]", content)
                #remove punctuation
                initial_tokens = [token for token in initial_tokens if not token in ".,!?;\"'"]
                # remove stop words
                tokens = [token for token in initial_tokens if not token in stop_word_list]
                if stemming:
                    # perform stemming
                    tokens = [p_stemmer.stem(token) for token in tokens]
                #Check if tweet is english
                if english_check:
                    if tweet_is_english(content, tokens):
                        current_user_english_tweets = current_user_english_tweets + 1
                        processed_tweet = " ".join(tokens)
                        if len(processed_tweet) > 1:
                            if tagged:
                                current_user_tweets.append([tweet_id, name, date, favorites, processed_tweet])
                            else:
                                current_user_tweets.append([tweet_id, name, processed_tweet])
                else:
                    processed_tweet = " ".join(tokens)
                    if len(processed_tweet) > 1:
                        if tagged:
                            current_user_tweets.append([tweet_id, name, date, favorites, processed_tweet])
                        else:
                            current_user_tweets.append([tweet_id, name, processed_tweet])
            except Exception as e:
                continue
    if current_user != "":
        if english_check:
            english_tweet_ratio = float(current_user_english_tweets) / \
            current_user_total_tweets
            if len(current_user_tweets) > 500 and english_tweet_ratio > 0.6:
                file_text = file_text + current_user_tweets
            print current_user + ", " + str(current_user_english_tweets) + \
            " english, " + str(current_user_total_tweets) + " total tweets"
        else:
            print current_user + ", " + str(current_user_total_tweets) + \
            " total tweets"
            file_text = file_text + current_user_tweets
    file_end_index = file_name.find(".csv")
    processed_file_name = file_name[:file_end_index] + "_processed.csv"
    if tagged:
        file_location = os.path.join(processed_directory, "tagged", processed_file_name)
    else:
        file_location = os.path.join(processed_directory, processed_file_name)
    processed_file = open(file_location, "wb")
    writer = csv.writer(processed_file)
    writer.writerows(file_text)
    processed_file.close()

if __name__ == "__main__":
    #u use utf8 by default
    parser = argparse.ArgumentParser()
    #command line flag to control whether to perform stemming during preprocessing
    parser.add_argument('-stemming', dest='stemming', default="True")
    #command line flag to control whether to only consider twitter individuals with
    #mostly english tweets
    parser.add_argument('-english_check', dest='english_check', default="True")
    #command line flag to control whether to perform preprocessing on unlabeled tweets
    #or the labeled tweets in the "tagged" directory
    parser.add_argument('-tagged', dest='tagged', default="True")
    results = parser.parse_args()
    stemming = True
    english_check = True
    if results.stemming == "False":
        stemming = False
    if results.english_check == "False":
        english_check = False
    if results.tagged == "True":
        tagged = True
        processed_dir = os.path.join(raw_directory, "tagged")
    else:
        tagged = False
        processed_dir = raw_directory
    reload(sys)
    sys.setdefaultencoding('utf-8')
    for filename in os.listdir(processed_dir):
        print filename
        if filename.endswith(".csv"):
            preprocess_file(filename, stemming=stemming, english_check=english_check, 
                tagged=tagged)
