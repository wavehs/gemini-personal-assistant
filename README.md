# Gemini Personal Assistant

This project is a modular, extensible, and production-ready Telegram bot that acts as a proactive, hyper-personalized assistant. It leverages the Gemini API for natural language understanding and task processing.

## ✨ Features

*   **Modular Architecture:** The code is split into logical components (`core`, `bot`, `apis`, `features`) for maintainability and extensibility.
*   **Intent Detection:** Uses the Gemini API to understand user messages, classify intents (e.g., `weather`, `create_event`), and extract relevant entities (e.g., a location or a date).
*   **Interactive Interface:** Provides an inline keyboard with buttons for easy access to features via the `/help` command.
*   **Asynchronous Core:** Built on `aiogram` and `asyncio` for high performance.
*   **Configuration Management:** All sensitive keys and settings are managed via a `.env` file.
*   **Testing:** Includes a testing suite with `pytest` for ensuring code quality.

### Implemented Features
*   **Weather Checking:** Ask the bot "What's the weather in [city]?" to get the current weather conditions.

### Planned Features
*   Google Calendar integration
*   News feed
*   Transport route planning
*   Pantry and shopping list management
*   Proactive notifications (e.g., morning briefings)

## 🏗️ Architecture

The project is organized into the following directories:

*   `/core`: Handles the core logic, including intent detection with the Gemini API.
*   `/bot`: Manages the Telegram bot interface, including command handlers and inline keyboards.
*   `/apis`: Contains wrappers for external APIs (e.g., OpenWeatherMap).
*   `/features`: Implements the logic for specific user-facing features.
*   `/scheduler`: (Planned) Will handle scheduled and proactive tasks.
*   `/tests`: Contains unit and integration tests for the project.

## 🚀 Getting Started

Follow these instructions to get a local copy up and running.

### Prerequisites

*   Python 3.11+
*   A Telegram Bot Token
*   API keys for Gemini and any other integrated services (like OpenWeatherMap)

### Installation

1.  **Clone the repository:**
    ```sh
    git clone <repository_url>
    cd gemini-personal-assistant
    ```

2.  **Create and activate a virtual environment (recommended):**
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3.  **Install the required dependencies:**
    ```sh
    pip install -r requirements.txt
    ```

4.  **Configure your environment variables:**
    *   Make a copy of the example environment file:
        ```sh
        cp .env.example .env
        ```
    *   Open the `.env` file and add your API keys and tokens.

### Running the Bot

Once you have completed the installation steps, you can start the bot with the following command:

```sh
python main.py
```

The bot will start polling for new messages. You can interact with it in your Telegram client.

### Testing the Assistant Directly

A script `test_assistant.py` is provided to allow you to test the assistant's core functionality directly from your command line, without needing to interact with the Telegram bot. This is useful for quick checks and debugging.

To run the test script:

```sh
python test_assistant.py
```

You can then type messages and see the assistant's responses in your terminal.
