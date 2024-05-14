import webbrowser

def generate_auth_link(client_id, scope):
    return f"https://www.strava.com/oauth/authorize?client_id={client_id}&response_type=code&scope={scope}"

def main():
    print("Welcome to the Strava CLI!")
    client_id = input("Enter your Strava App's Client ID: ")

    # We can use a default scope for basic access to Strava data
    scope = "read"

    auth_link = generate_auth_link(client_id, scope)
    print("Please click on the following link to authenticate with Strava:")
    print(auth_link)
    input("Press Enter to continue...")

    print("Authentication successful!")
    print("Fetching Strava data...")

    # Here you can make requests to the Strava API using the obtained access token
    # Remember to exchange the authorization code for an access token as per Strava's OAuth flow

    print("Strava data fetched successfully!")

if __name__ == "__main__":
    main()
