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
tag_list_file = os.path.join(directory, '../scripts/machine_learning/tags_list')
tweet_tag_file = os.path.join(directory, '../scripts/machine_learning/tweet_tags.csv')

tfidf_vec = TfidfVectorizer(max_df=0.5, min_df=10, stop_words='english', norm='l2')

user_to_tweets = {}
index_to_user = user_to_index  = index_to_tweets = user_by_vocab = features_dict = idfs = tag_list = None


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


def make_tags_list():
    global tag_list
    tag_list = []
    with open(tag_list_file, 'r') as handle:
        content = handle.readlines()
        for line in content:
            line = line.strip()
            if line != "":
                tag_list.append(line)


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


def save_tag_tf_idf_matrices():
    tag_to_user_tweets_list = {}
    num_users = len(user_to_index)
    for tag in tag_list:
        tag_to_user_tweets_list[tag] = list()
        for i in range(num_users):
            tag_to_user_tweets_list[tag].append("")
    with open(tweet_tag_file, 'r') as f:
        reader = csv.reader(f)
        for user_name, tweet, tag in reader:
            if user_name == 'name' :
                continue
            user_index = user_to_index[user_name]
            tag = tag.strip()
            if tag in tag_list:
                tag_to_user_tweets_list[tag][user_index] = tag_to_user_tweets_list[tag][user_index] + " " + str(tweet)
    tag_to_vocabulary_dict = {}
    tag_to_tfidf_dict = {}
    for tag in tag_list:
        tag_tfidf_vec = TfidfVectorizer(max_df=0.5, min_df=10, stop_words='english', norm='l2')
        tag_user_by_vocab = tag_tfidf_vec.fit_transform([tweets for tweets in tag_to_user_tweets_list[tag]])
        tag_user_by_vocab = tag_user_by_vocab.toarray()
        with open(os.path.join(pickle_directory, str(tag) + '_user_by_vocab.pickle'), 'wb') as handle:
            pickle.dump(tag_user_by_vocab, handle, protocol=pickle.HIGHEST_PROTOCOL)
        tag_features_dict = tag_tfidf_vec.vocabulary_
        with open(os.path.join(pickle_directory, str(tag) + '_features_dict.pickle'), 'wb') as handle:
            pickle.dump(tag_features_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)
        tag_idfs = tag_tfidf_vec.idf_
        with open(os.path.join(pickle_directory, str(tag) + '_idfs.pickle'), 'wb') as handle:
            pickle.dump(tag_idfs, handle, protocol=pickle.HIGHEST_PROTOCOL)
        tag_to_vocabulary_dict[tag] = tag_tfidf_vec.vocabulary_
        tag_to_tfidf_dict[tag] = tag_user_by_vocab
    return (tag_to_vocabulary_dict, tag_to_tfidf_dict)


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


def save_top_tag_user_words(tag_to_vocab_dict, tag_to_tfidf_dict):
    for tag in tag_list:
        tag_tfidf_matrix = tag_to_tfidf_dict[tag]
        word_to_index = tag_to_vocab_dict[tag]
        index_to_word = {}
        for word in word_to_index:
            index_to_word[word_to_index[word]] = word
        tag_user_top_words = np.empty((tag_tfidf_matrix.shape[0], 500), dtype='object')
        for i in range(len(tag_user_top_words)):
            user_sorted_top_words_indexes = np.argsort(tag_tfidf_matrix[i])[::-1]
            user_sorted_top_words = []
            for j in range(500):
                current_word = index_to_word[user_sorted_top_words_indexes[j]]
                user_sorted_top_words.append(current_word)
            tag_user_top_words[i] = user_sorted_top_words
        with open(os.path.join(pickle_directory, str(tag) + '_user_top_words.pickle'), 'wb') as handle:
            pickle.dump(tag_user_top_words, handle, protocol=pickle.HIGHEST_PROTOCOL)


def load_tfidf_matrix() :
    global user_by_vocab, features_dict, idfs
    with open(os.path.join(pickle_directory, 'user_by_vocab.pickle'), 'rb') as handle:
        user_by_vocab= pickle.load(handle)
    with open(os.path.join(pickle_directory, 'features_dict.pickle'), 'rb') as handle:
        features_dict = pickle.load(handle)
    with open(os.path.join(pickle_directory, 'idfs.pickle'), 'rb') as handle:
        idfs = pickle.load(handle)


