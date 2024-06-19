import os
import requests
import markdown
from flask import Flask, request, jsonify, render_template_string, redirect, session, url_for
from openai import OpenAI
from flask_session import Session

app = Flask(__name__)
app.secret_key = '4114'  # Replace with a secure key
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# Constants for Strava API
CLIENT_ID = '125867'
CLIENT_SECRET = 'c8488d2be97f69ae395f9954531b5a09ab37b8e1'
REDIRECT_URI = 'http://localhost/exchange_token'
AUTH_URL = (
    f"https://www.strava.com/oauth/authorize?client_id={CLIENT_ID}&response_type=code"
    f"&redirect_uri={REDIRECT_URI}&approval_prompt=force&scope=read"
)
TOKEN_URL = "https://www.strava.com/oauth/token"
ATHLETE_ID = '55382335'

# Constants for OpenAI API
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

@app.route('/')
def home():
    access_token = session.get('access_token')
    return render_template_string('''
        <h1>Welcome to My Strava CLI</h1>
        <ul>
            <li><a href="/auth">Authenticate with Strava</a></li>
            {% if access_token %}
            <li><a href="/get_stats">Get Athlete Stats</a></li>
            <li><a href="/ai_analysis">AI Analysis of Your Stats</a></li>
            {% endif %}
            <li><a href="/exit">Exit</a></li>
        </ul>
    ''', access_token=access_token)

@app.route('/auth')
def authenticate():
    return render_template_string(f'''
        <h1>Please authenticate with Strava:</h1>
        <p>Please visit the following link to authorize the application:</p>
        <a href="{AUTH_URL}" target="_blank">{AUTH_URL}</a>
        <p>After authorizing the application, you will be redirected to a URL starting with 'localhost'.</p>
        <p>Copy the 'code' parameter from that URL and paste it below.</p>
        <form action="/get_token" method="post">
            <input type="text" name="code" placeholder="Enter the code you received">
            <input type="submit" value="Submit">
        </form>
    ''')

@app.route('/get_token', methods=['POST'])
def get_token():
    code = request.form['code']
    data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'code': code,
        'grant_type': 'authorization_code'
    }
    response = requests.post(TOKEN_URL, data=data)
    if response.status_code == 200:
        access_token = response.json().get("access_token")
        session['access_token'] = access_token
        return redirect(url_for('home'))
    else:
        return jsonify(response.json()), 400

@app.route('/get_stats')
def get_athlete_stats():
    access_token = session.get('access_token')
    if not access_token:
        return redirect(url_for('home'))
    stats_url = f"https://www.strava.com/api/v3/athletes/{ATHLETE_ID}/stats?access_token={access_token}"
    response = requests.get(stats_url)
    if response.status_code == 200:
        stats = response.json()
        return render_template_string('''
            <h1>Athlete Stats:</h1>
            <pre>{{ stats }}</pre>
            <a href="/">Go back to Home</a>
        ''', stats=stats)
    else:
        return jsonify(response.json()), 400

@app.route('/ai_analysis')
def ai_analysis():
    access_token = session.get('access_token')
    if not access_token:
        return redirect(url_for('home'))
    stats_url = f"https://www.strava.com/api/v3/athletes/{ATHLETE_ID}/stats?access_token={access_token}"
    response = requests.get(stats_url)
    if response.status_code == 200:
        stats = response.json()
        stats_text = f"Analyze these stats: {stats}"
        OpenAI.api_key = OPENAI_API_KEY
        prompt = f"""
        You are a worldclass personal trainer. Based on the following athlete stats, provide detailed workout recommendations, insights, to help the athlete improve their performance. The stats include recent activities, overall performance, and progress over time.

        Athlete Stats:
        {stats_text}

        Your response should be in HTML and include:
        1. Personalized workout recommendations tailored to the athlete's current fitness level and goals.
        2. Insights on the athlete's recent performance and areas for improvement.
        3. Encouragement and motivational tips to keep the athlete engaged and positive.
        4. Mention key numbers, stats and activities the user has done.
        5. when speaking about distances use Kilometres.
        6. go into Great amounts of Detail, specific exercises, pre and post workout nutritional recomendations.


        Begin your analysis with a friendly greeting and remember to be supportive and motivational throughout your response.
        """
        client = OpenAI()
        stream = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": prompt}],
            stream=True,
        )
        ai_results = ""
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                ai_results += chunk.choices[0].delta.content
        return render_template_string(f'''
            <h1>AI Analysis Results:</h1>
            <p>{ai_results}</p>
            <a href="/">Go back to Home</a>
        ''')
    else:
        return jsonify(response.json()), 400

@app.route('/exit')
def exit_app():
    session.clear()
    return "Exiting the application. Goodbye!"

if __name__ == '__main__':
    app.run(debug=True)
