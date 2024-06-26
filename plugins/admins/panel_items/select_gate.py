from functools import partial as partial

from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from config import ADMINS
from database import cur, save
from gates import *

GATES = {
    "semchk": semchk,
    "custom":custom,
    
}  # fmt: skip

# Copiando o GATES (que é uma constante) para uma variável,
# na qual poderá ser modificada posteriormente.
gates = GATES.copy()


@Client.on_callback_query(filters.regex(r"^select_gate$") & filters.user(ADMINS))
async def type_chk(c: Client, m: CallbackQuery):
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton("💳 Checagem", callback_data="select_gate gate"),
                InlineKeyboardButton("♻ Trocas", callback_data="select_gate exchange"),
            ],
            [
                InlineKeyboardButton("🌈 Publico", callback_data="select_gate pub"),
                InlineKeyboardButton("🔃 Refresh", callback_data="refresh_gates"),
            ],
            [
                InlineKeyboardButton("⬅️ Menu Principal", callback_data="painel"),
            ],
        ]
    )

    await m.edit_message_text(
        "<b>🔃 Gates</b>\n"
        "<i>- Esta opção permite alterar as gates usadas para checagem e trocas, além de ser possível reestabelecer as gates.</i>\n\n"
        "<b>Selecione abaixo a opção desejada:</b>",
        reply_markup=kb,
    )


@Client.on_callback_query(
    filters.regex(r"^select_gate (?P<chk_type>.+)$") & filters.user(ADMINS)
)
async def options_gates(c: Client, m: CallbackQuery):
    type_exchange = m.matches[0]["chk_type"]
    bt_list = []
    for opt in gates:
        bt_list.append(
            InlineKeyboardButton(
                text=f"✦ {opt}", callback_data=f"set_gate {type_exchange} {opt}"
            )
        )

    orgn = (lambda data, step: [data[x : x + step] for x in range(0, len(data), step)])(
        bt_list, 2
    )
    orgn.append([InlineKeyboardButton(text="⬅️ Menu Principal", callback_data="select_gate")])
    kb = InlineKeyboardMarkup(inline_keyboard=orgn)

    await m.edit_message_text(
        "<b>🔃 Selecione a gate para operar checagem no bot</b>", reply_markup=kb
    )


@Client.on_callback_query(
    filters.regex(r"^set_gate (?P<chk_type>.+) (?P<gate>.+)") & filters.user(ADMINS)
)
async def select_gate(c: Client, m: CallbackQuery):
    var_alt = m.matches[0]["chk_type"]
    gate = m.matches[0]["gate"]

    if var_alt == "exchange":
        cur.execute("UPDATE bot_config SET gate_exchange = ?", [gate])
    elif var_alt == "pub":
    	  cur.execute("UPDATE bot_config SET gate_chk_publico = ?", [gate])
    else:
        cur.execute("UPDATE bot_config SET gate_chk = ?", [gate])
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Menu Principal", callback_data="select_gate")]
        ]
    )
    save()
    await m.edit_message_text(
        f"<b>✅ Gate alterada com sucesso. gate → {gate.title()}</b>", reply_markup=kb
    )


@Client.on_callback_query(filters.regex(r"^refresh_gates$") & filters.user(ADMINS))
async def refresh(c: Client, m: CallbackQuery):
    global gates
    gates = GATES.copy()
    await m.answer("Gates reestabelecidas com sucesso.", show_alert=True)