def get_similar_accounts(user, cos_sim_matrix, user_to_index_map, index_to_user_map, all_user_top_words, tags=None):
    """
    Using the cosine similarity matrix and top words of each user, this function returns the most similar users to the
    given user as well as top words in common
    """
    tag_to_user_top_words = {}
    if tags:
        for tag in tags:
            print tag
            with open(os.path.join(pickle_directory, str(tag) + '_user_top_words.pickle'), 'rb') as handle:
                user_top_words = pickle.load(handle)
                tag_to_user_top_words[tag] = user_top_words
    user_index = user_to_index_map[user]
    sim_vector = np.argsort(cos_sim_matrix[user_index])[::-1]
    similar_accounts_list = []
    # mapping from the user's top words to their index/rank in their list of top words
    user_top_words_to_index = {}
    for i in range(len(all_user_top_words[user_index])):
        user_top_words_to_index[all_user_top_words[user_index][i]] = i
    # for each tag contains mapping from the user's top words to their index/rank in their list of top words
    tags_user_top_words_to_index = {}
    if tags:
        for tag in tags:
            tags_user_top_words_to_index[tag] = {}
        for tag in tags:
            for i in range(len(tag_to_user_top_words[tag][user_index])):
                tags_user_top_words_to_index[tag][tag_to_user_top_words[tag][user_index][i]] = i
    for i in sim_vector:
        if i != user_index:
            current_user_top_words_to_index = {}
            for j in range(len(all_user_top_words[i])):
                current_user_top_words_to_index[all_user_top_words[i][j]] = j
            # Get top 5 global words (all tweets) in common with current user (we take the top 5 words that have
            # the smallest index sum, where the index refers to the list index of the word in their top words list)
            common_words = set(all_user_top_words[i]).intersection(set(all_user_top_words[user_index]))
            word_to_index_sum = {}
            for word in common_words:
                index_sum = user_top_words_to_index[word] + current_user_top_words_to_index[word]
                word_to_index_sum[word] = index_sum
            top_words_in_common = sorted(word_to_index_sum, key=word_to_index_sum.get)[:5]
            result_entry = {
                "cosine_similarity": cos_sim_matrix[user_index][i],
                "name": index_to_user_map[i],
                "top_words_in_common": top_words_in_common
            }
            # If a list of tags is given, also get top 5 words in common with current user within each tag
            if tags:
                for tag in tags:
                    tag_user_top_words = tag_to_user_top_words[tag]
                    current_user_top_tag_words_to_index = {}
                    for k in range(len(tag_user_top_words[i])):
                        current_user_top_tag_words_to_index[tag_user_top_words[i][k]] = k
                    common_words = set(tag_user_top_words[i]).intersection(set(tag_user_top_words[user_index]))
                    tag_word_to_index_sum = {}
                    for word in common_words:
                        index_sum = tags_user_top_words_to_index[tag][word] + current_user_top_tag_words_to_index[word]
                        tag_word_to_index_sum[word] = index_sum
                    top_words_in_common = sorted(tag_word_to_index_sum, key=tag_word_to_index_sum.get)[:5]
                    result_entry[tag + "_top_words_in_common"] = top_words_in_common
            similar_accounts_list.append(result_entry)
    return similar_accounts_list


def print_top_words(model, feature_names, n_top_words):
    for topic_idx, topic in enumerate(model.components_):
        print("Topic #%d:" % topic_idx)
        print(" ".join([feature_names[i] for i in topic.argsort()[:-n_top_words - 1:-1]]))


def setup_and_run(user, tags=None):
    cos_sim_matrix = np.load(os.path.join(pickle_directory, 'cos_sim_matrix.npy'))
    with open(os.path.join(pickle_directory, 'user_to_index.pickle'), 'rb') as handle:
        user_to_index_map = pickle.load(handle)
    with open(os.path.join(pickle_directory, 'index_to_user.pickle'), 'rb') as handle:
        index_to_user_map = pickle.load(handle)
    with open(os.path.join(pickle_directory, 'all_user_top_words.pickle'), 'rb') as handle:
        all_user_top_words = pickle.load(handle)
    return get_similar_accounts(user, cos_sim_matrix, user_to_index_map, index_to_user_map, all_user_top_words, tags)


if __name__ == "__main__":
    if not os.path.exists(os.path.join(pickle_directory, 'user_to_tweets.pickle')) :
        # puts all tweets into memory
        for filename in os.listdir(processed_directory):
            if filename.endswith(".csv") : build_data(filename)

        # get the tag list
        make_tags_list()

        # saves all relevant maps as pickle files for faster retrieval in subsequent runs
        save_maps()

        # save global tf-idf matrix (all tweets)
        save_tfidf_matrix()

        # save global top user words based on tf-idf weightings (all tweets)
        save_top_user_words()

        # save tf-idf matrix for each tag
        tag_to_vocabulary_dict, tag_to_tf_idf_dict = save_tag_tf_idf_matrices()

        # save top user words for each tag
        save_top_tag_user_words(tag_to_vocabulary_dict, tag_to_tf_idf_dict)

    load_maps()
    load_tfidf_matrix()

    # get cos_sim matrix
    cos_sim_matrix = np.dot(user_by_vocab, user_by_vocab.T)

    # save cosine similarity matrix
    np.save(os.path.join(pickle_directory, 'cos_sim_matrix'), cos_sim_matrix)
