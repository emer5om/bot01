import os
import re
from asyncio.exceptions import TimeoutError
from datetime import datetime
from typing import Union

from pyrogram import Client, filters
from pyrogram.types import (
    ForceReply,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    ReplyKeyboardRemove,
)

from config import ADMINS
from database import cur, save
from utils import search_bin
from ..admins.panel_items.select_gate import gates

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

from config import ADMIN_CHAT
from config import GRUPO_PUB
from database import cur, save
from utils import (
    create_mention,
    get_info_wallet,
    get_price,
    insert_buy_sold,
    insert_sold_balance,
    lock_user_buy,
    msg_buy_off_user,
    msg_buy_user,
    msg_group_adm,
    msg_group_publico,
    search_bin,
)

from ..admins.panel_items.select_gate import gates

gates_is_on = True if (len(gates) >= 1) else False
T = 0.1



async def chking(card):
    global gates, gates_is_on, T
    name_chk, _ = cur.execute(
        "SELECT gate_chk_publico, gate_exchange FROM bot_config"
    ).fetchone()
   # name_chk = "companychk"
    if name_chk == "pre-auth":
        T = 2
    else:
        T = 0.1

    return await gates[name_chk](card)


def get_numbers_sequence(content):
    caracteres = str(content.replace(r'\n', '\n').replace('\n', ' '))
    sublista = []
    blacklist = ['.', ':']
    for caractere in caracteres:
        if caractere.isnumeric() or caractere in blacklist:
            sublista.append(caractere)
        
        else:
            sublista.append(' ')

    
    results = ''.join(sublista).split()
    lista = []
    
    for result in results:
        if result.isnumeric():
            lista.append(result)

    return lista



def separator(content):
    numeros = get_numbers_sequence(content.replace(' ', '|'))
    result = []
    ccs = []

    if len(numeros) >= 4:
        cc_format = []
        for numero in numeros:
            numero = numero.replace(':', '').replace('.', '')
            try:
                if len(cc_format) == 0 and len(numero) == 16 or len(numero) == 15:
                    cc_format.append(numero)
                
                elif len(cc_format) == 1 and int(numero) >= 1 and int(numero) <= 12:
                    cc_format.append(numero)
                
                elif len(cc_format) == 2 and int(numero.replace('20', '')) >= 13 and int(numero.replace('20', '')) <= 99 or len(cc_format) == 2 and int(numero) >= 13 and int(numero) <= 99:
                    if len(numero) == 2:
                        numero = '20'+numero
                        
                    cc_format.append(numero)

                elif len(cc_format) == 3 and len(numero) == 3 or len(numero) == 4:
                    cc_format.append(numero)
                    if len(cc_format) == 4:
                        
                        ccs.append((cc_format))
                        cc_format = []
                        
                    else:
                        
                        cc_format = []

                else:
                    pass

            except:
                pass
    
    for cc in ccs:
        try:
            result.append(f'{cc[0]}|{cc[1]}|{cc[2]}|{cc[3]}')

        except:
            pass

    return list(result)


