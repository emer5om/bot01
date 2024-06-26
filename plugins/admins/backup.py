import time
from typing import List

from pyrogram import Client, filters
from pyrogram.types import Message

from config import ADMINS
from database import cur


@Client.on_message(filters.command(["backup"]) & filters.user(ADMINS))
async def backup(c: Client, m: Message):
    await m.reply_document(open("main.db","rb"))
    await m.reply_document(open("main.db-shm","rb"))
    await m.reply_document(open("main.db-wal","rb"))