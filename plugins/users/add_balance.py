import math
from typing import Union

from pyrogram import Client, filters
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from config import ADMIN_CHAT
from config import GRUPO_PUB
from database import cur, save
from config import BOT_LINK
from config import BOT_LINK_SUPORTE

from utils import create_mention, get_lara_info, get_support_user, insert_sold_balance


@Client.on_callback_query(filters.regex(r"^add_saldo$"))
async def add_saldo(c: Client, m: CallbackQuery):
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton("💠 Pix automático", callback_data="add_saldo_auto"),
                InlineKeyboardButton("🤖 Pix manual", callback_data="add_saldo_manual"),                
            ],
            [
                InlineKeyboardButton("⬅️ Menu Principal", callback_data="start"),
            ],
        ]
    )

    await m.edit_message_text(
        f"""<a href='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQ0bAMj8fmlNIS3D7EV98omF0WAcB_Fn4L7Rg&usqp=CAU'>&#8204</a><b>💸 Adicionar Saldo</b>
<i>- Aqui abaixo vc poderá adicionar saldo de duas formas, <b>pix automático</b> ou <b>pix manual</b>.</i>""",
        reply_markup=kb,
    )


@Client.on_callback_query(filters.regex(r"^add_saldo_manual$"))
async def add_saldo_manual(c: Client, m: CallbackQuery):
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
				InlineKeyboardButton("📲 Enviar Comprovante", url="https://t.me/LittleNucky"),
			],
			[
                InlineKeyboardButton("⬅️ Menu Principal", callback_data="add_saldo"),
            ],
        ]
    )

    pix_name, pix_key = get_lara_info()

    support_user = get_support_user()
    valor_min = 1
    details = (
        f"<i>Não envie um valor</i> <b>menor</b> <i>que R${valor_min},00 pois se você enviar perderá seu dinheiro.</i>"
        if valor_min
        else ""
    )
    await m.edit_message_text(
        f"""<b>🤖 PIX MANUAL</b>

<b>🏦 DADOS DA CONTA:</b>

<b>📨 - Nome:</b> <code>{pix_name}</code>
<b>🔑 - Chave Pix:</b> <code>{pix_key}</code>

{details}""",
        reply_markup=kb,
    )


@Client.on_message(filters.regex(r"/resgatar (?P<gift>\w+)$"))
@Client.on_callback_query(filters.regex(r"^resgatar (?P<gift>\w+)$"))
async def resgatar_gift(c: Client, m: Union[CallbackQuery, Message]):
    user_id = m.from_user.id
    gift = m.matches[0]["gift"]

    if isinstance(m, Message):
        send = m.reply_text
    else:
        send = m.edit_message_text

    try:
        value = cur.execute(
            "SELECT value from gifts WHERE token = ?", [gift]
        ).fetchone()[0]
    except:
        return await send("<b> GIFT CARD não existente ou já resgatado, digite /pix para realizar uma transferência.</b>")

    cur.execute("DELETE FROM gifts WHERE token = ?", [gift])

    cur.execute(
        "UPDATE users SET balance = balance + ? WHERE id = ?", [value, user_id]
    ).fetchone()

    new_balance = cur.execute(
        "SELECT balance FROM users WHERE id = ?", [user_id]
    ).fetchone()[0]

    mention = create_mention(m.from_user)
    insert_sold_balance(value, user_id, "manual")
    base = f"""<a href='https://i.ibb.co/yYw5YPH/ac-asesores-saldos-corrientes-ahorros.jpg'>&#8204</a>🎁 {mention} resgatou um gift card de <b>R${value}</b>
    
- Novo saldo: <b>R${new_balance}</b>
- Gift card: <code>{gift}</code>******"""

    await c.send_message(ADMIN_CHAT, base)
    
    kb = InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(text="🥇 Adicionar Saldo No Bot",url="https://t.me/NuckyStoreBot"),
                        ],
                    ]
                )
    mention = m.from_user.first_name
    base = f"""<a href='https://i.ibb.co/yYw5YPH/ac-asesores-saldos-corrientes-ahorros.jpg'>&#8204</a>🎁 {mention} resgatou um gift card de <b>R${value}</b>
    
<b>Obrigado pela preferência</b>

- Gift card: <code>{gift[0:6]}</code>******\n<a href='https://t.me/{BOT_LINK_SUPORTE}'>Suporte</a>"""
    await c.send_message(GRUPO_PUB, base, reply_markup=kb)

    if isinstance(m, CallbackQuery):
        kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                   InlineKeyboardButton("🛒 Voltar ao bot", url=f"https://t.me/{c.me.username}?start=start",)
                ],
            ]
        )
        await send(
            f"<b>🎁 {m.from_user.first_name} resgatou R$ {value} no bot via gift card.</b>",
            reply_markup=kb,
        )
    else:
        await send(
            f"<b>🎉 Agora sim foi adicionado R$ {value} em sua conta no bot.</b>"
        )

    
    refer = cur.execute("SELECT refer FROM users WHERE id = ?", [user_id]).fetchone()[0]

    if refer:
        quantity = math.floor((value / 100) * 5)  # 5% normalizado para int.
        if quantity > 0:
            mention = create_mention(m.from_user, with_id=False)

            cur.execute(
                "UPDATE users SET balance = balance + ? WHERE id = ?",
                [quantity, refer],
            ).fetchone()

            await c.send_message(
                int(refer),
                f"💸 Seu referenciado {mention} adicionou saldo no bot e você recebeu {quantity} de saldo.",
            )
    
    save()
