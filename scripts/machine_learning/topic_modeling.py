"""
Implements Topic Modeling Algorithms on the processed tweets in data/processed_tweets
"""
import gensim
import os
import csv
import logging
import sys
import nltk

processed_directory = "../../data/processed_tweets"

class LDASuperClass:
    """
    Super class for any LDA implementations
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

class BasicLDA(LDASuperClass):
    """
    Implements training and loading of the basic LDA model given tokenized documents
    and a list of the users
    """

    def __init__(self, all_tokenized_documents, all_processed_users):
        LDASuperClass.__init__(self, all_tokenized_documents, all_processed_users)

    def train_basic_lda(self, num_topics, num_passes):
        """
        Performs basic LDA with the given number of topics and given number of passes
        """
        #Enable logging in order to track the process of the LDA model
        logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
        self.lda_model = gensim.models.ldamodel.LdaModel(self.bag_of_words_documents, \
            num_topics=num_topics, id2word = self.dictionary, passes=num_passes)
        self.lda_model.save('trained_basic_lda_model/lda.model')
        topics_distribution = self.lda_model.show_topics(num_topics=num_topics, num_words=20)
        with open("trained_basic_lda_model/topics_distribution", 'wb') as f:
            for topic in topics_distribution:
                f.write(str(topic[0]) + " ")
                topic_words = topic[1].split("+")
                for topic_word in topic_words:
                    f.write(topic_word.strip() + " ")
                f.write("\n")

    def load_basic_lda(self):
        """
        Loads a trained LDA model from disk
        """
        self.lda_model = gensim.models.ldamodel.LdaModel.load('trained_basic_lda_model/lda.model')
        people_list = ["Ariana Grande", "Donald J. Trump", "Barack Obama", "Ellen DeGeneres",\
        "Kim Kardashian West", "Oprah Winfrey", "ESPN", "Miley Ray Cyrus", "Neil Patrick Harris"]
        for people in people_list:
            print people
            print (self.lda_model[bag_of_words_dict[people]])


class SeedWordsLDA(LDASuperClass):
    """
    Implements training and loading of an LDA model that first adjusts the 
    topic-word probability distributions based on given seed words specified 
    for each topic
    """

    def __init__(self, all_tokenized_documents, all_processed_users):
        LDASuperClass.__init__(self, all_tokenized_documents, all_processed_users)

    def build_topic_word_distributions(self, seed_words_matrix, num_topics):
        """
        Helper method for building the topic word probability distribution for each topic
        based on the given seed words matrix parameter (seed words for each topic), and 
        these distributions will be provided as a parameter to the LDA training; if the
        number of topics given exceeds the number of seed word sets, the remaining topics
        are set to a uniform probability distribution over the words
        """
        p_stemmer = nltk.stem.porter.PorterStemmer()
        topic_word_distributions = []
        num_words = len(self.dictionary.keys())
        word_to_id_dict = {}
        for word_id in self.dictionary.keys():
            word_to_id_dict[self.dictionary.get(word_id)] = word_id
        #Set assymetric probability distribution for each topic corresponding to 
        #its seed words set by setting higher probabilities for the seed words
        for i in range(len(seed_words_matrix)):
            topic_seed_words = seed_words_matrix[i]
            topic_word_distribution = [0] * num_words
            seed_words_prob_sum = 0.0
            seed_words_count = 0
            stemmed_seed_words = set()
            print "Topic " + str(i) + " Seed Words Used: "
            for seed_word in topic_seed_words:
                stemmed_word = p_stemmer.stem(seed_word)
                if (stemmed_word not in stemmed_seed_words) and \
                stemmed_word in word_to_id_dict:
                    seed_words_count = seed_words_count + 1
                    stemmed_seed_words.add(stemmed_word)
                    print seed_word
            for stemmed_seed_word in stemmed_seed_words:
                current_word_id = word_to_id_dict[stemmed_seed_word]
                topic_word_distribution[current_word_id] = 0.5 / seed_words_count
                seed_words_prob_sum = seed_words_prob_sum + (0.5 / seed_words_count)     
            regular_words_prob_sum = 1.0 - seed_words_prob_sum
            regular_words_count = num_words - seed_words_count
            for word_id in self.dictionary.keys():
                if self.dictionary.get(word_id) not in topic_seed_words:
                    topic_word_distribution[word_id] = regular_words_prob_sum / regular_words_count
            topic_word_distributions.append(topic_word_distribution)
        #Set uniform prpobability distribution over words for each remaining topic
        for j in range(num_topics - len(seed_words_matrix)):
            topic_word_distribution = [0] * num_words
            for word_id in self.dictionary.keys():
                topic_word_distribution[word_id] = 1.0 / num_words
            topic_word_distributions.append(topic_word_distribution)
        return topic_word_distributions

    def train_seed_words_lda(self, num_topics, num_passes, seed_words_matrix):
        """
        Performs LDA by first adjusting topic-word probability distributions using the
        given seed_words matrix, and then trains with the given number of topics and
        given number of passes
        """
        topic_word_distributions = self.build_topic_word_distributions(seed_words_matrix, num_topics)
        #Enable logging in order to track the process of the LDA model
        logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
        self.lda_model = gensim.models.ldamodel.LdaModel(self.bag_of_words_documents, \
            eta=topic_word_distributions, num_topics=num_topics, id2word = self.dictionary, \
            passes=num_passes)
        self.lda_model.save('trained_seed_words_lda_model/lda.model')
        topics_distribution = self.lda_model.show_topics(num_topics=num_topics, num_words=20)
        with open("trained_seed_words_lda_model/topics_distribution", 'wb') as f:
            for topic in topics_distribution:
                f.write(str(topic[0]) + " ")
                topic_words = topic[1].split("+")
                for topic_word in topic_words:
                    f.write(topic_word.strip() + " ")
                f.write("\n")

    def load_seed_words_lda(self):
        """
        Loads a trained LDA model from disk
        """
        self.lda_model = gensim.models.ldamodel.LdaModel.load('trained_seed_words_lda_model/lda.model')
        people_list = ["Ariana Grande", "Donald J. Trump", "Barack Obama", "Ellen DeGeneres",\
        "Kim Kardashian West", "Oprah Winfrey", "ESPN", "Miley Ray Cyrus", "Neil Patrick Harris"]
        for people in people_list:
            print people
            print (self.lda_model[self.bag_of_words_dict[people]])


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
    try:
        lda_model_type = sys.argv[2]
    except Exception as e:
        lda_model_type = "seed_words"
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
    if train_or_load == "train":
        try:
            #Number of topics to train from in the LDA model
            num_topics = int(sys.argv[3])
        except Exception as e:
            num_topics = 20
        try:
            #Number of iterations/passes to run for in the LDA model
            num_passes = int (sys.argv[4])
        except Exception as e:
            num_passes = 200
        if lda_model_type == "basic":
            basic_lda_model = BasicLDA(all_tokenized_documents, all_processed_users)
            basic_lda_model.train_basic_lda(num_topics, num_passes)
        elif lda_model_type == "seed_words":
            seed_matrix = []
            with open("seed_words.txt", 'r') as f:
                content = f.readlines()
                for line in content:
                    topic_seed_words = line[(line.index(":") + 1):].split(",")
                    topic_seed_words = [word.strip() for word in topic_seed_words]
                    seed_matrix.append(topic_seed_words)
            seed_words_lda_model = SeedWordsLDA(all_tokenized_documents, all_processed_users)
            seed_words_lda_model.train_seed_words_lda(num_topics, num_passes, seed_matrix)
    elif train_or_load == "load":
        if lda_model_type == "basic":
            basic_lda_model = BasicLDA(all_tokenized_documents, all_processed_users)
            basic_lda_model.load_basic_lda()
        elif lda_model_type == "seed_words":
            seed_words_lda_model = SeedWordsLDA(all_tokenized_documents, all_processed_users)
            seed_words_lda_model.load_seed_words_lda()

