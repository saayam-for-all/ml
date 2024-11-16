import json
from flask import Flask, jsonify, request
import pickle
import sqlite3

app = Flask(__name__)

app.config.from_object(config)
db.init_app(app)

with app.app_context():
        db.create_all()

@app.route('/')
def home():
     return jsonify('Service is running')

@app.route('/api/check_profanity', methods=['POST'])
def check_profanity():
    data = request.json
    text = data['text']
    input_words = text.split()
    # connecting to the database
    conn = sqlite3.connect("profane_words.db")

    # cursor
    cursor = conn.cursor()
    query = """
        SELECT words
        FROM profane_words
        WHERE words in input_words
        """
    cursor.execute(query)
    profanity = cursor.fetchall()

    if not profanity:
        contains_profanity = False

    else:
        contains_profanity = True
    res_body = {
                "contains_profanity": contains_profanity,
                "profanity": profanity
                }
    http_res = {}
    http_res['statusCode'] = 200
    http_res['body'] = json.dumps(res_body)

    return http_res

# New API for language detection and translation
@app.route('/api/translate', methods=['POST'])
def translate_request_content():
    data = request.get_json()
    content = data.get('content', '')
    http_res = {}

    if not content:
        http_res['status_code'] = 400
        res_body = {"error": "No content provided"}
        http_res['body'] = json.dumps(res_body)

        return http_res

    # Translate the text to English
    translated_content = translate_to_english(content)

    res_body = {
        "original": content,
        "translated": translated_content
        }

    http_res['statusCode'] = 200
    http_res['body'] = json.dumps(res_body)

    return http_res

# Run the application
if __name__ in "main":
    app.run(debug = True)
