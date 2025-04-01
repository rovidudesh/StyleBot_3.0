from flask import render_template, request, jsonify, session
from app import app
from models import db, UserSession, ChatMessage
import uuid
import requests
import json

@app.route('/')
def home():
    session.clear()
    return render_template('index.html')

@app.route('/start_chat', methods=['POST'])
def start_chat():
    session_id = str(uuid.uuid4())
    session['session_id'] = session_id
    
    body_type = request.form.get('body_type')
    height = request.form.get('height')
    gender = request.form.get('gender')
    
    new_session = UserSession(
        session_id=session_id,
        body_type=body_type,
        height=height,
        gender=gender
    )
    db.session.add(new_session)
    db.session.commit()
    
    initial_prompt = f"""
    You are StyleBot, a virtual fashion stylist assistant. The user is a {gender}, 
    {height} tall with a {body_type} body type. Start by welcoming them and asking 
    what occasion they need styling help for. Keep responses concise and in bullet points.
    """
    
    bot_response = generate_response(initial_prompt, [])
    save_message(session_id, bot_response, is_bot=True)
    
    return jsonify({
        'session_id': session_id,
        'bot_response': bot_response
    })

@app.route('/send_message', methods=['POST'])
def send_message():
    session_id = session.get('session_id')
    if not session_id:
        return jsonify({'error': 'Session not found'}), 400
    
    user_message = request.form.get('message')
    save_message(session_id, user_message, is_bot=False)
    
    conversation_history = get_conversation_history(session_id)
    user_session = UserSession.query.filter_by(session_id=session_id).first()
    
    context = f"""
    User details:
    - Gender: {user_session.gender}
    - Height: {user_session.height}
    - Body type: {user_session.body_type}
    - Style preferences: {user_session.style_preferences or 'Not specified'}
    - Color preferences: {user_session.color_preferences or 'Not specified'}
    """
    
    bot_response = generate_response(context, conversation_history)
    save_message(session_id, bot_response, is_bot=True)
    update_user_preferences(session_id, user_message, bot_response)
    
    return jsonify({'bot_response': bot_response})

@app.route('/new_chat', methods=['POST'])
def new_chat():
    session.clear()
    return jsonify({'status': 'success'})

def generate_response(context, history):
    messages = [
        {"role": "system", "content": """You are StyleBot, a friendly virtual fashion stylist. 
        Provide personalized outfit recommendations based on user details. Keep responses:
        - Concise (3-5 bullet points max)
        - Use emojis where appropriate
        - Suggest complete outfits
        - Ask follow-up questions to refine suggestions"""}
    ]
    
    messages.append({"role": "system", "content": context})
    
    for msg in history[-6:]:
        role = "assistant" if msg['is_bot'] else "user"
        messages.append({"role": role, "content": msg['message']})
    
    try:
        headers = {
            "Authorization": f"Bearer {app.config['OPENROUTER_API_KEY']}",
            "HTTP-Referer": "http://localhost:5000",
            "X-Title": app.config['OPENROUTER_APP_NAME'],
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "openai/gpt-3.5-turbo",
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 150
        }
        
        response = requests.post(
            app.config['OPENROUTER_API_URL'],
            headers=headers,
            data=json.dumps(payload),
            timeout=10
        )
        
        if response.status_code == 200:
            try:
                response_data = response.json()
                if 'choices' in response_data and len(response_data['choices']) > 0:
                    return response_data['choices'][0]['message']['content'].strip()
            except ValueError:
                print("Invalid JSON response from OpenRouter")
            return "Sorry, I received an unexpected response. Please try again."
        else:
            print(f"OpenRouter Error: {response.status_code} - {response.text}")
            return "Sorry, I'm having trouble generating a response. Please try again."
            
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {str(e)}")
        return "Sorry, there was a connection error. Please check your internet and try again."
    except Exception as e:
        print(f"Error generating response: {str(e)}")
        return "Sorry, I'm having trouble generating a response. Please try again."

def save_message(session_id, message, is_bot):
    new_message = ChatMessage(
        session_id=session_id,
        message=message,
        is_bot=is_bot
    )
    db.session.add(new_message)
    db.session.commit()

def get_conversation_history(session_id):
    messages = ChatMessage.query.filter_by(session_id=session_id).order_by(ChatMessage.timestamp.asc()).all()
    return [{
        'message': msg.message,
        'is_bot': msg.is_bot,
        'timestamp': msg.timestamp.isoformat()
    } for msg in messages]

def update_user_preferences(session_id, user_message, bot_response):
    user_session = UserSession.query.filter_by(session_id=session_id).first()
    if not user_session:
        return
    
    update_needed = False
    
    if 'like styles' in user_message.lower() or 'prefer styles' in user_message.lower():
        user_session.style_preferences = extract_preferences(user_message)
        update_needed = True
    
    if 'like colors' in user_message.lower() or 'favorite color' in user_message.lower():
        user_session.color_preferences = extract_preferences(user_message)
        update_needed = True
    
    if update_needed:
        db.session.commit()

def extract_preferences(text):
    text = text.lower()
    if 'casual' in text:
        return 'casual'
    elif 'formal' in text:
        return 'formal'
    elif 'sport' in text:
        return 'sporty'
    elif 'bohemian' in text:
        return 'bohemian'
    elif 'vintage' in text:
        return 'vintage'
    elif 'minimalist' in text:
        return 'minimalist'
    return None