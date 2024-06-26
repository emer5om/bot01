import asyncio

from pyrogram import Client, filters
from pyrogram.types import (
   CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQuery,
    InlineQueryResultArticle,
    InputTextMessageContent,
)

@Client.on_callback_query(filters.regex(r"^pesquisarcc"))
async def gift(c: Client, m: CallbackQuery):
    kb = InlineKeyboardMarkup(
        inline_keyboard=[            
            [
                InlineKeyboardButton("🏦 Buscar banco",switch_inline_query_current_chat="buscar_banco BANCO",),
                InlineKeyboardButton("🔐 Buscar bin",switch_inline_query_current_chat="buscar_bin 550209",),
            ],
            [
                InlineKeyboardButton("🏳️ Buscar bandeira",switch_inline_query_current_chat="buscar_bandeira MASTERCARD",),
                InlineKeyboardButton("🇧🇷 Buscar países",switch_inline_query_current_chat="buscar_paises BR",),
            ],             
            [
                 InlineKeyboardButton("⬅️ Menu Principal", callback_data="comprar_cc"),
            ],
        ]
    )
    await m.edit_message_text(
        f"""<b>🔎 | Filtros de Pesquisa</b>

<i>- Escolha um tipo de pesquisa para começar a pesquisar pelos cartões que você deseja!</i>""",
        reply_markup=kb,
	)