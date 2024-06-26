import asyncio
from dataclasses import dataclass
from typing import Optional
from pyrogram import Client, filters
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from database import cur, save
from utils import log_games

def wallet(user_id):
    return cur.execute(
        'SELECT id, balance FROM users WHERE id=?', [user_id]
    ).fetchone()


@dataclass
class Winner:
    win: int
    max_win: Optional[int] = None


@dataclass
class Loser:
    lose: list


@dataclass
class Game:
    name: str
    loser_points: Optional[Loser] = None
    winner_points: Optional[Winner] = None
    wins = {1: 15, 22: 20, 43: 30, 64: 40}


class Casino:
    Basket = Game('Basket', Loser([1, 2, 3]), Winner(4, 5))
    Bowling = Game('Bowling', Loser([1, 2, 3, 4, 5]), Winner(6))
    Dart = Game('Dart', Loser([1, 2, 3, 4, 5]), Winner(6))
    Dice = Game('Dice', Loser([1, 2, 3, 4, 5]), Winner(6))
    Sort = Game('Sort')

    @classmethod
    def Result(
        cls,
        result: int,
        win_cash: list,
        debit: float,
        game: Game,
        balance: float,
    ) -> tuple:
        rst = ''
        if game.name in ('Bowling', 'Dart', 'Dice'):
            if result == game.winner_points.win:
                balance += win_cash[0]
                rst = f'🥲 Ganhou {win_cash[0]} R$'
                msg = f'<i>🎉 Você ganhou <b>+ {win_cash[0]} R$</b></i>'
            else:
                rst = f'🤑 Perdeu {debit}'
                msg = f'<i>❌ Você perdeu <b>- {debit} R$</b></i>'

        elif game.name == 'Basket':
            if result == game.winner_points.win:
                balance += win_cash[0]
                rst = f'🥲 Ganhou {win_cash[0]} R$'
                msg = f'<i>🎉 Você ganhou <b>+ {win_cash[0]} R$</b></i>'

            elif result == game.winner_points.max_win:
                balance += win_cash[1]
                msg = f'<i>🎉 Você ganhou <b>+ {win_cash[1]} R$</b></i>'
            else:
                rst = f'🤑 Perdeu {debit} R$'
                msg = f'<i>❌ Você perdeu <b>- {debit} R$</b></i>'
        else:
            if result in list(game.wins):
                balance += game.wins[result]
                rst = f'🥲 Ganhou {game.wins[result]} R$'
                msg = f'<i>🎉 Você ganhou <b>+ {game.wins[result]} R$</b></i>'
            else:
                rst = f'🤑 Perdeu {debit} R$'
                msg = f'<i>❌ Você perdeu <b>- {debit} R$</b></i>'
        return game.name, balance, msg, rst


@Client.on_message(filters.command(['casino', 'cassino']))
@Client.on_callback_query(filters.regex(r'casino'))
async def start_casino(c: Client, m: Message ):
    user_id = m.from_user.id

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton('🎲 Dado', callback_data='dice'), 
                InlineKeyboardButton('✌️ Impar ou Par', callback_data='odd'), 
            ],
            [
                InlineKeyboardButton('🏀 Basquete', callback_data='basket'),
                InlineKeyboardButton('🎯 Dardo', callback_data='dart'),
            ],
            [
                InlineKeyboardButton('🎳 Boliche', callback_data='bowling'),
                InlineKeyboardButton('🎰 Sorte', callback_data='lucky'),
            ],
            [InlineKeyboardButton('⬅️ Menu Principal', callback_data='start')],
        ]
    )
    mmm = '<a href="https://images.unsplash.com/photo-1518895312237-a9e23508077d?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=1184&q=80">🎰</a> <i>Gosta de apostas e ganhar dinheiro no bot ao mesmo tempo? Está no lugar certo.</i>'
    msg = """ {}

<b>🥇 Seu Perfil:</b>
<b> ├👤 ID:</b> <code>{}</code>
<b> └💸 Saldo: <b>R${}</b>
""".format(
        mmm, *wallet(user_id)
    )

    if isinstance(m, Message):
        await m.reply_text(text=msg, reply_markup=kb)
    else:
        await m.edit_message_text(text=msg, reply_markup=kb)


