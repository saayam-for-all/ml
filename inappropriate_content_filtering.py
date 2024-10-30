# -*- coding: utf-8 -*-
"""Bad-Content-Filtering.ipynb
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import re
import string
import warnings
from nltk.tokenize import word_tokenize
warnings.filterwarnings("ignore")
nltk.download("stopwords")
nltk.download("wordnet")
nltk.download("punkt")
nltk.download("omw-1.4")
from wordcloud import WordCloud
from textblob import TextBlob

from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/')
def home():
     return jsonify('Service is running')

#from google.colab import drive
#drive.mount('/content/gdrive')

@app.route('/api/clean_text', methods=['POST'])
def clean_text(text):

    text = str(text).lower()

    text = re.sub('<.*?>+', '',text)

    text = re.sub('https?://\S+|www\.\S+', '', text)

    text = re.sub('[%s]' % re.escape(string.punctuation), '', text)
    text = re.sub('rt', '',text)
    text = re.sub('\d', '',text)
    text = re.sub('\w*\d\w*', '', text)

    text = re.sub('  ',' ',text)



    return text

sw = set(stopwords.words("english"))

@app.route('/api/remove_stopwords', methods=['POST'])
def remove_stopwords(text):
    tokens = word_tokenize(text)
    cleaned_tokens = [word for word in tokens if word.lower() not in sw]
    return " ".join(cleaned_tokens)

tweet_data = pd.read_csv('labeled_data.csv', encoding = "utf-8")
text = " ".join(i for i in tweet_data['tweet'])


from wordcloud import WordCloud


wordcloud = WordCloud(
    background_color="#6B5B95",
    colormap="Set2",
    collocations=False).generate(text)

plt.figure(figsize=(10,6))
plt.imshow(wordcloud, interpolation="bilinear")
plt.axis("off")
plt.title("Bad Tweets By Bad People")
plt.show()

#most frequent words


print(text.count("bitch"))
print(text.count("bitches"))
print(text.count("nigga"))
print(text.count("niggas"))
print(text.count("hoe"))
print(text.count("trash"))
print(text.count("pussy"))
print(text.count("fuck"))
print(text.count("fucking"))
print(text.count("love"))
print(text.count("faggot"))

#hate_tweet = (tweet_data['sentiment'] == "Hate_Speech").astype('int32')
#neither = (tweet_data['sentiment'] == "Neither").astype('int32')

#sns.countplot(x = hate_tweet)
#plt.show()

#sns.countplot(x = neither)
#plt.show()

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer

# Create a TfidfVectorizer object
vectorizer = TfidfVectorizer()

def create_data():
    tweet_data = pd.read_csv('labeled_data.csv', encoding = "utf-8")
    print(tweet_data.shape)

    tweet_data.columns

    tweet_data.head()

    tweet_data.isna().sum()

    tweet_data.describe()

    for col in tweet_data[['count', 'hate_speech', 'offensive_language', 'neither',
           'class']]:
        sns.histplot(tweet_data[col])
        plt.show()

    tweet_data[tweet_data['hate_speech']>0].describe()

    tweet_data[tweet_data['offensive_language']>0].describe()

    tweet_data[tweet_data['neither']>0].describe()

    tweet_data['class'].hist()

    tweet_data['sentiment'] = tweet_data['class'].map({0:'Hate_Speech',1:'offensive_language',
                                      2: 'Neither'})
    fig, axs = plt.subplots(figsize=(6,5))
    sns.countplot(x='sentiment',data = tweet_data,ax=axs)
    axs.set_xticklabels(axs.get_xticklabels(),rotation=40,ha="right")
    plt.tight_layout()
    plt.show()
    

    tweet_data['tweet'] = tweet_data['tweet'].apply(clean_text)
    tweet_data['tweet'] = tweet_data['tweet'].apply(remove_stopwords)
    X = tweet_data['tweet']
    y = tweet_data['class']

    X_train,X_test,y_train,y_test = train_test_split(X,y,test_size=.20,random_state=42)

    return X_train, X_test, y_train, y_test

from sklearn.linear_model import LogisticRegression
lr = LogisticRegression()

from sklearn.metrics import accuracy_score,classification_report

@app.route('/api/evaluate_model', methods=['POST'])
def evaluate_model(X_train,X_test,y_train,y_test,model):
    X_train = vectorizer.fit_transform(X_train)
    # Transform the test data using the same vectorizer
    X_test = vectorizer.transform(X_test)
    model = model.fit(X_train,y_train)
    pred = model.predict(X_test)
    acc = accuracy_score(y_test,pred)
    clf_rpt = classification_report(y_test,pred)
    print(f'{model.__class__.__name__}, --Accuracy-- {acc*100:.2f}%; --Clf RPT-- {clf_rpt}')
    return pred

#lr_pred = evaluate_model(X_train, X_test, y_train, y_test, lr)

@app.route('/api/classify_text', methods=['POST'])
def classify_text():
    data = request.json
    clean_data = clean_text(data['text'])
    text = remove_stopwords(clean_data)
    X_train, X_test, y_train, y_test = create_data()
    model = model.fit(X_train, y_train)
    pred = model.predict(text)

    return jsonify(pred), 200



if __name__ in "main":
    app.run(debug=True)
