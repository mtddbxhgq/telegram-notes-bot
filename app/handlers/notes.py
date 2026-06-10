import logging

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

from app.database.db import Database, MAX_NOTES_PER_USER


router = Router()
logger = logging.getLogger(__name__)

MAX_NOTE_LENGTH = 1000


class NoteStates(StatesGroup):
    waiting_for_note_text = State()
    waiting_for_delete_id = State()
    waiting_for_delete_confirmation = State()


@router.message(CommandStart())
async def start_command(message: Message) -> None:
    await message.answer(
        "Welcome to Personal Notes Bot!\n\n"
        "Available commands:\n"
        "/add - Add a new note\n"
        "/notes - View all your notes\n"
        "/delete - Delete a note\n"
        "/cancel - Cancel current action\n"
        "/help - Show help message"
    )


@router.message(Command("help"))
async def help_command(message: Message) -> None:
    await message.answer(
        "How to use this bot:\n\n"
        "/add - Start adding a note\n"
        "/notes - Show all saved notes\n"
        "/delete - Show notes and choose which one to delete\n"
        "/cancel - Cancel current action\n\n"
        "Each Telegram user has their own note IDs starting from 1."
    )


@router.message(Command("cancel"))
async def cancel_command(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()

    if current_state is None:
        await message.answer("There is no active action to cancel.")
        return

    await state.clear()
    await message.answer("Action cancelled.")


@router.message(Command("add"))
async def add_note_start(message: Message, state: FSMContext) -> None:
    await state.set_state(NoteStates.waiting_for_note_text)
    await message.answer(
        "Please enter the note text.\n\n"
        "To cancel this action, type /cancel."
    )


@router.message(NoteStates.waiting_for_note_text)
async def add_note_finish(
    message: Message,
    state: FSMContext,
    db: Database,
) -> None:
    if message.from_user is None:
        await message.answer("Error: user could not be identified.")
        await state.clear()
        return

    note_text = message.text.strip() if message.text else ""

    if not note_text:
        await message.answer("Error: note text cannot be empty.")
        return

    if note_text.startswith("/"):
        await message.answer(
            "This looks like a command, not a note.\n"
            "Please enter note text or type /cancel."
        )
        return

    if len(note_text) > MAX_NOTE_LENGTH:
        await message.answer(
            f"Error: note is too long. Maximum length is {MAX_NOTE_LENGTH} characters."
        )
        return

    try:
        notes_count = db.get_notes_count(user_id=message.from_user.id)

        if notes_count >= MAX_NOTES_PER_USER:
            await state.clear()
            await message.answer(
                f"You have reached the maximum limit of {MAX_NOTES_PER_USER} notes."
            )
            return

        note_id = db.add_note(
            user_id=message.from_user.id,
            text=note_text,
        )

        logger.info(
            "Note added | user_id=%s | note_id=%s",
            message.from_user.id,
            note_id,
        )

        await state.clear()
        await message.answer(f"Note added successfully. ID: {note_id}")

    except Exception:
        logger.exception(
            "Failed to add note | user_id=%s",
            message.from_user.id,
        )
        await state.clear()
        await message.answer("An error occurred while saving the note.")


@router.message(Command("notes"))
async def show_notes_command(message: Message, db: Database) -> None:
    if message.from_user is None:
        await message.answer("Error: user could not be identified.")
        return

    try:
        notes = db.get_notes(user_id=message.from_user.id)

    except Exception:
        logger.exception(
            "Failed to retrieve notes | user_id=%s",
            message.from_user.id,
        )
        await message.answer("An error occurred while retrieving notes.")
        return

    if not notes:
        await message.answer("You do not have any saved notes yet.")
        return

    response = ["Your notes:\n"]

    for note in notes:
        response.append(
            f"{note.note_id}. {note.text}\n"
            f"Created: {note.created_at}\n"
        )

    await message.answer("\n".join(response))


@router.message(Command("delete"))
async def delete_note_start(
    message: Message,
    state: FSMContext,
    db: Database,
) -> None:
    if message.from_user is None:
        await message.answer("Error: user could not be identified.")
        return

    try:
        notes = db.get_notes(user_id=message.from_user.id)

    except Exception:
        logger.exception(
            "Failed to retrieve notes before delete | user_id=%s",
            message.from_user.id,
        )
        await message.answer("An error occurred while retrieving notes.")
        return

    if not notes:
        await message.answer("You do not have any saved notes to delete.")
        return

    response = ["Choose note number to delete:\n"]

    for note in notes:
        response.append(
            f"{note.note_id}. {note.text}\n"
            f"Created: {note.created_at}\n"
        )

    response.append("Enter note ID:")

    await state.set_state(NoteStates.waiting_for_delete_id)
    await message.answer("\n".join(response))


@router.message(NoteStates.waiting_for_delete_id)
async def delete_note_choose_id(
    message: Message,
    state: FSMContext,
    db: Database,
) -> None:
    if message.from_user is None:
        await message.answer("Error: user could not be identified.")
        await state.clear()
        return

    note_id_text = message.text.strip() if message.text else ""

    if not note_id_text.isdigit():
        await message.answer(
            "Error: note ID must be a number.\n"
            "Please enter a valid note ID or type /cancel."
        )
        return

    note_id = int(note_id_text)

    try:
        notes = db.get_notes(user_id=message.from_user.id)

    except Exception:
        logger.exception(
            "Failed to retrieve notes for confirmation | user_id=%s",
            message.from_user.id,
        )
        await state.clear()
        await message.answer("An error occurred while retrieving notes.")
        return

    selected_note = None

    for note in notes:
        if note.note_id == note_id:
            selected_note = note
            break

    if selected_note is None:
        await message.answer(
            "Note not found or does not belong to you.\n"
            "Please enter another note ID or type /cancel."
        )
        return

    await state.update_data(
        note_id=selected_note.note_id,
        note_text=selected_note.text,
    )

    await state.set_state(NoteStates.waiting_for_delete_confirmation)

    await message.answer(
        "Are you sure you want to delete this note?\n\n"
        f"ID: {selected_note.note_id}\n"
        f"Created: {selected_note.created_at}\n"
        f"Text: {selected_note.text}\n\n"
        "Type YES to confirm or NO to cancel."
    )


@router.message(NoteStates.waiting_for_delete_confirmation)
async def delete_note_confirm(
    message: Message,
    state: FSMContext,
    db: Database,
) -> None:
    if message.from_user is None:
        await message.answer("Error: user could not be identified.")
        await state.clear()
        return

    answer = message.text.strip().upper() if message.text else ""

    if answer == "NO":
        await state.clear()
        await message.answer("Deletion cancelled.")
        return

    if answer != "YES":
        await message.answer("Please type YES to confirm deletion or NO to cancel.")
        return

    data = await state.get_data()
    note_id = data.get("note_id")

    if note_id is None:
        await state.clear()
        await message.answer("Error: note ID was not found. Please try again.")
        return

    try:
        deleted = db.delete_note(
            user_id=message.from_user.id,
            note_id=int(note_id),
        )

    except Exception:
        logger.exception(
            "Failed to delete note | user_id=%s | note_id=%s",
            message.from_user.id,
            note_id,
        )
        await state.clear()
        await message.answer("An error occurred while deleting the note.")
        return

    await state.clear()

    if deleted:
        logger.info(
            "Note deleted | user_id=%s | note_id=%s",
            message.from_user.id,
            note_id,
        )
        await message.answer(f"Note with ID {note_id} has been deleted.")
    else:
        await message.answer("Note not found or does not belong to you.")


@router.message(F.text)
async def unknown_message(message: Message) -> None:
    await message.answer("Unknown command. Type /help to see available commands.")