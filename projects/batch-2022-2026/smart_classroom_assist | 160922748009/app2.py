from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import re

# Configure Gemini with your API key
genai.configure(api_key="AIzaSyAkbyZQPcLJzy9AxyaYQw4ak8fOf9OJwBw")

app = Flask(__name__)
CORS(app)  # Allow CORS for all domains

# Function to clean unwanted formatting
def clean_text(text):
    return re.sub(r"[*_`#\-]+", "", text).strip()

@app.route("/teach", methods=["POST"])
def teach_topic():
    data = request.get_json()
    topic = data.get("topic")

    if not topic:
        return jsonify({"error": "Missing topic"}), 400

    prompt = f"""You are an expert teacher explaining the topic: "{topic}" to a beginner.
Provide:
1. A clear and concise explanation (easy to understand).
2. 2 or 3 real-life examples or applications.
Avoid markdown, asterisks, or special formatting characters in your output."""

    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(prompt)
    cleaned_output = clean_text(response.text)

    return jsonify({"topic": topic, "explanation": cleaned_output})

if __name__ == "__main__":
    app.run(host='127.0.1.2', port=5000, debug=True)
