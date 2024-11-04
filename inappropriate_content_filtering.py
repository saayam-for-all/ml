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

from flask import Flask, jsonify, request
import pickle

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

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer

# Create a TfidfVectorizer object
vectorizer = TfidfVectorizer()
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

@app.route('/api/classify_text', methods=['POST'])
def classify_text():
    data = request.json
    clean_data = clean_text(data['text'])
    text = remove_stopwords(clean_data)
    # Load the model
    with open('model.pkl', 'rb') as f:
        model = pickle.load(f)
    pred = model.predict(text)

    return jsonify(pred), 200



if __name__ in "main":
    app.run(debug=True)
