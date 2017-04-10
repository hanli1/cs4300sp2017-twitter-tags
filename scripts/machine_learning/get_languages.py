from langdetect import detect
import re
import sys
import csv
import os
import pickle
from collections import Counter
from preprocess import emoji_pattern, raw_directory
from cos_sim_and_lda import pickle_directory

people = {}

# don't run unless you got a lot of time
# results already available as pickle file
def detect_language(file_name):
    with open(os.path.join(raw_directory, file_name), 'rb') as f:
      reader = csv.reader(f)
      for a, b, line in reader:
        try:
            # remove links
            content = re.sub(r'http\S+', '', line, flags=re.MULTILINE)
            content = content.decode('utf-8')
            # remove emojis
            content = re.sub(emoji_pattern, "", content)
            content = content.lower()
            tokens = re.findall(r"[\w']+|[.,!?;]", content)
            #remove punctuation
            tokens = [token for token in tokens if not token in ".,!?;\"'"]
            #detect the language of the tweet
            processed_tweet = " ".join(tokens)
            if not processed_tweet : continue
            if not b in people : people[b] = []
            people[b].append(detect(processed_tweet))
        except Exception as e:
            print "Error processing tweet", e, processed_tweet
            continue

if __name__ == "__main__":
    reload(sys)
    sys.setdefaultencoding('utf-8')
    for filename in os.listdir(raw_directory):
        if filename.endswith(".csv"):
            detect_language(filename)

    # languages in ISO 639-1 https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes
    people = {person: Counter(languages) for person, languages in people.items() if person != 'name'}

    # save the distribution of the tweet languages of each user as a pickle file
    with open(os.path.join(pickle_directory,'tweet_language_distribution.pickle'), 'wb') as handle:
        pickle.dump(people, handle, protocol=pickle.HIGHEST_PROTOCOL)

    people = {person: (sorted([(val, lang) for lang, val in people[person].items()], reverse=True)[0][1]) for person
                in people}

    # save the most likely language of each user as a pickle file
    with open(os.path.join(pickle_directory,'user_language_map.pickle'), 'wb') as handle:
        pickle.dump(people, handle, protocol=pickle.HIGHEST_PROTOCOL)
