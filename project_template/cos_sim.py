from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer

import pickle
import os
import csv
import numpy as np
import sys

directory = os.path.dirname(__file__)
processed_directory = os.path.join(directory, "../data/processed_tweets")
pickle_directory = os.path.join(directory, '../scripts/machine_learning/pickles')

count_vec = CountVectorizer(max_df=0.8, min_df=10, stop_words='english')
tfidf_vec = TfidfVectorizer(max_df=0.8, min_df=10, stop_words='english', norm='l2')

user_to_tweets = {}
index_to_user = user_to_index  = index_to_tweets = cos_sim_matrix = user_by_vocab_count = user_by_vocab_tfidf \
    = features = english_users = None

# build user_to_tweets from csv files
# set english_only to false if you want to consider all users
def build_data(filename, english_only) :
    with open(os.path.join(processed_directory, filename), 'rb') as f:
      reader = csv.reader(f)
      for tweetid, user, tweet in reader:
          if user == 'name' : continue
          if english_only and user not in english_users : continue
          if user not in user_to_tweets : user_to_tweets[user] = []
          user_to_tweets[user].append(tweet)


# saves index_to_user, user_to_index, index_to_tweets , and user_to_tweets as a pickle file
def save_maps() :
    # set user_to_tweets in form for tf-idf vectorizer
    global user_to_tweets, index_to_user, user_to_index, index_to_tweets
    user_to_tweets = {user: ' '.join(tweets) for user, tweets in user_to_tweets.items()}
    with open(os.path.join(pickle_directory, 'user_to_tweets.pickle'), 'wb') as handle:
        pickle.dump(user_to_tweets, handle, protocol=pickle.HIGHEST_PROTOCOL)

    index_to_user = user_to_tweets.keys()
    with open(os.path.join(pickle_directory, 'index_to_user.pickle'), 'wb') as handle:
        pickle.dump(index_to_user, handle, protocol=pickle.HIGHEST_PROTOCOL)

    user_to_index = {user: index for index, user in enumerate(index_to_user)}
    with open(os.path.join(pickle_directory, 'user_to_index.pickle'), 'wb') as handle:
        pickle.dump(user_to_index, handle, protocol=pickle.HIGHEST_PROTOCOL)

    index_to_tweets = [user_to_tweets[index_to_user[i]] for i in range(len(user_to_tweets))]
    with open(os.path.join(pickle_directory, 'index_to_tweets.pickle'), 'wb') as handle:
        pickle.dump(index_to_tweets, handle, protocol=pickle.HIGHEST_PROTOCOL)

# loads index_to_user, user_to_index, index_to_tweets , and user_to_tweets from pickle files
def load_maps() :
    global user_to_tweets, index_to_user, user_to_index, index_to_tweets
    with open(os.path.join(pickle_directory, 'user_to_tweets.pickle'), 'rb') as handle:
        user_to_tweets = pickle.load(handle)

    with open(os.path.join(pickle_directory, 'index_to_user.pickle'), 'rb') as handle:
        index_to_user = pickle.load(handle)

    with open(os.path.join(pickle_directory, 'user_to_index.pickle'), 'rb') as handle:
        user_to_index = pickle.load(handle)

    with open(os.path.join(pickle_directory, 'index_to_tweets.pickle'), 'rb') as handle:
        index_to_tweets = pickle.load(handle)

def save_count_and_tfidf_matrix() :
    global user_by_vocab_count, user_by_vocab_tfidf, index_to_tweets, features

    user_by_vocab_count = count_vec.fit_transform([tweets for tweets in index_to_tweets])
    user_by_vocab_count = user_by_vocab_count.toarray()
    with open(os.path.join(pickle_directory, 'user_by_vocab_count.pickle'), 'wb') as handle:
        pickle.dump(user_by_vocab_count, handle, protocol=pickle.HIGHEST_PROTOCOL)

    user_by_vocab_tfidf = tfidf_vec.fit_transform([tweets for tweets in index_to_tweets])
    user_by_vocab_tfidf = user_by_vocab_tfidf.toarray()
    with open(os.path.join(pickle_directory, 'user_by_vocab_tfidf.pickle'), 'wb') as handle:
        pickle.dump(user_by_vocab_tfidf, handle, protocol=pickle.HIGHEST_PROTOCOL)

    features = count_vec.get_feature_names()
    with open(os.path.join(pickle_directory, 'features.pickle'), 'wb') as handle:
        pickle.dump(features, handle, protocol=pickle.HIGHEST_PROTOCOL)

def load_count_and_tfidf_matrix() :
    global user_by_vocab_count, user_by_vocab_tfidf, features
    with open(os.path.join(pickle_directory, 'user_by_vocab_count.pickle'), 'rb') as handle:
        user_by_vocab_count = pickle.load(handle)
    with open(os.path.join(pickle_directory, 'user_by_vocab_tfidf.pickle'), 'rb') as handle:
        user_by_vocab_tfidf = pickle.load(handle)
    with open(os.path.join(pickle_directory, 'features.pickle'), 'rb') as handle:
        features = pickle.load(handle)

# get all the similar accounts for a given user
def get_similar_accounts(user) :
    user_index = user_to_index[user]
    sim_vector = np.argsort(cos_sim_matrix[user_index])
    return [(index_to_user[i], cos_sim_matrix[user_index][i]) for i in sim_vector if i != user_index][::-1]

# gets all users who have mostly english tweets
def get_english_users() :
    with open(os.path.join(pickle_directory, 'user_language_map.pickle'), 'rb') as handle:
        languageMapping = pickle.load(handle)
    return [user for user, language in languageMapping.items() if language == 'en']

def print_top_words(model, feature_names, n_top_words):
    for topic_idx, topic in enumerate(model.components_):
        print("Topic #%d:" % topic_idx)
        print(" ".join([feature_names[i] for i in topic.argsort()[:-n_top_words - 1:-1]]))

def setup_and_run(user):
  global cos_sim_matrix

  if not os.path.exists(os.path.join(pickle_directory, 'user_to_tweets.pickle')) :
      for filename in os.listdir(processed_directory):
          if filename.endswith(".csv") : build_data(filename, english_only)

      # saves all relevant maps as pickle files for faster retrieval in subsequent runs
      save_maps()

      # save tf-idf matrix
      save_count_and_tfidf_matrix()

  load_maps()
  load_count_and_tfidf_matrix()

  # get cos_sim matrix
  cos_sim_matrix = np.dot(user_by_vocab_tfidf, user_by_vocab_tfidf.T)
  return get_similar_accounts(user)

if __name__ == "__main__":
    english_only = True
    english_users = set(get_english_users())

    try:
        if sys.argv[1] == 'all': english_only = False
    except Exception as e: pass

    if not os.path.exists(os.path.join(pickle_directory, 'user_to_tweets.pickle')) :
        for filename in os.listdir(processed_directory):
            if filename.endswith(".csv") : build_data(filename, english_only)

        # saves all relevant maps as pickle files for faster retrieval in subsequent runs
        save_maps()

        # save tf-idf matrix
        save_count_and_tfidf_matrix()

    load_maps()
    load_count_and_tfidf_matrix()

    # get cos_sim matrix
    cos_sim_matrix = np.dot(user_by_vocab_tfidf, user_by_vocab_tfidf.T)

    # print top 10 similar users
    for user in ['Ariana Grande', 'Trey Songz', 'Zendaya', 'Hillary Clinton'] :
        print get_similar_accounts(user)[:10]

    # run topic modeling and fetch 30 topics
    # lda_results = lda_model.fit_transform(user_by_vocab_count)

    # print_top_words(lda_model, features, 30)
