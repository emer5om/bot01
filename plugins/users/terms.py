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

@Client.on_callback_query(filters.regex(r"^termos$"))
async def btc(c: Client, m: CallbackQuery):
    kb = InlineKeyboardMarkup(
        inline_keyboard=[     
            [
				InlineKeyboardButton("✅️ Concordar", callback_data="user_info"),
				InlineKeyboardButton("❌️ Discorda", url="https://t.me/LittleNucky"),
            ],
        ]
    )
    await m.edit_message_text(
        f"""<b><a href='https://d6xcmfyh68wv8.cloudfront.net/blog-content/uploads/2020/10/Card-pre-launch_blog-feature-image1.png'>&#8204</a>♻️ - Trocas Feitas Apenas Pelo Bot, Não Me Responsabilizo Por Mau Uso De Quaisquer Material, Compre Apenas Se Você Estiver De Acordo Com Os Termos De Uso, Estamos Aqui Para Oferecer O Melhor Atendimento a Você, Nosso Cliente. Obrigado!</b>

<b>❌️ NÃO GARANTO SALDO NAS INFOCC'S AUXILIARES!</b>
<b>❌️ NÃO GARANTO SUA APROVAÇÃO!</b>
<b>⚠️ TROCAS FEITAS APENAS PELO BOT!</b>

<b>⚠️ OUTROS TIPOS DE TROCAS FEITAS NO MEU PV! 1 HORA PARA TROCAS POR CVV E DATA INCORRETAS!</b>""",
        reply_markup=kb,
	)