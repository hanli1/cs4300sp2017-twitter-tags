import re, nltk, os, sys, pickle, numpy as np
from tweet_retriever import get_user_tweets
from sklearn.feature_extraction.text import CountVectorizer
from project_template.cos_sim import pickle_directory

N = 200 # number of tweets to fetch for live user
emoji_pattern = re.compile(
    u"(\ud83d[\ude00-\ude4f])|"  # emoticons
    u"(\ud83c[\udf00-\uffff])|"  # symbols & pictographs (1 of 2)
    u"(\ud83d[\u0000-\uddff])|"  # symbols & pictographs (2 of 2)
    u"(\ud83d[\ude80-\udeff])|"  # transport & map symbols
    u"(\ud83c[\udde0-\uddff])"  # flags (iOS)
    "+", flags=re.UNICODE)
p_stemmer = nltk.stem.porter.PorterStemmer()

def preprocess(tweet) :
    # remove links
    content = re.sub(r'http\S+', '', tweet, flags=re.MULTILINE)
    content = content.decode('utf-8')
    # remove emojis
    content = re.sub(emoji_pattern, "", content)
    content = content.lower()
    initial_tokens = re.findall(r"[\w']+|[.,!?;]", content)
    # remove punctuation
    tokens = [token for token in initial_tokens if not token in ".,!?;\"'"]
    # perform stemming
    tokens = [p_stemmer.stem(token) for token in tokens]
    return tokens

# gets N tweets of a user handle : username
def get_tweets(username) :
    return get_user_tweets(username, 0, N)

# preprocess and build doc
def build_doc(raw_tweets) :
    doc = []
    for line in raw_tweets.values()[0] :
        preprocessed_tweet = preprocess(line[-1])
        if preprocessed_tweet :
            doc += preprocessed_tweet
    return doc

# returns top 5 words in common
def top_words_in_common(tfid_query_vec, doc_vec, inv_features_dict) :
    top_indices = np.argsort(np.multiply(tfid_query_vec, doc_vec))[:5]
    return [inv_features_dict[index] for index in top_indices]

# get similarities to doc using stored tfidf matrix
def get_similarities(doc) :
    with open(os.path.join(pickle_directory, 'features_dict.pickle'), 'rb') as handle:
        features_dict = pickle.load(handle)
        inv_features_dict = {index : feature for feature, index in features_dict.items()}

    with open(os.path.join(pickle_directory, 'index_to_user.pickle'), 'rb') as handle:
        index_to_user_map = pickle.load(handle)

    count_vec = CountVectorizer(stop_words='english', vocabulary=features_dict)
    query_vec = count_vec.fit_transform([' '.join(doc)]).toarray()[0]

    with open(os.path.join(pickle_directory, 'idfs.pickle'), 'rb') as handle:
        idfs = pickle.load(handle)

    tfid_query_vec = np.multiply(idfs, query_vec) # get tfidf vector
    tfid_query_vec = tfid_query_vec / np.linalg.norm(tfid_query_vec) # normalize
    tfidf_matrix = np.load(os.path.join(pickle_directory, 'user_by_vocab.pickle'))

    similarities = tfidf_matrix.dot(tfid_query_vec)

    return [
        {
        "cosine_similarity": similarities[i],
        "name": index_to_user_map[i],
        "top_words_in_common": top_words_in_common(tfid_query_vec, tfidf_matrix[i], inv_features_dict)
        }
        for i in np.argsort(similarities)[::-1] ]

def get_live_similarities(handle) :
    try :
        return get_similarities(build_doc(get_tweets(handle)))
    except Exception as e:
        print e
        return [] # no output

if __name__ == "__main__" :
    print(get_live_similarities('@BarackObama'))