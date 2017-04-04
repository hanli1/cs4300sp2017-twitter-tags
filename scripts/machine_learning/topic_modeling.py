"""
Implements Topic Modeling Algorithms on the processed tweets in data/processed_tweets
"""
import gensim
import os
import csv
import logging

processed_directory = "../../data/processed_tweets"

def run_basic_lda(all_tokenized_documents, all_processed_users):
    """
    Given a list of tokenized documents, performs LDA on these documents
    """
    docs_to_consider = all_tokenized_documents[:100]
    dictionary = gensim.corpora.Dictionary(docs_to_consider)
    print(len(dictionary.keys()))
    print(len(dictionary.values()))
    bag_of_words_documents = [dictionary.doc2bow(doc) for doc in docs_to_consider]
    #Mapping from a user to the bag of words of their tweets
    bag_of_words_dict  = {}
    for i in range(len(bag_of_words_documents)):
        bag_of_words_dict[all_processed_users[i]] = bag_of_words_documents[i]
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
    lda_model = gensim.models.ldamodel.LdaModel(bag_of_words_documents, num_topics=20, \
        id2word = dictionary, passes=200)
    print(lda_model.print_topics(num_topics=20, num_words=5))
    print(lda_model[bag_of_words_dict["Ariana Grande"]])
    print(lda_model[bag_of_words_dict["Donald J. Trump"]])
    print(lda_model[bag_of_words_dict["Al Yankovic"]])


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
    run_basic_lda(all_tokenized_documents, all_processed_users)




