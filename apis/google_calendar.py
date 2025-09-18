import os
import datetime
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from bot.user_data import get_user_data

CLIENT_SECRETS_FILE = "client_secrets.json"

def _get_credentials(user_id: int) -> Credentials | None:
    """Builds Google API credentials from a stored refresh token."""
    refresh_token = get_user_data(user_id, 'google_refresh_token')
    if not refresh_token:
        return None

    # Scopes must match the ones used during authorization
    scopes = ['https://www.googleapis.com/auth/calendar.readonly']

    try:
        # Create credentials from the stored refresh token.
        # client_id and client_secret are needed for the refresh flow.
        # These are loaded from the client_secrets.json file.
        # Note: A more robust implementation would cache this file.
        import json
        with open(CLIENT_SECRETS_FILE, 'r') as f:
            secrets = json.load()['installed']

        credentials = Credentials(
            token=None,  # No access token, it will be refreshed
            refresh_token=refresh_token,
            token_uri=secrets['token_uri'],
            client_id=secrets['client_id'],
            client_secret=secrets['client_secret'],
            scopes=scopes
        )
        return credentials
    except Exception as e:
        print(f"Error building credentials: {e}")
        return None


async def get_first_event_for_day(user_id: int, target_day: datetime.date) -> dict | None:
    """
    Fetches the first Google Calendar event for a user on a specific day.

    Args:
        user_id: The ID of the user.
        target_day: The date to check for events.

    Returns:
        A dictionary with event details {'summary': str, 'start': str} or None.
    """
    credentials = _get_credentials(user_id)
    if not credentials:
        print(f"No credentials found for user {user_id}")
        # This could also return a specific error message string
        return None

    try:
        service = build('calendar', 'v3', credentials=credentials)

        # Set the time range to the beginning and end of the target day
        time_min = datetime.datetime.combine(target_day, datetime.time.min).isoformat() + 'Z'
        time_max = datetime.datetime.combine(target_day, datetime.time.max).isoformat() + 'Z'

        events_result = service.events().list(
            calendarId='primary',
            timeMin=time_min,
            timeMax=time_max,
            maxResults=1,
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        events = events_result.get('items', [])
        if not events:
            return None  # No events found

        event = events[0]
        start = event['start'].get('dateTime', event['start'].get('date'))

        return {
            'summary': event['summary'],
            'start': start
        }

    except Exception as e:
        print(f"An error occurred with Google Calendar API: {e}")
        return None
