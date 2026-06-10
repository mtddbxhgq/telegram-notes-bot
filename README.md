# Installation and Setup Guide

This guide explains how to install and run the Telegram Notes Bot from scratch.

## Prerequisites

Before starting, make sure you have:

* Python 3.10 or newer installed
* Internet connection
* Telegram account

Check Python version:

```bash
python --version
```

or

```bash
python3 --version
```

Example:

```text
Python 3.12.3
```

---

## Step 1. Download the Project

Clone the repository:

```bash
git clone https://github.com/mtddbxhgq/telegram-notes-bot.git
```

Move into the project folder:

```bash
cd telegram-notes-bot
```

---

## Step 2. Create a Virtual Environment

Linux/macOS:

```bash
python3 -m venv venv
```

Windows:

```bash
python -m venv venv
```

---

## Step 3. Activate the Virtual Environment

Linux/macOS:

```bash
source venv/bin/activate
```

Windows:

```bash
.\venv\Scripts\Activate.ps1
```

If activation is successful, you will see:

```text
(venv)
```

at the beginning of the terminal line.

---

## Step 4. Install Required Packages

Install all dependencies:

```bash
pip install -r requirements.txt
```

---

## Step 5. Create a Telegram Bot

Open Telegram and search for:

```text
BotFather
```

Run:

```text
/newbot
```

Follow the instructions.

After the bot is created, BotFather will provide a token.

Example:

```text
123456789:AAExampleBotToken123456789
```

Save this token.

---

## Step 6. Generate an Encryption Key

The bot encrypts note contents before storing them in the database.

Generate a Fernet key:

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Example output:

```text
wL0gJ3u7Tz4j2h0k2rYxX3fJrV4P7nM5K8cD9sQ1eFg=
```

Save this key.

Important:

* Never share this key.
* Never upload this key to GitHub.
* If the key is lost, stored notes cannot be decrypted.

---

## Step 7. Create the .env File

Copy the example configuration:

```bash
cp .env.example .env
```

Open the file:

```bash
nano .env
```

or use any text editor.

Fill it with your values:

```env
BOT_TOKEN=your_bot_token
DATABASE_PATH=notes.db
FERNET_KEY=your_generated_fernet_key
```

Example:

```env
BOT_TOKEN=123456789:AAExampleBotToken123456789
DATABASE_PATH=notes.db
FERNET_KEY=wL0gJ3u7Tz4j2h0k2rYxX3fJrV4P7nM5K8cD9sQ1eFg=
```

Save the file.

---

## Step 8. Initialize the Database

Create the SQLite database:

```bash
python init_db.py
```

Expected output:

```text
Database initialized successfully.
```

This creates:

```text
notes.db
```

and the required database tables.

---

## Step 9. Start the Bot

Run:

```bash
python main.py
```

Expected output:

```text
Bot started successfully.
```

The bot is now running and ready to receive Telegram messages.

---

## Step 10. Open Your Bot in Telegram

Open Telegram.

Search for your bot username.

Press:

```text
START
```

or send:

```text
/start
```

---

## Available Commands

```text
/start
```

Start the bot.

```text
/help
```

Show help information.

```text
/add
```

Create a new note.

```text
/notes
```

View all saved notes.

```text
/delete
```

Delete a note.

```text
/cancel
```

Cancel the current operation.

---

## Example Usage

Create a note:

```text
/add
```

Bot:

```text
Please enter the note text.
```

User:

```text
Prepare laboratory work
```

Bot:

```text
Note added successfully. ID: 1
```

---

View notes:

```text
/notes
```

Bot:

```text
1. Prepare laboratory work
Created: 2026-06-10 18:30:00
```

---

Delete a note:

```text
/delete
```

Bot:

```text
Choose note number to delete:

1. Prepare laboratory work
Created: 2026-06-10 18:30:00

Enter note ID:
```

User:

```text
1
```

Bot:

```text
Are you sure you want to delete this note?

Type YES to confirm or NO to cancel.
```

User:

```text
YES
```

Bot:

```text
Note with ID 1 has been deleted.
```

---

## Updating the Database Structure

If you changed the database schema during development:

```bash
rm notes.db
python init_db.py
```

Warning:

This removes all saved notes.

---

## Stopping the Bot

Press:

```text
CTRL + C
```

in the terminal.

---

## Security Notes

Do not upload the following files to GitHub:

```text
.env
notes.db
bot.log
```

These files contain sensitive information or user data.

The project already ignores these files through `.gitignore`.
