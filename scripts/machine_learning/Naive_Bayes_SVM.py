import sys
import os
import csv
import pickle
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup  
import re
import nltk
from nltk.corpus import stopwords

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn import svm
from sklearn.cross_validation import KFold

NUM_CATEGORY = 10
processed_tagged_directory = "../../data/processed_tweets/tagged"
processed_untagged_directory = "../../data/processed_tweets"

def create_data(type):
    """
    Creates panda dataframe from csv files
    """
    data_frames = []

    if type == "train":
        directory = processed_tagged_directory
    else:
        directory = processed_untagged_directory

    for filename in os.listdir(directory):
        if filename.endswith(".csv"):
            tag_label = filename[:filename.find("_processed.csv")]
            t = pd.read_csv(directory + "/" + filename, header=None)
            if type == "train":
                t['CATEGORY'] = tag_label
            data_frames.append(t)
    tweets = pd.concat(data_frames, ignore_index = True)
    return tweets

def train_data(data):
    """
    Perform K-Fold cross validation and create full model
    """
    tweets = np.array(data[4])

    y = np.array(data["CATEGORY"])

    print "Performing 10-fold Cross Validation" 
    kf = KFold(len(tweets), n_folds = 10, shuffle=True)    

    vectorizer = CountVectorizer(analyzer = "word", tokenizer = None, preprocessor = None, stop_words = 'english')

    accuracy = []
    for train_idx, test_idx in kf:
        X_train = vectorizer.fit_transform(tweets[train_idx])
        X_test = vectorizer.transform(tweets[test_idx])
          
        nb = MultinomialNB()
        nb.fit(X_train, y[train_idx])

        pred_nb = nb.predict(X_test)
        pred_nb_prob = nb.predict_proba(X_test)
                        
        pred = pred_nb
        pred_prob = pred_nb_prob
                
        accuracy.append(np.mean(pred == np.array(y[test_idx])))
        print "."

    print ""
    print "Avg Accuracy: " + str(np.mean(accuracy))
    print accuracy

    #Creating Full Model
    X = vectorizer.fit_transform(tweets)

    nb = MultinomialNB()
    nb.fit(X, y)

    with open("trained_naive_bayes_model/trained_model_new", 'w') as f:
        pickle.dump(nb, f)

    with open('pickles/vectorizer_new', 'w') as f:
        pickle.dump(vectorizer, f)

def train_agg_data(data):
    """
    Perform K-Fold cross validation and create full model
    """
    tweets = np.array(data['Tweets'])

    y = np.array(data["CATEGORY"])

    print "Performing 10-fold Cross Validation" 
    kf = KFold(len(tweets), n_folds = 10, shuffle=True)    

    vectorizer = CountVectorizer(analyzer = "word", tokenizer = None, preprocessor = None, stop_words = None, max_df=0.8, min_df=10)

    accuracy = []
    for train_idx, test_idx in kf:
        X_train = vectorizer.fit_transform(tweets[train_idx])
        X_test = vectorizer.transform(tweets[test_idx])
          
        nb = MultinomialNB()
        nb.fit(X_train, y[train_idx])

        pred_nb = nb.predict(X_test)
        pred_nb_prob = nb.predict_proba(X_test)
                        
        pred = pred_nb
        pred_prob = pred_nb_prob
                
        accuracy.append(np.mean(pred == np.array(y[test_idx])))
        print "."

    print ""
    print "Avg Accuracy: " + str(np.mean(accuracy))
    print accuracy

    #Creating Full Model
    X = vectorizer.fit_transform(tweets)

    nb = MultinomialNB()
    nb.fit(X, y)

    with open("trained_naive_bayes_model/trained_agg_model_new", 'w') as f:
        pickle.dump(nb, f)

    with open('pickles/vectorizer_agg_new', 'w') as f:
        pickle.dump(vectorizer, f)

