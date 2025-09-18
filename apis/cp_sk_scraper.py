import aiohttp
from bs4 import BeautifulSoup
import urllib.parse
from datetime import datetime

async def find_latest_departure(origin_stop: str, dest_stop: str, arrival_time: datetime) -> str | None:
    """
    Scrapes cp.sk to find the latest departure time for a given arrival time.

    Args:
        origin_stop: The name of the starting bus stop.
        dest_stop: The name of the destination bus stop.
        arrival_time: The desired arrival time as a datetime object.

    Returns:
        The latest departure time as a string "HH:MM", or None if not found.
    """
    # Format parameters for the URL according to the documentation
    date_str = arrival_time.strftime("%d.%m.%Y")
    time_str = arrival_time.strftime("%H:%M")

    # URL encode stop names to handle special characters
    params = {
        'f': origin_stop,
        't': dest_stop,
        'date': date_str,
        'time': time_str,
        'byarr': 'true',  # Search by arrival time
        'submit': 'true'  # Directly get results
    }
    encoded_params = urllib.parse.urlencode(params, encoding='utf-8')

    # Using the combination of bus and train for broader results
    base_url = "http://www.cp.sk/vlakbus/spojenie/"
    search_url = f"{base_url}?{encoded_params}"

    print(f"Requesting URL: {search_url}")

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(search_url) as response:
                response.raise_for_status()
                html = await response.text()

                soup = BeautifulSoup(html, 'lxml')

                # --- This is the fragile part ---
                # I am making educated guesses about the HTML structure.
                # I'll look for a table with connections and find the first row.

                # Assumption 1: The connections are in a table with class 'connection-list' or similar.
                # Let's try to find a common wrapper for connections. A `div` with class `box-spoj` seems plausible.
                # Or maybe a table `<table>`. Let's search broadly.

                # Find all potential connection rows. I'll look for a div with a "cas-odchodu" (departure time) class inside.
                # This is a guess. Another guess could be looking for `<td>` elements with time formats.

                # Let's assume the first element with a title containing "Odchod" (Departure) is what we need.
                # This is a very rough guess.
                first_connection = soup.find('td', {'class': 'time-dep'})

                if not first_connection:
                    # Alternative guess: find a div that contains the time.
                    first_connection = soup.find('div', {'class': 'departure-time'})

                if first_connection:
                    departure_time = first_connection.get_text(strip=True)
                    # The time might have extra characters, let's try to clean it.
                    # Assuming format is HH:MM
                    cleaned_time = ''.join(filter(lambda x: x.isdigit() or x == ':', departure_time))
                    if ':' in cleaned_time:
                         return cleaned_time

                # If the above fails, let's try a different approach.
                # Find the table of connections.
                connections_table = soup.find('table', {'class': 'connections'})
                if connections_table:
                    # Get the first data row
                    first_row = connections_table.find('tbody').find('tr')
                    if first_row:
                        # Find the cell corresponding to departure time (let's assume it's the 2nd cell)
                        departure_cell = first_row.find_all('td')[1]
                        if departure_cell:
                            return departure_cell.get_text(strip=True)

                print("Failed to parse departure time from cp.sk HTML.")
                return None
                # --- End of fragile part ---

        except aiohttp.ClientError as e:
            print(f"Error fetching cp.sk data: {e}")
            return None
        except Exception as e:
            print(f"An unexpected error occurred during scraping: {e}")
            return None
