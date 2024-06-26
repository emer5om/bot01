from typing import Callable, Iterable, Optional, Tuple, Union
from pyrogram import Client, filters
from pyrogram.types import (
    CallbackQuery,
    ForceReply,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from config import ADMINS
from database import cur, db
from utils import get_lara_info

def get_custom_info() -> Tuple[str, str, str]:
	"""Retorna uma tupla contendo o nome da lara e chave Pix."""
	q = cur.execute("SELECT url, resultlive, resultdie from custom_gate")
	return q.fetchone()

def update_gatecustom(url: str, live: str, die: str):
    cur.execute(
        "UPDATE custom_gate SET url = ?, resultlive = ?, resultdie = ? WHERE ROWID = 0",
        (url, live, die),
    )
    db.commit()


@Client.on_callback_query(filters.regex(r"^custom_gate$") & filters.user(ADMINS))
async def customgates(c: Client, m: CallbackQuery):
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    "❇️ Adicionar Gate Custom", callback_data="change_custom_details"
                ),
            ],
            [InlineKeyboardButton("⬅️ Menu Principal", callback_data="painel")],
        ]
    )


    url, resultlive, resultdie = get_custom_info()

    await m.edit_message_text(
        "<b>❇️ Adicionar Gate Custom</b>\n"
        '<i>- Esta opção permite alterar a url de uma gate custom para usar na vendas e trocas do bot</i>\n\n'
        "<b>Dados atuais:</b>\n"
        f"<b>URL:</b> <code>{url}</code>\n"
        f"<b>RESPOSTA DE LIVE:</b> <code>{resultlive}</code>\n"
         f"<b>RESPOSTA DE DIE</b> <code>{resultdie}</code>",
        reply_markup=kb,
    )


@Client.on_callback_query(
    filters.regex(r"^change_custom_details$") & filters.user(ADMINS)
)
async def change_custom_details(c: Client, m: CallbackQuery):
    await m.message.delete()

    url = await m.message.ask("Informe o url completo da gate\nExemplo: https://gatexemplo.com/api.php?key1234&card=", reply_markup=ForceReply())
    resultlive = await m.message.ask(
        "Informe o Retorno de LIVE\nExemplo: True", reply_markup=ForceReply()
    )
    resultdie = await m.message.ask(
        "Informe o Retorno de DIE\nExemplo: False", reply_markup=ForceReply()
    )

    update_gatecustom(url.text, resultlive.text, resultdie.text)

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton("✅ Ok", callback_data="painel")],
        ]
    )

    await m.message.reply_text(
        "✅ Dados da GATE CUSTOM alterados com sucesso.", reply_markup=kb
    )
