from flask import Flask, render_template, request, jsonify, session
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import uuid

app = Flask(__name__)
app.secret_key = 'liaplus_secret'
analyzer = SentimentIntensityAnalyzer()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    session_id = session.get('id', str(uuid.uuid4()))
    session['id'] = session_id
    
    user_msg = request.json['message']
    responses = {
        'hi': 'Hello! How can I help?',
        'help': 'I can chat and analyze your sentiment.',
        'bye': 'Goodbye!',
        'default': 'Tell me more about your experience.'
    }
    bot_response = responses.get(user_msg.lower(), responses['default'])
    
    if 'history' not in session:
        session['history'] = []
    session['history'].append({'user': user_msg, 'bot': bot_response})
    session.modified = True
    
    sentiment = analyzer.polarity_scores(user_msg)
    compound = sentiment['compound']
    if compound >= 0.05:
        sent_label = 'Positive'
    elif compound <= -0.05:
        sent_label = 'Negative'
    else:
        sent_label = 'Neutral'
    
    return jsonify({
        'response': bot_response,
        'sentiment': sent_label,
        'score': compound
    })

@app.route('/analyze')
def analyze():
    history = session.get('history', [])
    if not history:
        return jsonify({'overall': 'No conversation yet', 'details': []})
    
    all_user_text = ' '.join([msg['user'] for msg in history])
    overall_sent = analyzer.polarity_scores(all_user_text)
    overall_label = 'Positive' if overall_sent['compound'] >= 0.05 else 'Negative' if overall_sent['compound'] <= -0.05 else 'Neutral'
    
    details = []
    scores = [analyzer.polarity_scores(msg['user'])['compound'] for msg in history]
    trend = 'Improving' if scores[-1] > scores[0] else 'Declining' if scores[-1] < scores[0] else 'Stable'
    
    for msg in history:
        sent = analyzer.polarity_scores(msg['user'])
        label = 'Positive' if sent['compound'] >= 0.05 else 'Negative' if sent['compound'] <= -0.05 else 'Neutral'
        details.append({'user': msg['user'], 'sentiment': label})
    
    return jsonify({
        'overall': f"{overall_label} (general {'satisfaction' if overall_label == 'Positive' else 'dissatisfaction'})",
        'trend': trend,
        'details': details
    })

if __name__ == '__main__':
    app.run(debug=True)

