from flask import Flask, render_template, request, jsonify
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

with open('prompt.txt', 'r', encoding='utf-8') as f:
    SYSTEM_PROMPT = f.read()

client = OpenAI(
    api_key=os.getenv('OPENROUTER_API_KEY'),
    base_url='https://openrouter.ai/api/v1',
    max_retries=0
)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    data = request.json
    question = data.get('question', '')

    try:
        response = client.chat.completions.create(
            model='meta-llama/llama-3.3-70b-instruct:free',
            messages=[
                {'role': 'system', 'content': SYSTEM_PROMPT},
                {'role': 'user', 'content': question}
            ],
            max_tokens=400,
            temperature=0.7
        )
        answer = response.choices[0].message.content
        return jsonify({'answer': answer})
    except Exception as e:
        return jsonify({'answer': 'Ошибка при обработке запроса: ' + str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)