@Client.on_callback_query(filters.regex(r'^dice'))  # falta
async def dice(c: Client, m: CallbackQuery):
    await m.message.delete()
    await m.message.reply_to_message.delete() if m.message.reply_to_message else ...
    user_id, balance = wallet(m.from_user.id)

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton('✅ Continue', callback_data='continue'),
                InlineKeyboardButton('❌ Cancel', callback_data='cancel'),
            ]
        ]
    )
    confirm = await m.message.reply_text(
        """<b>💰 jogue o dado se der 6 ganhe 15R$</b>\n<i>⚠ custo 4 R$</i>""",
        reply_markup=kb,
    )

    rt = await c.wait_for_callback_query(chat_id=user_id)

    if rt.data == 'continue':
        kb.inline_keyboard[0].pop(0)
        (
            kb.inline_keyboard[0][0].text,
            kb.inline_keyboard[0][0].callback_data,
        ) = ('⬅️ Menu Principal', 'casino')
        await confirm.delete()
        balance -= 4

        if balance < 0:
            kb.inline_keyboard[0][0].callback_data = 'start'
            return await m.message.reply_text(
                '<b>💸 Saldo Insuficiente.</b>', reply_markup=kb
            )

        sort = await c.send_dice(chat_id=m.message.chat.id, emoji='🎲')
        await asyncio.sleep(3)
        name, balance, msg, rst = Casino.Result(
            sort.dice.value, [15], 4, Casino.Dice, balance
        )
        await m.message.reply_text(msg, reply_markup=kb)

        cur.execute(
            'UPDATE users SET balance=? WHERE id=?', [balance, user_id]
        )
        save()
        await c.send_message(
            chat_id=ADMIN_CHAT, text=log_games(name, m.from_user, rst, balance)
        )
    else:
        await confirm.delete()
        kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton('⬅️ Menu Principal', callback_data='casino')]
            ]
        )
        return await m.message.reply_text(
            '<b>✅️ Cancelado com Sucesso</b>', reply_markup=kb
        )


@Client.on_callback_query(filters.regex(r'^odd'))
async def odd(c: Client, m: CallbackQuery):
    await m.message.delete()
    await m.message.reply_to_message.delete() if m.message.reply_to_message else ...
    user_id, balance = wallet(m.from_user.id)
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton('✌️Par', callback_data='par'),
                InlineKeyboardButton('☝ Impar', callback_data='impar'),
                InlineKeyboardButton('❌ Cancel', callback_data='cancel'),
            ]
        ]
    )
    confirm = await m.message.reply_text(
        """<b>💰 Aposte em PAR ou IMPAR se acertar ganhar 20 R$</b>\n<i>⚠ custo 10 R$</i>""",
        reply_markup=kb,
    )

    rt = await c.wait_for_callback_query(chat_id=user_id)

    if rt.data != 'cancel':
        result_ask = rt.data
        await confirm.delete()
        balance -= 10

        if balance < 0:
            kb.inline_keyboard[0].pop(0)
            kb.inline_keyboard[0].pop(0)
            (
                kb.inline_keyboard[0][0].text,
                kb.inline_keyboard[0][0].callback_data,
            ) = ('⬅️ Menu Principal', 'casino')
            return await m.message.reply_text(
                '<b>💸 Saldo Insuficiente.</b>', reply_markup=kb
            )

        kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton('⬅️ Menu Principal', callback_data='casino')]
            ]
        )
        dice_1 = await c.send_dice(chat_id=m.message.chat.id, emoji='🎲')
        dice_2 = await c.send_dice(chat_id=m.message.chat.id, emoji='🎲')
        dice_3 = await c.send_dice(chat_id=m.message.chat.id, emoji='🎲')
        await asyncio.sleep(3.5)
        result_dice = (
            'par'
            if sum(int(d.dice.value) for d in [dice_1, dice_2, dice_3]) % 2
            == 0
            else 'impar'
        )

        if result_dice == result_ask.lower():
            balance += 20
            rst = f'🥲 Ganhou {20} R$'
            await m.message.reply_text(
                f'<i>🎉 you win <b>+25 R$</b></i>', reply_markup=kb
            )

        else:
            rst = f'🤑 Perdeu {10} R$'
            await m.message.reply_text(
                '<i>❌ you lose <b>- 10 R$</b></i>', reply_markup=kb
            )
        cur.execute(
            'UPDATE users SET balance=? WHERE id=?', [balance, user_id]
        )
        save()
        await c.send_message(
            chat_id=ADMIN_CHAT,
            text=log_games('Par ou Impar', m.from_user, rst),
        )
    else:
        await confirm.delete()
        kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton('⬅️ Menu Principal', callback_data='casino')]
            ]
        )
        return await m.message.reply_text(
            '<b>✅️ Cancelado com Sucesso</b>', reply_markup=kb
        )


