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

    #Creating a index to category and category to index mapping
    idx_to_cat = list(pd.Series(y, dtype="category").cat.categories)
    cat_to_idx = {}
    for i, cat in enumerate(idx_to_cat):
        cat_to_idx[cat] = i

    print "Performing 10-fold Cross Validation" 
    kf = KFold(len(tweets), n_folds = 10, shuffle=True)    
    vectorizer = CountVectorizer(analyzer = "word", tokenizer = None, preprocessor = None, stop_words = None)

    accuracy = []
    for train_idx, test_idx in kf:
        X_train = vectorizer.fit_transform(tweets[train_idx])
        X_test = vectorizer.transform(tweets[test_idx])
          
        nb = MultinomialNB()
        nb.fit(X_train, y[train_idx])
        
        llf = svm.LinearSVC()
        llf.fit(X_train, y[train_idx])

        pred_nb = nb.predict(X_test)
        pred_nb_prob = nb.predict_proba(X_test)
        
        pred_svm = llf.predict(X_test)
                
        pred = pred_svm
        pred_prob = pred_nb_prob
        for i, row in enumerate(pred_nb_prob):
            if np.max(row) >= 0.95:
                pred[i] = pred_nb[i]
            else:
                svm_prob = [0]*NUM_CATEGORY;
                svm_prob[cat_to_idx[pred_svm[i]]] = 1
                pred_prob[i] = np.add(np.multiply(0.5, row), np.multiply(0.5,svm_prob))
                pred[i] = idx_to_cat[np.argmax(pred_prob[i])]
                
        accuracy.append(np.mean(pred == np.array(y[test_idx])))
        print "."

    print ""
    print "Avg Accuracy: " + str(np.mean(accuracy))
    print accuracy

    #Creating Full Model
    X = vectorizer.fit_transform(tweets)

    nb = MultinomialNB()
    nb.fit(X, y)

    llf = svm.LinearSVC()
    llf.fit(X, y)

    with open("trained_naive_bayes_model/trained_model_v2", 'w') as f:
        pickle.dump(nb, f)

    with open("trained_svm_model/trained_model_v2", 'w') as f:
        pickle.dump(llf, f)

    with open('pickles/vectorizer', 'w') as f:
        pickle.dump(vectorizer, f)

    # with open("trained_svm_model/trained_model_v2", 'r') as f:
    #   llf = pickle.load(f)

    # pred = llf.predict(X)
    # print np.mean(pred == np.array(y))

def test_data(data):
    """
    Returns prediction given X (data) as well mapping of index to category and vice versa
    """
    tweets = np.array(data[2].values.astype('U'))

    with open("trained_naive_bayes_model/trained_model_v2", 'r') as f:
        nb = pickle.load(f)

    with open("trained_svm_model/trained_model_v2", 'r') as f:
        llf = pickle.load(f)

    with open('pickles/vectorizer', 'r') as f:
        vectorizer = pickle.load(f)
    
    #Creating a index to category and category to index mapping 
    idx_to_cat = nb.classes_
    cat_to_idx = {}
    for i, cat in enumerate(idx_to_cat):
        cat_to_idx[cat] = i

    X = vectorizer.transform(tweets)

    pred_nb = nb.predict(X)
    pred_nb_prob = nb.predict_proba(X)
    pred_svm = llf.predict(X)        
    pred = pred_svm
    pred_prob = pred_nb_prob
    for i, row in enumerate(pred_nb_prob):
        if np.max(row) >= 0.95:
            pred[i] = pred_nb[i]
        else:
            svm_prob = [0]*NUM_CATEGORY;
            svm_prob[cat_to_idx[pred_svm[i]]] = 1
            pred_prob[i] = np.add(np.multiply(0.5, row), np.multiply(0.5,svm_prob))
            pred[i] = idx_to_cat[np.argmax(pred_prob[i])]

    return pred, idx_to_cat, cat_to_idx

def tag_users(data, pred, idx_to_cat, cat_to_idx):
    """
    Tags untagged users
    """
    users_tag_freq = {}
    for i, row in data.iterrows():
        freq = users_tag_freq.setdefault(row[1], [0]*NUM_CATEGORY)
        freq[cat_to_idx[pred[i]]]+=1
        users_tag_freq[row[1]] = freq

    threshold = 0.65
    with open("trained_naive_bayes_model/user_tags_v2", 'w') as f:
        for user, freq in users_tag_freq.items():
            user_output = str(user) + ": "
            user_output = user_output + str(idx_to_cat[np.argmax(freq)]) + " "
            for i, c in enumerate(freq):
                if c > np.max(freq)*threshold and i != np.argmax(freq):
                    user_output = user_output + str(idx_to_cat[i]) + " "
            f.write(user_output + "\n")
    return

if __name__ == "__main__":
    try:
        train_or_test = sys.argv[1].lower()
    except Exception as e:
        print "Input train or test as string"
    
    if train_or_test == "train":
        print "Training Data..."
        data = create_data(train_or_test)
        train_data(data)
    elif train_or_test == "test":
        print "Testing Data..."
        data = create_data(train_or_test)
        pred, idx_to_cat, cat_to_idx = test_data(data)
        print "Labeling Twitter Users..."
        tag_users(data, pred, idx_to_cat, cat_to_idx)
    else:
        print "Invalid Input"

