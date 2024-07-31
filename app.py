from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
from transformers import pipeline
import google.generativeai as genai
from twilio.rest import Client
from googletrans import Translator

app = Flask(__name__)

# TechCrunch Scraping
@app.route('/scrape', methods=['POST'])
def scrape():
    data = request.get_json()
    query = data.get('query', 'tech') 
    URL = f"https://techcrunch.com/?s={query}"
    r = requests.get(URL)
    soup = BeautifulSoup(r.content, 'html.parser')
    a_tags = soup.find_all('a', attrs={'data-destinationlink': True})

    links = [tag['data-destinationlink'] for tag in a_tags]
    return jsonify(links)

# Summarization
summarizer = pipeline('summarization')

@app.route('/summarize', methods=['POST'])
def summarize():
    data = request.get_json()
    text = data.get('text', '')

    if not text:
        return jsonify({"error": "No text provided"}), 400

    summary = summarizer(text, max_length=130, min_length=30, do_sample=False)
    return jsonify(summary[0]['summary_text'])

# Gemini API
genai.configure(api_key="YOUR_GOOGLE_API_KEY")
model = genai.GenerativeModel('gemini-1.5-flash')

@app.route('/search', methods=['POST'])
def searchandreturn():
    data = request.get_json()
    query = data.get("query", "")
    response = model.generate_content(query)
    return jsonify(response.text)

# Twilio Cold Calls
account_sid = "YOUR_TWILIO_ACCOUNT_SID"
auth_token = "YOUR_TWILIO_AUTH_TOKEN"
client = Client(account_sid, auth_token)

@app.route('/make_call', methods=['POST'])
def make_call():
    data = request.get_json()
    to_number = data.get('to', '')

    if not to_number:
        return jsonify({"error": "No 'to' number provided"}), 400

    try:
        call = client.calls.create(
            url="https://handler.twilio.com/twiml/YOUR_TWIML_URL",
            to=to_number,
            from_="YOUR_TWILIO_PHONE_NUMBER"
        )
        return jsonify({"message": "Call initiated successfully", "call_sid": call.sid})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Translation
translator = Translator()

@app.route('/translate', methods=['POST'])
def translate():
    data = request.get_json()
    text = data.get('text', '')
    target_lang = data.get('target', '')
    source_lang = data.get('from', '')

    if not text or not target_lang or not source_lang:
        return jsonify({"error": "Missing text, target language, or source language"}), 400

    try:
        translation = translator.translate(text, src=source_lang, dest=target_lang)
        return jsonify({"translated_text": translation.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/')
def hello_world():
    return 'Hello from Flask!'

if __name__ == '__main__':
    app.run(debug=True)
