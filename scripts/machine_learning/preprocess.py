"""
Performs preprocessing of tweets of csv files in data/raw_tweets by removing
links, emojis, punctuation, and stop words as well as performing stemming and 
writing out the results to data/processed_tweets
"""
import re
import sys
import csv
import os
import stop_words
import nltk
from langdetect import detect

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


def preprocess_file(file_name):
    """
    Performs preprocessing for the tweets in a given file
    """
    file_text = []
    with open(os.path.join(raw_directory, file_name), 'rb') as f:
        reader = csv.reader(f)
        current_user_tweets = []
        current_user = ""
        current_user_english_tweets = 0
        current_user_total_tweets = 0
        for a, b, line in reader:
            try:
                if current_user != b:
                    if current_user != "":
                        english_tweet_ratio = float(current_user_english_tweets) / \
                        current_user_total_tweets
                        if len(current_user_tweets) > 500 and english_tweet_ratio > 0.6:
                            file_text = file_text + current_user_tweets
                        print current_user + ", " + str(current_user_english_tweets) + \
                        " english, " + str(current_user_total_tweets) + " total"
                    current_user = b
                    current_user_tweets = []
                    current_user_english_tweets = 0
                    current_user_total_tweets = 0
                current_user_total_tweets = current_user_total_tweets + 1
                # remove links
                content =  re.sub(r'http\S+', '', line, flags=re.MULTILINE)
                content = content.decode('utf-8')
                # remove emojis
                content = re.sub(emoji_pattern, "", content)
                content = content.lower()
                tokens = re.findall(r"[\w']+|[.,!?;]", content)
                #remove punctuation
                tokens = [token for token in tokens if not token in ".,!?;\"'"]
                #Check if tweet is english
                if tweet_is_english(content, tokens):
                    current_user_english_tweets = current_user_english_tweets + 1
                    # remove stop words
                    tokens = [token for token in tokens if not token in stop_word_list]
                    # perform stemming
                    tokens = [p_stemmer.stem(token) for token in tokens]
                    processed_tweet = " ".join(tokens)
                    if len(processed_tweet) > 1:
                        current_user_tweets.append([a, b, processed_tweet])
            except Exception as e:
                continue
    file_end_index = file_name.find(".csv")
    processed_file_name = file_name[:file_end_index] + "_processed.csv"
    processed_file = open(os.path.join(processed_directory, processed_file_name), "wb")
    writer = csv.writer(processed_file)
    writer.writerows(file_text)
    processed_file.close()

if __name__ == "__main__":
    #u use utf8 by default
    reload(sys)
    sys.setdefaultencoding('utf-8')
    for filename in os.listdir(raw_directory):
        if filename.endswith(".csv"): 
            preprocess_file(filename)
