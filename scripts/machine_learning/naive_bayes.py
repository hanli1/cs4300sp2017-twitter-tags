from sklearn.naive_bayes import MultinomialNB
import os
import csv
import gensim
import numpy

processed_tagged_directory = "../../data/processed_tweets/tagged"


def run_naive_bayes(training_set):
    nb = MultinomialNB()
    training_tweets = []
    training_labels = []
    for (bag_of_words, label) in training_set:
        training_tweets.append(bag_of_words)
        training_labels.append(label)
    nb.fit(training_tweets, training_labels)
    return nb

def test_accuracy(nb_model, test_set):
    num_examples = 0
    correct_examples = 0
    for (bag_of_words, label) in test_set:
        predicted_label = nb_model.predict(bag_of_words)[0]
        if label == predicted_label:
            correct_examples = correct_examples + 1
        num_examples = num_examples + 1
    print str(correct_examples)
    print str(num_examples)
    print "Test Set Accuracy" + str(float(correct_examples)/num_examples)


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
    return tokenized_tweets


if __name__ == "__main__":
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
    bag_of_words_tweets = [words_dict.doc2bow(tweet) for tweet in all_tokenized_tweets]
    bag_of_words_vectors = []
    for bag_of_words_tweet in bag_of_words_tweets:
        bag_of_words_vector = [0]*len(words_dict.keys())
        for (word_index, word_count) in bag_of_words_tweet:
            bag_of_words_vector[word_index] = word_count
        bag_of_words_vectors.append(bag_of_words_vector)
    #Randomly select 90% of tweets for training, and the remaining 10% as the test set
    training_set_indices = set(numpy.random.choice(range(len(all_tokenized_tweets)), \
        int(0.9 * len(all_tokenized_tweets)), replace=False))
    test_set_tweets = []
    training_set_tweets = []
    for i in range(len(all_tokenized_tweets)):
        if i in training_set_indices:
            training_set_tweets.append((bag_of_words_vectors[i], all_tokenized_tweets_labels[i]))
        else:
            test_set_tweets.append((bag_of_words_vectors[i], all_tokenized_tweets_labels[i]))
    nb_model = run_naive_bayes(training_set_tweets)
    test_accuracy(nb_model, test_set_tweets)



