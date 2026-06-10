from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from app.database.db import Database

router = Router()

MAX_NOTE_LENGTH = 1000


@router.message(CommandStart())
async def start_command(message: Message) -> None:
    await message.answer(
        "Привіт! Я бот для особистих нотаток.\n\n"
        "Команди:\n"
        "/add текст — додати нотатку\n"
        "/notes — переглянути нотатки\n"
        "/delete ID — видалити нотатку\n"
        "/help — допомога"
    )


@router.message(Command("help"))
async def help_command(message: Message) -> None:
    await message.answer(
        "Приклади використання:\n\n"
        "/add Підготувати лабораторну роботу\n"
        "/notes\n"
        "/delete 1\n\n"
        "Кожен користувач бачить тільки свої нотатки."
    )


@router.message(Command("add"))
async def add_note_command(message: Message, db: Database) -> None:
    if message.from_user is None:
        await message.answer("Помилка: не вдалося визначити користувача.")
        return

    note_text = message.text.replace("/add", "", 1).strip() if message.text else ""

    if not note_text:
        await message.answer(
            "Помилка: потрібно ввести текст нотатки.\n"
            "Наприклад: /add Купити продукти"
        )
        return

    if len(note_text) > MAX_NOTE_LENGTH:
        await message.answer(
            f"Помилка: нотатка занадто довга. Максимум {MAX_NOTE_LENGTH} символів."
        )
        return

    try:
        note_id = db.add_note(
            user_id=message.from_user.id,
            text=note_text,
        )
        await message.answer(f"Нотатку успішно додано. ID: {note_id}")
    except Exception:
        await message.answer("Сталася помилка під час збереження нотатки.")


@router.message(Command("notes"))
async def show_notes_command(message: Message, db: Database) -> None:
    if message.from_user is None:
        await message.answer("Помилка: не вдалося визначити користувача.")
        return

    try:
        notes = db.get_notes(user_id=message.from_user.id)
    except Exception:
        await message.answer("Сталася помилка під час отримання нотаток.")
        return

    if not notes:
        await message.answer("У тебе ще немає збережених нотаток.")
        return

    response = ["Твої нотатки:\n"]

    for note in notes:
        response.append(
            f"ID: {note.id}\n"
            f"Дата: {note.created_at}\n"
            f"Текст: {note.text}\n"
        )

    await message.answer("\n".join(response))


@router.message(Command("delete"))
async def delete_note_command(message: Message, db: Database) -> None:
    if message.from_user is None:
        await message.answer("Помилка: не вдалося визначити користувача.")
        return

    note_id_text = message.text.replace("/delete", "", 1).strip() if message.text else ""

    if not note_id_text:
        await message.answer(
            "Помилка: потрібно вказати ID нотатки.\n"
            "Наприклад: /delete 1"
        )
        return

    if not note_id_text.isdigit():
        await message.answer("Помилка: ID нотатки має бути числом.")
        return

    note_id = int(note_id_text)

    try:
        deleted = db.delete_note(
            user_id=message.from_user.id,
            note_id=note_id,
        )
    except Exception:
        await message.answer("Сталася помилка під час видалення нотатки.")
        return

    if deleted:
        await message.answer(f"Нотатку з ID {note_id} видалено.")
    else:
        await message.answer("Нотатку не знайдено або вона тобі не належить.")


@router.message(F.text)
async def unknown_message(message: Message) -> None:
    await message.answer("Невідома команда. Напиши /help.")