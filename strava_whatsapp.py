
import webbrowser
import os
import requests

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

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def display_menu():
    clear_screen()
    print("\033[95mWelcome to My Strava CLI\033[0m")
    print("1. \033[94mAuthenticate with Strava\033[0m")
    print("2. \033[94mGet Athlete Stats\033[0m")
    print("3. \033[94mExit\033[0m")

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

def get_athlete_stats(access_token):
    clear_screen()
    print("\033[95mFetching athlete stats...\033[0m")

    stats_url = f"https://www.strava.com/api/v3/athletes/{ATHLETE_ID}/stats?access_token={access_token}"
    response = requests.get(stats_url)

    if response.status_code == 200:
        print("\033[92mAthlete Stats:\033[0m")
        stats = response.json()

        # Convert distance to kilometers
        for key, value in stats.items():
            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    if sub_key.endswith('distance'):
                        stats[key][sub_key] = sub_value / 1000
                    elif sub_key.endswith('elevation_gain'):
                        stats[key][sub_key] = sub_value
            elif key.endswith('distance'):
                stats[key] = value / 1000
            elif key.endswith('elevation_gain'):
                stats[key] = value

        for key, value in stats.items():
            if isinstance(value, dict):
                print(f"\033[93m{key}:\033[0m")
                for sub_key, sub_value in value.items():
                    if sub_key.endswith('distance'):
                        print(f"  \033[93m{sub_key}:\033[0m {sub_value:.2f} km")
                    elif sub_key.endswith('time'):
                        print(f"  \033[93m{sub_key}:\033[0m {sub_value // 60} minutes")
                    elif sub_key.endswith('gain'):
                        print(f"  \033[93m{sub_key}:\033[0m {sub_value:.2f} meters")
                    else:
                        print(f"  \033[93m{sub_key}:\033[0m {sub_value}")
            else:
                print(f"\033[93m{key}:\033[0m {value}")
        input("Press Enter to continue...")
    else:
        print("\033[91mFailed to retrieve athlete stats.\033[0m")
        print("Error:", response.json())
        input("Press Enter to continue...")

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
            print("\033[95mExiting...\033[0m")
            break
        else:
            print("\033[91mInvalid choice. Please try again.\033[0m")
            input("Press Enter to continue...")

if __name__ == "__main__":
    main()
