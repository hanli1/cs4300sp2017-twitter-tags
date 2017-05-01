from sklearn.feature_extraction.text import TfidfVectorizer

import pickle
import os
import csv
import numpy as np
import boto3
from StringIO import StringIO
from django.conf import settings

directory = os.path.dirname(__file__)
processed_directory = os.path.join(directory, "../data/processed_tweets")
pickle_directory = os.path.join(directory, '../scripts/machine_learning/pickles')

tfidf_vec = TfidfVectorizer(max_df=0.7, min_df=10, stop_words='english', norm='l2')

user_to_tweets = {}
index_to_user = user_to_index  = index_to_tweets = user_by_vocab = features_dict = idfs = None

# build user_to_tweets from csv files
# set english_only to false if you want to consider all users
def build_data(filename):
    with open(os.path.join(processed_directory, filename), 'rb') as f:
      reader = csv.reader(f)
      for tweetid, user, tweet in reader:
          if user == 'name' :
              continue
          if user not in user_to_tweets :
              user_to_tweets[user] = []
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

def save_tfidf_matrix() :
    global user_by_vocab, index_to_tweets, features_dict, idfs

    user_by_vocab = tfidf_vec.fit_transform([tweets for tweets in index_to_tweets])
    user_by_vocab = user_by_vocab.toarray()
    with open(os.path.join(pickle_directory, 'user_by_vocab.pickle'), 'wb') as handle:
        pickle.dump(user_by_vocab, handle, protocol=pickle.HIGHEST_PROTOCOL)

    features_dict = tfidf_vec.vocabulary_
    with open(os.path.join(pickle_directory, 'features_dict.pickle'), 'wb') as handle:
        pickle.dump(features_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)

    idfs = tfidf_vec.idf_
    with open(os.path.join(pickle_directory, 'idfs.pickle'), 'wb') as handle:
        pickle.dump(idfs, handle, protocol=pickle.HIGHEST_PROTOCOL)

def save_top_user_words():
    word_to_index = tfidf_vec.vocabulary_
    index_to_word = {}
    for word in word_to_index:
        index_to_word[word_to_index[word]] = word
    all_user_top_words = np.empty((user_by_vocab.shape[0], 500), dtype='object')
    for i in range(len(all_user_top_words)):
        user_sorted_top_words_indexes = np.argsort(user_by_vocab[i])[::-1]
        user_sorted_top_words = []
        for j in range(500):
            current_word = index_to_word[user_sorted_top_words_indexes[j]]
            user_sorted_top_words.append(current_word)
        all_user_top_words[i] = user_sorted_top_words

    with open(os.path.join(pickle_directory, 'all_user_top_words.pickle'), 'wb') as handle:
        pickle.dump(all_user_top_words, handle, protocol=pickle.HIGHEST_PROTOCOL)

def load_tfidf_matrix() :
    global user_by_vocab, features_dict, idfs
    with open(os.path.join(pickle_directory, 'user_by_vocab.pickle'), 'rb') as handle:
        user_by_vocab= pickle.load(handle)
    with open(os.path.join(pickle_directory, 'features_dict.pickle'), 'rb') as handle:
        features_dict = pickle.load(handle)
    with open(os.path.join(pickle_directory, 'idfs.pickle'), 'rb') as handle:
        idfs = pickle.load(handle)

# get all the similar accounts for a given user
def get_similar_accounts(user, cos_sim_matrix, user_to_index_map, index_to_user_map, all_user_top_words) :
    user_index = user_to_index_map[user]
    sim_vector = np.argsort(cos_sim_matrix[user_index])[::-1]
    similar_accounts_list = []
    user_top_words_to_index = {}
    for i in range(len(all_user_top_words[user_index])):
        user_top_words_to_index[all_user_top_words[user_index][i]] = i
    for i in sim_vector:
        if i != user_index:
            current_user_top_words_to_index = {}
            for j in range(len(all_user_top_words[i])):
                current_user_top_words_to_index[all_user_top_words[i][j]] = j
            # Get top 5 words in common with current user (we take the top 5 words that have the smallest index sum,
            # where the index refers to the list index of the word in their top words list)
            common_words = set(all_user_top_words[i]).intersection(set(all_user_top_words[user_index]))
            word_to_index_sum = {}
            for word in common_words:
                index_sum = user_top_words_to_index[word] + current_user_top_words_to_index[word]
                word_to_index_sum[word] = index_sum
            top_words_in_common = sorted(word_to_index_sum, key=word_to_index_sum.get)[:5]
            similar_accounts_list.append({
                "cosine_similarity": cos_sim_matrix[user_index][i],
                "name": index_to_user_map[i],
                "top_words_in_common": top_words_in_common
            })
    return similar_accounts_list


def print_top_words(model, feature_names, n_top_words):
    for topic_idx, topic in enumerate(model.components_):
        print("Topic #%d:" % topic_idx)
        print(" ".join([feature_names[i] for i in topic.argsort()[:-n_top_words - 1:-1]]))


def setup_and_run(user):
    if not settings.DEBUG:
        client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )
        s3 = client.list_objects(
            Bucket=settings.AWS_BUCKET
        )
        r1 = client.get_object(
            Bucket=settings.AWS_BUCKET,
            Key="cos_sim_matrix.npy"
        )
        data_string = StringIO(r1['Body'].read())
        cos_sim_matrix = np.load(data_string)
        r2 = client.get_object(
            Bucket=settings.AWS_BUCKET,
            Key="user_to_index.pickle"
        )
        user_to_index_map = pickle.loads(r2['Body'].read())
        r3 = client.get_object(
            Bucket=settings.AWS_BUCKET,
            Key="index_to_user.pickle"
        )
        index_to_user_map = pickle.loads(r3['Body'].read())
        r4 = client.get_object(
            Bucket=settings.AWS_BUCKET,
            Key="all_user_top_words.pickle"
        )
        all_user_top_words = pickle.loads(r4['Body'].read())
    else:
        cos_sim_matrix = np.load(os.path.join(pickle_directory, 'cos_sim_matrix.npy'))
        with open(os.path.join(pickle_directory, 'user_to_index.pickle'), 'rb') as handle:
            user_to_index_map = pickle.load(handle)
        with open(os.path.join(pickle_directory, 'index_to_user.pickle'), 'rb') as handle:
            index_to_user_map = pickle.load(handle)
        with open(os.path.join(pickle_directory, 'all_user_top_words.pickle'), 'rb') as handle:
            all_user_top_words = pickle.load(handle)
    return get_similar_accounts(user, cos_sim_matrix, user_to_index_map, index_to_user_map, all_user_top_words)


if __name__ == "__main__":
    if not os.path.exists(os.path.join(pickle_directory, 'user_to_tweets.pickle')) :
        for filename in os.listdir(processed_directory):
            if filename.endswith(".csv") : build_data(filename)

        # saves all relevant maps as pickle files for faster retrieval in subsequent runs
        save_maps()

        # save tf-idf matrix
        save_tfidf_matrix()

        # save top user words based on tf-idf weightings
        save_top_user_words()

    load_maps()
    load_tfidf_matrix()

    # get cos_sim matrix
    cos_sim_matrix = np.dot(user_by_vocab, user_by_vocab.T)

    # save cosine similarity matrix
    np.save(os.path.join(pickle_directory, 'cos_sim_matrix'), cos_sim_matrix)
