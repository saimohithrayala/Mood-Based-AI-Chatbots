import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

from langchain_mistralai import ChatMistralAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # This allows your local React web interface to connect securely

# Your exact model setup
model = ChatMistralAI(model="mistral-small-2603", temperature=0.9)

@app.route('/chat', methods=['POST'])
def chat_endpoint():
    data = request.json
    
    # 1. Grab the system matrix string and conversation array sent from React
    selected_mode = data.get('mode')
    user_messages = data.get('messages', [])
    
    # 2. Re-compile your messages log array starting with your SystemMessage
    messages = [SystemMessage(content=selected_mode)]
    
    for msg in user_messages:
        if msg['type'] == 'human':
            messages.append(HumanMessage(content=msg['content']))
        elif msg['type'] == 'ai':
            messages.append(AIMessage(content=msg['content']))
            
    try:
        # 3. Exactly like your original while loop invocation
        response = model.invoke(messages)
        return jsonify({"content": response.content})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Starts your backend on port 5000
    app.run(port=5000, debug=True)