@Client.on_callback_query(filters.regex(r'^basket'))
async def basket(c: Client, m: CallbackQuery):
    await m.message.delete()
    await m.message.reply_to_message.delete() if m.message.reply_to_message else ...
    user_id, balance = wallet(m.from_user.id)
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton('✅ Continue', callback_data='continue'),
                InlineKeyboardButton('❌ Cancel', callback_data='cancel'),
            ]
        ]
    )
    confirm = await m.message.reply_text(
        """<b>💰 Jogue na cesta\n<i>- se entrar batendo no aro ganhe 6
- se for perfeito 8 R$</i>
</b>\n<i>⚠ custo 4 R$</i>""",
        reply_markup=kb,
    )

    rt = await c.wait_for_callback_query(chat_id=user_id)
    if rt.data == 'continue':
        kb.inline_keyboard[0].pop(0)
        (
            kb.inline_keyboard[0][0].text,
            kb.inline_keyboard[0][0].callback_data,
        ) = ('⬅️ Menu Principal', 'casino')
        await confirm.delete()
        balance -= 2

        if balance < 0:
            kb.inline_keyboard[0][0].callback_data = 'start'
            return await m.message.reply_text(
                '<b>💸 Saldo Insuficiente.</b>', reply_markup=kb
            )

        sort = await c.send_dice(chat_id=m.message.chat.id, emoji='🏀')
        await asyncio.sleep(3.8)
        name, balance, msg, rst = Casino.Result(
            sort.dice.value, [6, 8], 4, Casino.Basket, balance
        )
        await m.message.reply_text(msg, reply_markup=kb)
        cur.execute(
            'UPDATE users SET balance=? WHERE id=?', [balance, user_id]
        )
        save()
        await c.send_message(
            chat_id=ADMIN_CHAT, text=log_games(name, m.from_user, rst, balance)
        )
    else:
        await confirm.delete()
        kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton('⬅️ Menu Principal', callback_data='casino')]
            ]
        )
        return await m.message.reply_text(
            '<b>✅️ Cancelado com Sucesso</b>', reply_markup=kb
        )


@Client.on_callback_query(filters.regex(r'^bowling'))
async def bowling(c: Client, m: CallbackQuery):
    await m.message.delete()
    await m.message.reply_to_message.delete() if m.message.reply_to_message else ...
    user_id, balance = wallet(m.from_user.id)
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton('✅ Continue', callback_data='continue'),
                InlineKeyboardButton('❌ Cancel', callback_data='cancel'),
            ]
        ]
    )
    confirm = await m.message.reply_text(
        """<b>💰 fazendo o STRIKE ganha 20R$</b>
<i>⚠ custo 8 R$</i>""",
        reply_markup=kb,
    )
    rt = await c.wait_for_callback_query(chat_id=user_id)
    await confirm.delete()

    if rt.data == 'continue':
        kb.inline_keyboard[0].pop(0)
        (
            kb.inline_keyboard[0][0].text,
            kb.inline_keyboard[0][0].callback_data,
        ) = ('⬅️ Menu Principal', 'casino')
        balance -= 8
        if balance < 0:
            kb.inline_keyboard[0][0].callback_data = 'start'
            return await m.message.reply_text(
                '<b>💸 Saldo Insuficiente.</b>', reply_markup=kb
            )
        sort = await c.send_dice(chat_id=m.message.chat.id, emoji='🎳')
        await asyncio.sleep(4.5)
        name, balance, msg, rst = Casino.Result(
            sort.dice.value, [20], 8, Casino.Bowling, balance
        )
        await m.message.reply_text(msg, reply_markup=kb)
        cur.execute(
            'UPDATE users SET balance=? WHERE id=?', [balance, user_id]
        )
        save()
        await c.send_message(
            chat_id=ADMIN_CHAT, text=log_games(name, m.from_user, rst, balance)
        )
    else:
        await confirm.delete()
        kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton('⬅️ Menu Principal', callback_data='casino')]
            ]
        )
        return await m.message.reply_text(
            '<b>✅️ Cancelado com Sucesso</b>', reply_markup=kb
        )


