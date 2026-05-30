import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

from langchain_mistralai import ChatMistralAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

load_dotenv()

app = Flask(__name__)
CORS(app)  

model = ChatMistralAI(model="mistral-small-2603", temperature=0.9)

@app.route('/chat', methods=['POST'])
def chat_endpoint():
    data = request.json
    selected_mode = data.get('mode')
    user_messages = data.get('messages', [])
    
    messages = [SystemMessage(content=selected_mode)]
    
    for msg in user_messages:
        if msg['type'] == 'human':
            messages.append(HumanMessage(content=msg['content']))
        elif msg['type'] == 'ai':
            messages.append(AIMessage(content=msg['content']))
            
    try:
        response = model.invoke(messages)
        return jsonify({"content": response.content})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)