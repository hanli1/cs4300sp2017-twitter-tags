"""
Implements Topic Modeling Algorithms on the processed tweets in data/processed_tweets
"""
import gensim
import os
import csv
import logging
import sys

processed_directory = "../../data/processed_tweets"

class BasicLDA:
    """
    Implements training and loading of the basic LDA model given tokenized documents
    and a list of the users
    """
    
    def __init__(self, all_tokenized_documents, all_processed_users):
        """
        Performs initializations necessary for the LDA model; specifically, prepares
        the bag of words for each document
        """
        docs_to_consider = all_tokenized_documents[:500]
        self.dictionary = gensim.corpora.Dictionary(docs_to_consider)
        self.dictionary.filter_extremes(no_below=5, no_above=0.5, keep_n=100000)
        self.bag_of_words_documents = [self.dictionary.doc2bow(doc) for doc in docs_to_consider]
        #Mapping from a user to the bag of words of their tweets
        self.bag_of_words_dict  = {}
        for i in range(len(self.bag_of_words_documents)):
            self.bag_of_words_dict[all_processed_users[i]] = self.bag_of_words_documents[i]
        self.lda_model = None

    def train_basic_lda(self, num_topics, num_passes):
        """
        Given a list of tokenized documents, performs LDA on these documents
        """
        #Enable logging in order to track the process of the LDA model
        logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
        lda_model = gensim.models.ldamodel.LdaModel(self.bag_of_words_documents, \
            num_topics=num_topics, id2word = self.dictionary, passes=num_passes)
        lda_model.save('trained_basic_lda_model/lda.model')
        topics_distribution = lda_model.show_topics(num_topics=2, num_words=20)
        with open("trained_basic_lda_model/topics_distribution", 'wb') as f:
            for topic_distribution in topics_distribution:
                f.write(str(topic_distribution[0]) + " ")
                topic_words = topic_distribution[1].split("+")
                for topic_word in topic_words:
                    f.write(topic_word.strip() + " ")
                f.write("\n")

    def load_basic_lda(self):
        """
        Loads a trained LDA model from disk
        """
        lda_model = gensim.models.ldamodel.LdaModel.load('trained_basic_lda_model/lda.model')
        print(self.lda_model[bag_of_words_dict["Ariana Grande"]])
        print(self.lda_model[bag_of_words_dict["Donald J. Trump"]])


def build_tokenized_documents_list(file_name):
    """
    Build tokenized documents from the tweets of each user from the given file
    """
    tokenized_documents = []
    processed_users = []
    with open(os.path.join(processed_directory, file_name), 'rb') as f:
        reader = csv.reader(f)
        current_tokenized_document = []
        current_user = ""
        for a, b, line in reader:
            tokens = line.split()
            if current_user == "":
                current_user = b
                print current_user
                processed_users.append(b)
            elif b != current_user:
                tokenized_documents.append(current_tokenized_document)
                current_user = b
                print current_user
                current_tokenized_document = []
                processed_users.append(b)
            current_tokenized_document = current_tokenized_document + tokens
        tokenized_documents.append(current_tokenized_document)
    return (processed_users, tokenized_documents)


if __name__ == "__main__":
    try:
        train_or_load = sys.argv[1]
    except Exception as e:
        train_or_load = "train"
    #Will contain all tokenized documents, where each document corresponds to all
    #the tweets of the user
    all_tokenized_documents = []
    #List of the processed users corresponding to the order of the tokenized documents
    all_processed_users = []
    for filename in os.listdir(processed_directory):
        if filename.endswith(".csv"): 
            processed_users, tokenized_documents = build_tokenized_documents_list(filename)
            all_tokenized_documents = all_tokenized_documents + tokenized_documents
            all_processed_users = all_processed_users + processed_users
    basic_lda_model = BasicLDA(all_tokenized_documents, all_processed_users)
    if train_or_load == "train":
        try:
            #Number of topics to train from in the LDA model
            num_topics = int(sys.argv[2])
        except Exception as e:
            num_topics = 20
        try:
            #Number of iterations/passes to run for in the LDA model
            num_passes = int (sys.argv[3])
        except Exception as e:
            num_passes = 200
        basic_lda_model.train_basic_lda(num_topics, num_passes)
    elif train_or_load == "load":
        basic_lda_model.load_basic_lda()



