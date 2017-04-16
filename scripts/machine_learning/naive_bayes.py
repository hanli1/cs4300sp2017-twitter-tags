from sklearn.naive_bayes import MultinomialNB
import os
import csv
import gensim
import numpy
import random
import pickle
import sys
import operator

processed_tagged_directory = "../../data/processed_tweets/tagged"
processed_untagged_directory = "../../data/processed_tweets"


def run_naive_bayes(training_set):
    nb = MultinomialNB()
    training_tweets = []
    training_labels = []
    for (bag_of_words, label) in training_set:
        training_tweets.append(bag_of_words)
        training_labels.append(label)
    print "Starting to train for this fold..."
    nb.fit(training_tweets, training_labels)
    print "Finished training for this fold..."
    return nb


def get_test_accuracy(nb_model, test_set):
    num_examples = 0
    correct_examples = 0
    for (bag_of_words, label) in test_set:
        predicted_label = nb_model.predict(bag_of_words)[0]
        if label == predicted_label:
            correct_examples = correct_examples + 1
        num_examples = num_examples + 1
    return float(correct_examples)/num_examples


def build_tokenized_tweets_list(file_name):
    """
    Build tokenized tweets of each user from the given file
    """
    tokenized_tweets = []
    with open(os.path.join(processed_tagged_directory, file_name), 'rb') as f:
        reader = csv.reader(f)
        for tweet_id, name, date, favorites, text in reader:
            tokens = text.split()
            tokenized_tweets.append(tokens)
    return list(numpy.random.choice(tokenized_tweets, 10000))


def build_tokenized_tweets_dict(file_name):
    """
    Build dictionary mapping each user to their tokenized tweets from a given file
    """
    tokenized_tweets_dict = {}
    with open(os.path.join(processed_untagged_directory, file_name), 'rb') as f:
        reader = csv.reader(f)
        current_name = ""
        current_tweets = []
        for tweet_id, name, text in reader:
            if current_name == "":
                current_name = name
                current_tweets = []
            elif current_name != name:
                tokenized_tweets_dict[current_name] = current_tweets
                current_name = name
                current_tweets = []
            tokens = text.split()
            current_tweets.append(tokens)
        tokenized_tweets_dict[current_name] = current_tweets
    return tokenized_tweets_dict


if __name__ == "__main__":
    try:
        train_or_predict = sys.argv[1]
    except Exception as e:
        train_or_predict = "train"
    if train_or_predict == "train":
        all_tokenized_tweets = []
        all_tokenized_tweets_labels = []
        for filename in os.listdir(processed_tagged_directory):
            if filename.endswith(".csv"):
                tag_label = filename[:filename.find("_processsed.csv")]
                tokenized_tweets = build_tokenized_tweets_list(filename)
                all_tokenized_tweets = all_tokenized_tweets + tokenized_tweets
                all_tokenized_tweets_labels = all_tokenized_tweets_labels + \
                ([tag_label]*len(tokenized_tweets))
        #Build bag of words vector for each tweet
        words_dict = gensim.corpora.Dictionary(all_tokenized_tweets)
        words_dict.filter_extremes(no_below=5, no_above=0.5, keep_n=100000)
        print "Num Words in Dictionary: " + str(len(words_dict.keys()))
        bag_of_words_tweets = [words_dict.doc2bow(tweet) for tweet in all_tokenized_tweets]
        bag_of_words_vectors = []
        for bag_of_words_tweet in bag_of_words_tweets:
            bag_of_words_vector = [0]*len(words_dict.keys())
            for (word_index, word_count) in bag_of_words_tweet:
                bag_of_words_vector[word_index] = word_count
            bag_of_words_vectors.append(bag_of_words_vector)
        #Perform k-fold cross-validation, with k = 10 in this case
        tweets_and_labels = zip(bag_of_words_vectors, all_tokenized_tweets_labels)
        random.shuffle(tweets_and_labels)
        fold_size = int(0.1 * len(tweets_and_labels))
        print "Fold Size: " + str(fold_size)
        k_folds = [tweets_and_labels[i:i + fold_size] for i in xrange(0, len(tweets_and_labels), fold_size)]
        k_folds_results = []
        for i in range(len(k_folds)):
            print "Current fold: " + str(i)
            test_set_tweets = []
            training_set_tweets = []
            for j in range(len(k_folds)):
                if j != i:
                    training_set_tweets = training_set_tweets + k_folds[j]
                else:
                    test_set_tweets = test_set_tweets + k_folds[j]
            nb_model = run_naive_bayes(training_set_tweets)
            k_folds_results.append(get_test_accuracy(nb_model, test_set_tweets))
        print "K-folds Accuracies: " + str(k_folds_results)
        print "Mean Accuracy: " + str(numpy.mean(k_folds_results))
        #Run Naive Bayes on all training data
        nb_model = run_naive_bayes(tweets_and_labels)
        #Write out trained model to a file
        with open("trained_naive_bayes_model/trained_model", 'w') as f:
            pickle.dump(nb_model, f)
        with open("trained_naive_bayes_model/dictionary", 'w') as f:
            words_dict.save(f)
    elif train_or_predict == "predict":
        all_tokenized_tweets_dict = {}
        for filename in os.listdir(processed_untagged_directory):
            if filename.endswith(".csv"):
                tokenized_tweets_dict = build_tokenized_tweets_dict(filename)
                all_tokenized_tweets_dict.update(tokenized_tweets_dict)
        # Load trained Naive Bayes model from memory
        with open("trained_naive_bayes_model/trained_model", 'r') as f:
            nb_model = pickle.load(f)
        tags = nb_model.classes_
        for i in range(len(tags)):
            tags[i] = tags[i][:tags[i].find("_processed")]
        # Build list of bag of words vectors for each user and then predict their tags
        words_dict = gensim.corpora.Dictionary.load("trained_naive_bayes_model/dictionary")
        word_ids = words_dict.keys()
        print "Num Words in Dictionary: " + str(len(words_dict.keys()))
        word_to_id_dict = {}
        for word_id in word_ids:
            word_to_id_dict[words_dict.get(word_id)] = word_id
        bag_of_words_vectors_dict = {}
        user_tags_dict = {}
        for user in all_tokenized_tweets_dict:
            current_bag_of_words_vectors = []
            for tokenized_tweet in all_tokenized_tweets_dict[user]:
                current_bag_of_words_vector = [0] * len(word_ids)
                for word in tokenized_tweet:
                    if word in word_to_id_dict:
                        current_bag_of_words_vector[word_to_id_dict[word]] += 1
                current_bag_of_words_vectors.append(current_bag_of_words_vector)
            user_tag_label_counts = [0] * len(tags)
            prediction_probs = nb_model.predict_proba(current_bag_of_words_vectors)
            for predict_prob in prediction_probs:
                tag_index, prob = max(enumerate(predict_prob), key=operator.itemgetter(1))
                # Only label the tweet if the probability of the most likely tag is greater than some threshold
                if prob > 0.2:
                    user_tag_label_counts[tag_index] += 1
            user_tags_dict[user] = []
            user_output = str(user) + ": "
            for i in range(len(tags)):
                if (float(user_tag_label_counts[i]) / sum(user_tag_label_counts)) > 0.15:
                    user_tags_dict[user].append(tags[i])
                    user_output = user_output + str(tags[i]) + " "
            print user_output
        # Write out tag labels determined for each user to a file
        with open("trained_naive_bayes_model/user_tags", 'w') as f:
            for user in user_tags_dict:
                user_output = str(user) + ": "
                for tag in user_tags_dict[user]:
                    user_output = user_output + str(tag) + " "
                f.write(user_output + "\n")

