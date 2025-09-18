import os
from google_auth_oauthlib.flow import Flow
from bot.user_data import update_user_data, get_user_data

# The file path for the client secrets.
CLIENT_SECRETS_FILE = "client_secrets.json"

# The scope defines the level of access you are requesting from the user.
# For reading calendar events, this scope is appropriate.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def generate_auth_url():
    """
    Generates a Google authorization URL for the user to visit.

    Returns:
        A tuple of (authorization_url, state) or (None, None) if setup fails.
    """
    if not os.path.exists(CLIENT_SECRETS_FILE):
        print(f"Error: {CLIENT_SECRETS_FILE} not found. Please create it from the example.")
        return None, None

    try:
        # Create a Flow instance to manage the OAuth 2.0 Authorization Grant Flow.
        flow = Flow.from_client_secrets_file(
            CLIENT_SECRETS_FILE,
            scopes=SCOPES,
            # The 'redirect_uri' is where the user will be sent after authorization.
            # 'urn:ietf:wg:oauth:2.0:oob' is for "out-of-band" (copy-paste) authorization.
            redirect_uri='urn:ietf:wg:oauth:2.0:oob'
        )

        # Generate the URL for the consent page.
        authorization_url, state = flow.authorization_url(
            # 'access_type=offline' is crucial to receive a refresh token.
            access_type='offline',
            # 'prompt=consent' ensures the user is prompted for consent every time,
            # which is useful for development and ensures a refresh token is issued.
            prompt='consent'
        )
        return authorization_url, state
    except Exception as e:
        print(f"Error creating Google auth flow: {e}")
        return None, None

def get_refresh_token(code: str) -> str | None:
    """
    Exchanges an authorization code for a refresh token.

    Args:
        code: The authorization code provided by the user.

    Returns:
        The refresh token string, or None if it fails.
    """
    if not os.path.exists(CLIENT_SECRETS_FILE):
        return None

    try:
        flow = Flow.from_client_secrets_file(
            CLIENT_SECRETS_FILE,
            scopes=SCOPES,
            redirect_uri='urn:ietf:wg:oauth:2.0:oob'
        )
        # Exchange the authorization code for credentials
        flow.fetch_token(code=code)

        # The refresh token is part of the credentials object
        credentials = flow.credentials
        return credentials.refresh_token
    except Exception as e:
        print(f"Error fetching refresh token: {e}")
        return None
