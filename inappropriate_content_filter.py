import json
import sqlite3
import string
import os

# from huggingface_hub import InferenceClient
from groq import Groq

import boto3



def lambda_handler(event, context):
    body = json.loads(event['body'])
    subject = body.get('subject')
    description = body.get('description')
    text = subject + " " + description

    # Remove punctuation
    translator = str.maketrans('', '', string.punctuation)
    clean_text = text.translate(translator).lower()
    input_words = clean_text.split()

    # ---- Singular form handling ----
    singular_words = ['ass', 'dumbass', 'piss']
    for i, word in enumerate(input_words):
        if word in singular_words:
            continue
        if word.endswith("ies"):
            input_words[i] = word[:-3] + "y"
        elif word.endswith("es") and len(word) > 2:
            input_words[i] = word[:-2]
        elif word.endswith("s") and len(word) > 1:
            input_words[i] = word[:-1]

    # ---- Connect to SQLite DB ----
    db_path = os.path.join(os.getcwd(), 'profane_words.db')

    if not os.path.exists(db_path):
        return {"statusCode": 500, "body": "Database file not found"}

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Integrity check
    cursor.execute("PRAGMA integrity_check;")
    if cursor.fetchone()[0] != "ok":
        raise ValueError("Database integrity check failed.")

    # ---- Helper function for table lookup ----
    def lookup(table):
        placeholders = ",".join("?" for _ in input_words)
        query = f"SELECT words FROM {table} WHERE words IN ({placeholders})"
        cursor.execute(query, input_words)
        return [row[0] for row in cursor.fetchall()]

    # ---- Keyword detection ----
    profane_words = lookup("profane_words")
    depressive_words = lookup("depressive_suicidal_terms")
    threatening_words = lookup("threatening_language")

    conn.close()

    try:
        ssm = boto3.client('ssm', region_name='us-east-1')
        api_key = ssm.get_parameter(Name = '/dev/saayam/GenAI/groq/key', WithDecryption = True)

        if not api_key:
            raise ValueError("API Key not found. Please check your .env file.")
        # client = InferenceClient(api_key = api_key)
        client = Groq(api_key = api_key)

        response = client.chat.completions.create(
        model = "openai/gpt-oss-120b",
        messages = [

            {
                "role": "user",
                "content": f""" You are a multilingual moderation assistant.

                Determine whether the text has depressive content, suicidal language, or threatening language.

                Return it as a JSON object in the following format:

                    "contains_depressive_content": contains_depressive_content,
                    "contains_suicidal_content": contains_suicidal_content,
                    "2. Depressive/Suicidal Content": depressive_suicidal_words,

                    "contains_threatening_content": contains_threatening_content,
                    "3. Threatening Content": threatening_words

                Text: {clean_text}
                """
            }
            ]
        )
        llm_response = response.choices[0].message.content
        llm_response = llm_response.replace("```json", "").replace("```", "").strip()
        llm_dict = json.loads(llm_response)

    except:
        llm_dict = { "status_code": 500,
                "Error": "Invalid API key or issue with the model",
                "contains_depressive_content": False,
                "contains_suicidal_content": False,
                "2. Depressive/Suicidal Content": [],

                "contains_threatening_content": False,
                "3. Threatening Content": []
                }

    finally:
        profanity_dict = {
            "contains_profanity": bool(profane_words),
            "1. profanity": profane_words
            }

        # ---- Final Response ----
        response_data = profanity_dict | llm_dict

        if not response_data["contains_profanity"] and not response_data["contains_depressive_content"] and not response_data["contains_suicidal_content"] and not response_data["contains_threatening_content"]:
            normal_dict = {"0. This is a normal request": []}
            response_data = normal_dict | response_data

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": '*'
            },
            "body": json.dumps(response_data)
            }



if __name__ == "__main__":
    test_phrases = [
    "I've been feeling down, and there is no hope.",                 # English Depressive
    "Me siento increíblemente solo, vacío y que nada va a mejorar.", # Spanish Depressive
    "I'm feeling very happy today.",                                 # English Happy (Normal)
    "Hoy fui al supermercado y compré algunas frutas.",              # Spanish Normal
    "Get out of my way or you will regret it.",                     # English Threat
    "Te voy a buscar y lo vas a pagar muy caro."                    # Spanish Threat
    ]
    event = {
        "body": "{ \"subject\": \"Hi\", \"description\": \"Get out of my way or you will regret.\" }"
        }
    print(lambda_handler(event, ""))
