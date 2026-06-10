# Telegram Notes Bot

A simple Telegram bot for storing personal notes using Python, aiogram 3.x, and SQLite.

## Features

- Add personal notes
- View all saved notes
- Delete notes by ID
- Store notes separately for each Telegram user
- SQLite database support
- Environment-based configuration
- Basic error handling

## Technologies

- Python 3
- aiogram 3.x
- SQLite
- python-dotenv

## Project Structure

```text
telegram_notes_bot/
├── app/
│   ├── database/
│   │   ├── __init__.py
│   │   └── db.py
│   ├── handlers/
│   │   ├── __init__.py
│   │   └── notes.py
│   ├── __init__.py
│   └── middlewares.py
├── .env.example
├── .gitignore
├── config.py
├── init_db.py
├── main.py
├── README.md
└── requirements.txt
Security Notes

The bot token and other sensitive configuration values are not stored directly in the source code.

The project uses a .env file for local configuration. This file must not be committed to GitHub.

The .env.example file is provided only as a template.

Additional security measures:

Parameterized SQL queries are used to reduce SQL injection risks.
Each note is linked to a specific Telegram user_id.
Users can view and delete only their own notes.
Basic rate limiting is used to reduce spam and simple DoS attempts.
Suspicious or too frequent requests are logged.
Installation
1. Clone the repository
git clone https://github.com/mtddbxhgq/telegram-notes-bot.git
cd telegram-notes-bot
2. Create a virtual environment
python3 -m venv venv
3. Activate the virtual environment

Linux/macOS:

source venv/bin/activate

Windows:

venv\Scripts\activate
4. Install dependencies
pip install -r requirements.txt
5. Create the environment file
cp .env.example .env

Open .env and add your Telegram bot token:

BOT_TOKEN=your_telegram_bot_token_here
DATABASE_PATH=notes.db

You can get a Telegram bot token from BotFather.

Database Initialization

Before running the bot for the first time, initialize the SQLite database:

python init_db.py

This command creates the notes.db file and the required notes table.

Running the Bot

Start the bot with:

python main.py

If the bot starts successfully, it will begin polling Telegram updates.

Bot Commands
/start - Start the bot
/help - Show help message
/add text - Add a new note
/notes - Show all your notes
/delete ID - Delete a note by ID
Usage Examples

Add a note:

/add Prepare laboratory work

View notes:

/notes

Delete a note:

/delete 1
How Notes Are Stored

Each note is stored in the SQLite database with the Telegram user's user_id.

This means that every user has a separate list of notes.

One user cannot see or delete notes that belong to another user.

Environment Variables
Variable	Description
BOT_TOKEN	Telegram bot token from BotFather
DATABASE_PATH	Path to the SQLite database file
Files Not Included in GitHub

The following files are ignored for security and cleanliness:

.env
notes.db
bot.log
venv/
__pycache__/
License

This project is created for educational purposes.
