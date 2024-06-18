import webbrowser
import os
import requests
from openai import OpenAI

########################################################## Constants for Strava API
CLIENT_ID = '125867'
CLIENT_SECRET = 'c8488d2be97f69ae395f9954531b5a09ab37b8e1'
REDIRECT_URI = 'http://localhost/exchange_token'
AUTH_URL = (
    f"https://www.strava.com/oauth/authorize?client_id={CLIENT_ID}&response_type=code"
    f"&redirect_uri={REDIRECT_URI}&approval_prompt=force&scope=read"
)
TOKEN_URL = "https://www.strava.com/oauth/token"
ATHLETE_ID = '55382335'

########################################################## Constants for OpenAI API

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

########################################################## Home
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def display_menu():
    clear_screen()
    print("\033[95mWelcome to My Strava CLI\033[0m")
    print("1. \033[94mAuthenticate with Strava\033[0m")
    print("2. \033[94mGet Athlete Stats\033[0m")
    print("3. \033[94mAI Analysis of Your Stats\033[0m")
    print("4. \033[94mExit\033[0m")
########################################################## Authentication
def authenticate():
    clear_screen()
    print("\033[95mPlease authenticate with Strava:\033[0m")
    print(f"Please visit the following link to authorize the application:\n{AUTH_URL}")
    print("After authorizing the application, you will be redirected to a URL starting with 'localhost'.")
    print("Copy the 'code' parameter from that URL and paste it below.")
    code = input("Enter the code you received: ")

    data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'code': code,
        'grant_type': 'authorization_code'
    }

    response = requests.post(TOKEN_URL, data=data)

    if response.status_code == 200:
        print("\033[92mAuthentication successful!\033[0m")
        access_token = response.json().get("access_token")
        print("\033[93mAccess Token:\033[0m", access_token)
        input("Press Enter to continue...")
        return access_token
    else:
        print("\033[91mAuthentication failed. Please try again.\033[0m")
        print("Error:", response.json())
        input("Press Enter to continue...")
        return None
########################################################## Fetch athlete stats
def get_athlete_stats(access_token):
    clear_screen()
    print("\033[95mFetching athlete stats...\033[0m")

    stats_url = f"https://www.strava.com/api/v3/athletes/{ATHLETE_ID}/stats?access_token={access_token}"
    response = requests.get(stats_url)

    if response.status_code == 200:
        print("\033[92mAthlete Stats:\033[0m")
        stats = response.json()
        print(stats)  # Print the fetched stats
        input("Press Enter to continue...")
    else:
        print("\033[91mFailed to retrieve athlete stats.\033[0m")
        print("Error:", response.json())
        input("Press Enter to continue...")

########################################################## Ai this shit

def ai_analysis(access_token):
    clear_screen()
    print("\033[95mAI Analysis of Your Stats\033[0m")


    stats_url = f"https://www.strava.com/api/v3/athletes/{ATHLETE_ID}/stats?access_token={access_token}"
    response = requests.get(stats_url)

    if response.status_code == 200:
        stats = response.json()
        stats_text = f"Analyze these stats: {stats}"
        OpenAI.api_key = OPENAI_API_KEY
        prompt = f"""
        You are an AI personal trainer. Based on the following Strava athlete stats, provide detailed workout recommendations, insights, and words of encouragement to help the athlete improve their performance. The stats include recent activities, overall performance, and progress over time.

        Athlete Stats:
        {stats_text}

        Your response should include:
        1. Personalized workout recommendations tailored to the athlete's current fitness level and goals.
        2. Insights on the athlete's recent performance and areas for improvement.
        3. Encouragement and motivational tips to keep the athlete engaged and positive.
        4. Mention key numbers,stats and activities the user has done.

        Begin your analysis with a friendly greeting and remember to be supportive and motivational throughout your response.
        """
        client = OpenAI()
        stream = client.chat.completions.create(
        model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            stream=True,
        )
        print("\033[92mAI Analysis Results:\033[0m")
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                print(chunk.choices[0].delta.content, end="")
        input("\nPress Enter to continue...")
    else:
        print("\033[91mFailed to retrieve athlete stats for analysis.\033[0m")
        print("Error:", response.json())
        input("Press Enter to continue...")
########################################################## Main
def main():
    access_token = None
    while True:
        display_menu()
        choice = input("Enter your choice: ")
        if choice == "1":
            access_token = authenticate()
        elif choice == "2":
            if access_token:
                get_athlete_stats(access_token)
            else:
                print("\033[91mYou need to authenticate first.\033[0m")
                input("Press Enter to continue...")
        elif choice == "3":
            if access_token:
                ai_analysis(access_token)
            else:
                print("\033[91mYou need to authenticate first.\033[0m")
                input("Press Enter to continue...")
        elif choice == "4":
            print("\033[95mExiting...\033[0m")
            break
        else:
            print("\033[91mInvalid choice. Please try again.\033[0m")
            input("Press Enter to continue...")

if __name__ == "__main__":
    main()
