from pyrogram import Client, filters
from pyrogram.types import (
    CallbackQuery,
    ForceReply,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from database import cur, save
from utils import get_info_wallet

import datetime
from typing import Union
import asyncio

@Client.on_callback_query(filters.regex(r"^filiados$"))
async def gift(c: Client, m: CallbackQuery):
    kb = InlineKeyboardMarkup(
        inline_keyboard=[            
             [
				         InlineKeyboardButton("📭 TROCAR PONTOS", callback_data="swap"),
				     ],
		      	 [
				         InlineKeyboardButton("⬅️ Menu Principal", callback_data="start"),
             ],
        ]
    )
    link = f"https://t.me/{c.me.username}?start={m.from_user.id}"
    await m.edit_message_text(
        f"""<a href='https://d6xcmfyh68wv8.cloudfront.net/blog-content/uploads/2020/10/Card-pre-launch_blog-feature-image1.png'>&#8204</a>🔗 - SISTEMA DE AFILIADOS!

<b>📎 - COMO FUNCIONA:</b>

<b>♻️ - VOCÊ VAI COMPARTILHAR O SEU LINK DE AFILIADOS COM ALGUMA PESSOA, A CADA RECARGA QUE ELE FIZER VOCÊ GANHA 10% EM SALDO NO BOT!</b>

<b>️📎 - COMPARTILHE SEU LINK AGORA:</b>
<code>{link}</code></b>
""",
        reply_markup=kb,
	)