@Client.on_callback_query(filters.regex(r'^dart'))
async def dart(c: Client, m: CallbackQuery):
    await m.message.delete()
    await m.message.reply_to_message.delete() if m.message.reply_to_message else ...
    user_id, balance = wallet(m.from_user.id)
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton('✅ continue', callback_data='continue'),
                InlineKeyboardButton('❌ Cancel', callback_data='cancel'),
            ]
        ]
    )
    confirm = await m.message.reply_text(
        """<b>💰 acertando no alvo ganho de 15R$</b>\n<i>⚠ custo 5 R$</i>""",
        reply_markup=kb,
    )
    rt = await c.wait_for_callback_query(chat_id=user_id)

    if rt.data == 'continue':
        kb.inline_keyboard[0].pop(0)
        (
            kb.inline_keyboard[0][0].text,
            kb.inline_keyboard[0][0].callback_data,
        ) = ('⬅️ Menu Principal', 'casino')
        await confirm.delete()
        balance -= 5

        if balance < 0:
            kb.inline_keyboard[0][0].callback_data = 'start'
            return await m.message.reply_text(
                '<b>💸 Saldo Insuficiente.</b>', reply_markup=kb
            )

        sort = await c.send_dice(chat_id=m.message.chat.id, emoji='🎯')
        await asyncio.sleep(3)
        name, balance, msg, rst = Casino.Result(
            sort.dice.value, [15], 5, Casino.Dart, balance
        )
        await m.message.reply_text(msg, reply_markup=kb)
        cur.execute(
            'UPDATE users SET balance=? WHERE id=?', [balance, user_id]
        )
        save()
        await c.send_message(
            chat_id=ADMIN_CHAT, text=log_games(name, m.from_user, rst, balance)
        )
    else:
        await confirm.delete()
        kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton('⬅️ Menu Principal', callback_data='casino')]
            ]
        )
        return await m.message.reply_text(
            '<b>✅️ Cancelado com Sucesso</b>', reply_markup=kb
        )


@Client.on_callback_query(filters.regex(r'^lucky'))
async def lucky(c: Client, m: CallbackQuery):
    await m.message.delete()
    await m.message.reply_to_message.delete() if m.message.reply_to_message else ...
    user_id, balance = wallet(m.from_user.id)
    balance -= 5
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton('✅ continue', callback_data='continue'),
                InlineKeyboardButton('❌ Cancel', callback_data='cancel'),
            ]
        ]
    )
    confirm = await m.message.reply_text(
        """<b>Combinação | Ganho R$
➖➖➖       |  15
🍇🍇🍇       |  20
🍋🍋🍋       |  30
7️⃣7️⃣7️⃣       |  40</b>

<i>⚠ custo 5 R$</i>
""",
        reply_markup=kb,
    )

    rt = await c.wait_for_callback_query(chat_id=user_id)
    await confirm.delete()

    if rt.data == 'continue':
        kb.inline_keyboard[0].pop(0)
        (
            kb.inline_keyboard[0][0].text,
            kb.inline_keyboard[0][0].callback_data,
        ) = ('⬅️ Menu Principal', 'casino')
        if balance < 0:
            kb.inline_keyboard[0][0].callback_data = 'start'
            return await m.message.reply_text(
                '<b>💸 Saldo Insuficiente.</b>', reply_markup=kb
            )

        sort = await c.send_dice(chat_id=m.message.chat.id, emoji='🎰')
        await asyncio.sleep(2.7)
        name, balance, msg, rst = Casino.Result(
            sort.dice.value, [], 5, Casino.Sort, balance
        )
        await m.message.reply_text(msg, reply_markup=kb)
        cur.execute(
            'UPDATE users SET balance=? WHERE id=?', [balance, user_id]
        )
        save()
        await c.send_message(
            chat_id=ADMIN_CHAT, text=log_games(name, m.from_user, rst, balance)
        )
    else:
        await confirm.delete()
        kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton('⬅️ Menu Principal', callback_data='casino')]
            ]
        )
        return await m.message.reply_text(
            '<b>✅️ Cancelado com Sucesso</b>', reply_markup=kb
        )