def test_data(data):
    """
    Returns prediction given X (data) as well mapping of index to category and vice versa
    """
    tweets = np.array(data[2].values.astype('U'))

    with open("trained_naive_bayes_model/trained_model_new", 'r') as f:
        nb = pickle.load(f)

    with open('pickles/vectorizer_new', 'r') as f:
        vectorizer = pickle.load(f)
    
    #Creating a index to category and category to index mapping 
    idx_to_cat = nb.classes_
    cat_to_idx = {}
    for i, cat in enumerate(idx_to_cat):
        cat_to_idx[cat] = i

    X = vectorizer.transform(tweets)

    pred = nb.predict(X)

    return pred, idx_to_cat, cat_to_idx

def test_agg_data(data):
    """
    Returns prediction given X (data) as well mapping of index to category and vice versa
    """
    tweets = np.array(data['Tweets'].values.astype('U'))

    with open("trained_naive_bayes_model/trained_agg_model_new", 'r') as f:
        nb = pickle.load(f)

    with open('pickles/vectorizer_agg_new', 'r') as f:
        vectorizer = pickle.load(f)
    
    X = vectorizer.transform(tweets)

    pred_agg = nb.predict(X)

    return pred_agg

def tag_users(data, pred, pred_agg, idx_to_cat, cat_to_idx):
    """
    Tags untagged users
    """
    users_tag_freq = {}
    for i, row in data.iterrows():
        freq = users_tag_freq.setdefault(row[1], [0]*NUM_CATEGORY)
        freq[cat_to_idx[pred[i]]]+=1
        users_tag_freq[row[1]] = freq

    threshold = 0.3
    with open("trained_naive_bayes_model/user_tags_new", 'w') as f:
        i = 0
        for user, freq in users_tag_freq.items():
            user_output = str(user) + ": "
            # user_output = user_output + str(idx_to_cat[np.argmax(freq)]) + " "
            user_output = user_output + str(pred_agg[i]) + " "
            for j, c in enumerate(freq):
                if c > np.sum(freq)*threshold and idx_to_cat[j] != pred_agg[i]:
                    if (pred_agg[i] == "liberal" and idx_to_cat[j] == "conservative") or (pred_agg[i] == "conservative" and idx_to_cat[j] == "liberal"):
                        pass
                    user_output = user_output + str(idx_to_cat[j]) + " "
            i+=1
            f.write(user_output + "\n")
    return

def aggregate_tweets(data, train = True):
    text = ""
    users = []
    tweets = []
    category = []
    if train:
        for index, row in data.iterrows():
            if len(users) == 0:
                users.append(row[1])
                if train:
                    category.append(row[5])
            elif users[-1] != row[1]:
                users.append(row[1])
                if train:
                    category.append(row[5])
                tweets.append(text)
                text = ""
            text = text + row[4] + " " 
        tweets.append(text)
        return pd.DataFrame({'User': users, 'Tweets': tweets, 'CATEGORY': category})
    else:
        for index, row in data.iterrows():
            if len(users) == 0:
                users.append(row[1])
            elif users[-1] != row[1]:
                users.append(row[1])
                tweets.append(text)
                text = ""
            text = text + str(row[2]) + " "
            if index % 100000 == 0:
                print "Still aggregating..."
        tweets.append(text)
        return pd.DataFrame({'User': users, 'Tweets': tweets})

if __name__ == "__main__":
    try:
        train_or_test = sys.argv[1].lower()
    except Exception as e:
        print "Input train or test as string"
    
    if train_or_test == "train":
        print "Training Data..."
        data = create_data(train_or_test)
        train_data(data)
        print "Training Aggregated Data..."
        data = aggregate_tweets(data)
        train_agg_data(data)
    elif train_or_test == "test":
        print "Testing Data..."
        data = create_data(train_or_test)
        pred, idx_to_cat, cat_to_idx = test_data(data)
        print "Testing Aggregated Data..."
        data2 = aggregate_tweets(data, False)
        pred_agg = test_agg_data(data2)
        print "Labeling Twitter Users..."
        tag_users(data, pred, pred_agg, idx_to_cat, cat_to_idx)
    else:
        print "Invalid Input"