@Client.on_message(filters.regex(r"/separador( (?P<cards>.+))?", re.S))
async def separador(c: Client, m: Message):
    cards = m.matches[0]["cards"]

    if cards:
        ccs = '\n'.join(separator(cards))
        if not ccs:
            text = (
                "❌ Não encontrei CCs na sua mensagem. Envie elas como texto ou arquivo."
            )
        else:
            f = open("separadas.txt", "w")
            f.write(ccs)
            f.close()
            text = f"{ccs}"
        sent = await m.reply_text(text, quote=True)

        if open("separadas.txt").read() != "":
            await sent.reply_document(open("separadas.txt", "rb"), quote=True)
        os.remove("separadas.txt")

        return

    await m.reply_text(
        "💳 Modo separação, envie as ccs para separar como texto ou arquivo",
        reply_markup=ForceReply(),
    )

    first = True
    while True:
        if not first:
            await m.reply_text(
                "✅ Envie mais CCs ou digite /done para sair do modo de separação",
                reply_markup=ForceReply(),
            )

        try:
            msg = await c.wait_for_message(m.chat.id, timeout=300)
        except TimeoutError:
            kb = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton("❮ ❮", callback_data="shop")]
                ]
            )

            await m.reply_text(
                "❕ Não recebi uma resposta para o comando anterior e ele foi automaticamente cancelado.",
                reply_markup=kb,
            )
            return

        first = False

        if not msg.text and (
            not msg.document or msg.document.file_size > 100 * 1024 * 1024
        ):  # 100MB
            await msg.reply_text(
                "❕ Eu esperava um texto ou documento contendo as CCs.", quote=True
            )
            continue
        if msg.text and msg.text.startswith("/done"):
            break

        if msg.document:
            cache = await msg.download()
            with open(cache) as f:
                msg.text = f.read()
            os.remove(cache)

        ccs = '\n'.join(separator(msg.text))
        f = open("separadas.txt", "w")
        f.write(ccs)
        f.close()

        if not ccs:
            text = (
                "❌ Não encontrei CCs na sua mensagem. Envie elas como texto ou arquivo."
            )
        else:
            text = f"{ccs}"
        sent = await msg.reply_text(text, quote=True)

        if open("separadas.txt").read() != "":
            await sent.reply_document(open("separadas.txt", "rb"), quote=True)
        os.remove("separadas.txt")

    await m.reply_text(
        "⚠️ Você Saiu do modo de separação de CCs.", reply_markup=ReplyKeyboardRemove()
    )
    
    
    
    
@Client.on_message(filters.regex(r"/chk( (?P<cards>.+))?", re.S))
async def chk(c: Client, m: Message):
    user_id = m.from_user.id
    balance: int = cur.execute("SELECT balance FROM users WHERE id = ?", [user_id]).fetchone()[0]  # fmt: skip

    cctest = m.matches[0]["cards"]
    price = 2
    if balance < price:
        await m.reply_text(
            "📛<b> Ops!! Parece que você não pode usar o checker, porquê você não tem saldo suficiente, recarregue no menu principal.</b>")
            
    elif not cctest:
        await m.reply_text(
            "<b>⚠️ Insira uma cc para testar:</b>")
    else:
    	await m.reply_text(
            "<b>Estou testando seu cartão, aguarde 🚀✅</b>")
    	global gates
    	card_bin = cctest[:6]
    	info = await search_bin(card_bin)
    	live_or_die = await chking(cctest)
    	await asyncio.sleep(T)
    	if live_or_die[0]:
    		new_balance = round(balance - price, 2)
    		cur.execute(
                    "UPDATE users SET balance = round(balance - ?, 2) WHERE id = ?",
                    [price, user_id],
                )
    		await m.reply_text(
            f"Aprovado com sucesso ✅\n\nVerifique seu cartão testado:\n\n<code>{cctest}|{info['vendor']}|{info['card_type']}|{info['level']}|{info['bank']}</code>\n\n<b>Foram descontados R$ 2,00 da sua carteira</b>\n\n<b>Saldo atual: {new_balance}</b>")
    	elif live_or_die[0] is None:
    			await m.reply_text(
            f"<b>⚠️ Ocorreu um erro, não pude testar seu cartão, tente novamente em alguns segundos ⚠️<b>")
    	else:
    				await m.reply_text(
            f"Infelizmente esse cartão foi reprovado ❌\n\nVerifique seu cartão testado:\n\n<code>{cctest}|{info['vendor']}|{info['card_type']}|{info['level']}|{info['bank']}</code>\n\n<b>Foram descontados R$ 0,00 da sua carteira</b>\n\n")
    #	if live_or_die[0] is None:
    		#await m.reply_text(
          #  "{live_or_die}")
        