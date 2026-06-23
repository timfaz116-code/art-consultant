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

    max_retries = 3
    retry_delay = 5

    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model='openrouter/free',
                messages=[
                    {'role': 'system', 'content': SYSTEM_PROMPT},
                    {'role': 'user', 'content': question}
                ],
                max_tokens=300,
                temperature=0.7,
                timeout=60
            )
            answer = response.choices[0].message.content
            if response.choices[0].finish_reason == 'length':
                answer += '\n\n[Ответ обрезан из-за ограничения длины. Задайте уточняющий вопрос.]'
            return jsonify({'answer': answer})
        except Exception as e:
            if '429' in str(e) and attempt < max_retries - 1:
                import time
                time.sleep(retry_delay * (attempt + 1))
                continue
            return jsonify({'answer': 'Слишком много запросов к бесплатной модели. Попробуйте через минуту. Ошибка: ' + str(e)}), 429

if __name__ == '__main__':
    app.run(debug=True)