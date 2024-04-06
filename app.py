from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

API_KEY = "AIzaSyAvXDlCJP8MtdANPlwtU0fzuPYCHjjBOms"

@app.route('/')
def home():
    return render_template('index.html', generated_response=None)

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
        response = requests.post(f'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={API_KEY}', json=data, headers=headers)
        response.raise_for_status()  
        
        response_json = response.json()
        candidates = response_json.get("candidates", [])
        if candidates:
            content = candidates[0].get("content", {})
            parts = content.get("parts", [])
            if parts:
                first_part = parts[0]
                generated_response = first_part.get("text", "")
                return jsonify({"response": generated_response})

        return jsonify({"error": "No suitable response found"})

    except requests.exceptions.HTTPError as http_err:
        return jsonify({"error": f"HTTP error occurred: {http_err}"}), 500
    except Exception as err:
        return jsonify({"error": f"An unexpected error occurred: {err}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
