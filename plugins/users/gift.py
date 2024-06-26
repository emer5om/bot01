from typing import Union

from pyrogram import Client, filters
from pyrogram.errors import BadRequest
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from database import cur, save
from utils import create_mention, get_info_wallet

@Client.on_callback_query(filters.regex(r"^gift$"))
async def gift(c: Client, m: CallbackQuery):
    kb = InlineKeyboardMarkup(
        inline_keyboard=[            
             [
                 InlineKeyboardButton("⬅️ Menu Principal", callback_data="user_info"),
             ],
        ]
    )
    await m.edit_message_text(
        f"""<a href='https://d6xcmfyh68wv8.cloudfront.net/blog-content/uploads/2020/10/Card-pre-launch_blog-feature-image1.png'>&#8204</a><b>🎁 Resgatar Gift</b>
		
<i>♾️ - Aqui você resgatar o gift com facilidade, digite seu gift como o exemplo abaixo.</i>

<i>🏷 - Exemplo: /resgatar GDX0FCOT7OTH </i>

<i>🚫 - NÃO TENTE DA UM DE ESPERTINHO E FLOODAR VÁRIOS CÓDIGOS AO MESMO TEMPOS, TEMOS UM SISTEMA DE ANTI FLOOD, CASO FLOOD IRÁ TOMAR BAN AUTOMÁTICO!</i>
""",
        reply_markup=kb,
	)