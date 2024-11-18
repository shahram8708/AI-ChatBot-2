from flask import Flask, render_template, request, jsonify
import requests
import re

app = Flask(__name__)

API_KEY = "API_Key"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/generate-content', methods=['POST'])
def generate_content():
    user_input = request.json.get('userInput')

    if not user_input:
        return jsonify({"error": "User input not provided"}), 400

    headers = {'Content-Type': 'application/json'}
    data = {
        "contents": [{
            "parts": [{
                "text": user_input
            }]
        }]
    }

    try:
        response = requests.post(
            f'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={API_KEY}',
            json=data,
            headers=headers
        )
        response.raise_for_status()
        
        response_json = response.json()
        print(response_json) 
        candidates = response_json.get("candidates", [])
        if candidates:
            content = candidates[0].get("content", {})
            parts = content.get("parts", [])
            if parts:
                first_part = parts[0]
                generated_response = first_part.get("text", "")
                return jsonify({"response": format_message(generated_response)})

        return jsonify({"error": "No suitable response found"})

    except requests.exceptions.HTTPError as http_err:
        return jsonify({"error": f"HTTP error occurred: {http_err}"}), 500
    except Exception as err:
        return jsonify({"error": f"An unexpected error occurred: {err}"}), 500

def format_message(message):
    formatted_message = re.sub(r'\n', '<br>', message)
    formatted_message = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', formatted_message)
    formatted_message = re.sub(r'__(.*?)__', r'<strong>\1</strong>', formatted_message)
    formatted_message = re.sub(r'\*(.*?)\*', r'<em>\1</em>', formatted_message)
    formatted_message = re.sub(r'_(.*?)_', r'<em>\1</em>', formatted_message)
    formatted_message = re.sub(r'\*\*\*(.*?)\*\*\*', r'<strong><em>\1</em></strong>', formatted_message)
    formatted_message = re.sub(r'___(.*?)___', r'<strong><em>\1</em></strong>', formatted_message)
    formatted_message = re.sub(r'~~(.*?)~~', r'<del>\1</del>', formatted_message)
    formatted_message = re.sub(r'`([^`]*)`', r'<code>\1</code>', formatted_message)
    formatted_message = re.sub(r'```([^`]*)```', r'<pre><code>\1</code></pre>', formatted_message)
    formatted_message = re.sub(r'^> (.*)', r'<blockquote>\1</blockquote>', formatted_message, flags=re.MULTILINE)
    formatted_message = re.sub(r'^\* (.*)', r'<ul><li>\1</li></ul>', formatted_message, flags=re.MULTILINE)
    formatted_message = re.sub(r'^- (.*)', r'<ul><li>\1</li></ul>', formatted_message, flags=re.MULTILINE)
    formatted_message = re.sub(r'^\d+\. (.*)', r'<ol><li>\1</li></ol>', formatted_message, flags=re.MULTILINE)
    formatted_message = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2">\1</a>', formatted_message)
    formatted_message = re.sub(r'\!\[(.*?)\]\((.*?)\)', r'<img src="\2" alt="\1">', formatted_message)
    formatted_message = re.sub(r'^# (.*)', r'<h1>\1</h1>', formatted_message, flags=re.MULTILINE)
    formatted_message = re.sub(r'^## (.*)', r'<h2>\1</h2>', formatted_message, flags=re.MULTILINE)
    formatted_message = re.sub(r'^### (.*)', r'<h3>\1</h3>', formatted_message, flags=re.MULTILINE)
    formatted_message = re.sub(r'^#### (.*)', r'<h4>\1</h4>', formatted_message, flags=re.MULTILINE)
    formatted_message = re.sub(r'^##### (.*)', r'<h5>\1</h5>', formatted_message, flags=re.MULTILINE)
    formatted_message = re.sub(r'^###### (.*)', r'<h6>\1</h6>', formatted_message, flags=re.MULTILINE)
    return formatted_message

if __name__ == '__main__':
    app.run(debug=True)
