from asyncio.exceptions import TimeoutError
from datetime import datetime, timedelta

from pyrogram import Client, filters
from pyrogram.types import (
    CallbackQuery,
    ForceReply,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from config import ADMIN_CHAT
from database import cur, save
from utils import create_mention, insert_buy_sold

from ..admins.panel_items.select_gate import gates
from .buy_cc import chking


@Client.on_callback_query(filters.regex(r"^exchange$"))
async def exchange(c: Client, m: CallbackQuery):
    swap_is = cur.execute("SELECT exchange_is FROM bot_config").fetchone()[0]

    if swap_is == 0:
        return await m.answer("⚠️ Trocas desativadas pelo dono do bot", show_alert=True)

    tm = cur.execute("SELECT time_exchange FROM bot_config").fetchone()[0]
    td = timedelta(minutes=tm)

    now = (datetime.now() - td).strftime("%Y-%m-%d %H:%M:%S")

    num = cur.execute(
        "SELECT count() FROM cards_sold WHERE owner = ? and bought_date >= ? and is_checked = 1",
        [m.from_user.id, now],
    ).fetchone()[0]

    kb = InlineKeyboardMarkup(
        inline_keyboard=(
            []
            if not num
            else [
                [
                    InlineKeyboardButton(
                        "🔃 Iniciar troca", callback_data="start_exchange"
                    )
                ]
            ]
        )
        + [[InlineKeyboardButton("⬅️ Menu Principal", callback_data="start")]]
    )

    troca_info = f"""<b>🔃 Trocas</b>
<i>- Aqui você pode trocar CCs compradas que estejam die por novas CCs checadas e live.</i>

❇️ CCs disponíveis para troca: <b>{num}</b>"""

    await m.edit_message_text(troca_info, reply_markup=kb)


@Client.on_callback_query(filters.regex(r"^reembolso (?P<numero>\d+) (?P<valor>\d+)$"))
async def reembolso(c: Client, m: CallbackQuery):
    _, name_exchange = cur.execute(
        "SELECT gate_chk, gate_exchange FROM bot_config"
    ).fetchone()

    numero = int(m.matches[0]["numero"])
    valor = int(m.matches[0]["valor"])

    tm = cur.execute("SELECT time_exchange FROM bot_config").fetchone()[0]
    td = timedelta(minutes=tm)
    now = (datetime.now() - td).strftime("%Y-%m-%d %H:%M:%S")

    kb = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton("⬅️ Menu Principal", callback_data="start")]]
    )

    selected_cc = cur.execute(
        "SELECT number, month, year, cvv, level, added_date, vendor, bank, country, cpf, name, owner, plan, bought_date FROM cards_sold WHERE owner = ? AND bought_date >= ? AND number = ? AND plan != 'troca' AND plan != 'live'",
        [m.from_user.id, now, numero],
    ).fetchone()

    mention = create_mention(m.from_user)

    if not selected_cc:
        await m.answer(
            "⚠️ O tempo de troca expirou.",
            show_alert=True,
        )
    else:
        sent = await m.edit_message_text(
            "<b>🔄 Aguarde enquanto verifico o status da CC...</b>",
        )

        is_live = await gates[name_exchange]("|".join(str(i) for i in selected_cc[:4]))

        if is_live[0]:
            await m.edit_message_text(
                '❕ A CC informada está live, eu não posso reembolsá-la. Você ainda pode ver ela no seu histórico (em "Minhas informações").',
                reply_markup=kb,
            )
            cur.execute(
                "UPDATE cards_sold SET plan = ? WHERE number = ?",
                ["live", selected_cc[0]],
            )

            await c.send_message(
                ADMIN_CHAT,
                f"<b>🔄 O usuário {mention} pediu reembolso</b>\n\n"
                "Status: <b>☑️ Negado</b>\n"
                f"Valor: <s><b>R$ {valor}</b></s>\n\n"
                f"Cartão testado: <code>{'|'.join(str(i) for i in selected_cc[:4])}</code>",
            )
            save()
            return

        if is_live[0] is False:
            cur.execute(
                "UPDATE cards_sold SET is_checked = ? WHERE number = ?",
                [False, selected_cc[0]],
            )

            cur.execute(
                "UPDATE users SET balance = balance + ? WHERE id = ?",
                [valor, m.from_user.id],
            )

            await c.send_message(
                ADMIN_CHAT,
                f"<b>🔄 O usuário {mention} pediu reembolso</b>\n\n"
                "Status: <b>✅ Aprovado</b>\n"
                f"Valor: <b>R$ {valor}</b>\n\n"
                f"Cartão testado: <code>{'|'.join(str(i) for i in selected_cc[:4])}</code>",
            )

            return await m.edit_message_text(
                f"✅ Seu reembolso foi aprovado e o saldo de R$ {valor} devolvido a sua conta.\n\n"
                f"CC: <code>{'|'.join(str(i) for i in selected_cc[:4])}</code>",
                reply_markup=kb,
            )
        if is_live[0] is None:
            kb = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton("🔄 Tentar novamente", callback_data=m.data)]
                ]
            )

            return await m.edit_message_text(
                "❕ Ops, ocorreu um erro e não pude checar o status da CC. Tente novamente ou comunique o administrador.\n\n"
                f"CC: <code>{'|'.join(str(i) for i in selected_cc[:4])}</code>",
                reply_markup=kb,
            )
            
            
@Client.on_callback_query(filters.regex(r"^reembolsofull (?P<numero>\d+) (?P<valor>\d+)$"))
async def reembolsofull(c: Client, m: CallbackQuery):
    _, name_exchange = cur.execute(
        "SELECT gate_chk, gate_exchange FROM bot_config"
    ).fetchone()

    numero = int(m.matches[0]["numero"])
    valor = int(m.matches[0]["valor"])

    tm = cur.execute("SELECT time_exchange FROM bot_config").fetchone()[0]
    td = timedelta(minutes=tm)
    now = (datetime.now() - td).strftime("%Y-%m-%d %H:%M:%S")

    kb = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton("⬅️ Menu Principal", callback_data="start")]]
    )

    selected_cc = cur.execute(
        "SELECT number, month, year, cvv, level, added_date, vendor, bank, country, cpf, name, owner, plan, bought_date FROM cards_sold_full WHERE owner = ? AND bought_date >= ? AND number = ? AND plan != 'troca' AND plan != 'live'",
        [m.from_user.id, now, numero],
    ).fetchone()

    mention = create_mention(m.from_user)

    if not selected_cc:
        await m.answer(
            "⚠️ O tempo de troca expirou.",
            show_alert=True,
        )
    else:
        sent = await m.edit_message_text(
            "<b>🔄 Aguarde enquanto verifico o status da CC...</b>",
        )

        is_live = await gates[name_exchange]("|".join(str(i) for i in selected_cc[:4]))

        if is_live[0]:
            await m.edit_message_text(
                '❕ A CC informada está live, eu não posso reembolsá-la. Você ainda pode ver ela no seu histórico (em "Minhas informações").',
                reply_markup=kb,
            )
            cur.execute(
                "UPDATE cards_sold_full SET plan = ? WHERE number = ?",
                ["live", selected_cc[0]],
            )

            await c.send_message(
                ADMIN_CHAT,
                f"<b>FULL DADOS🔄 O usuário {mention} pediu reembolso</b>\n\n"
                "Status: <b>☑️ Negado</b>\n"
                f"Valor: <s><b>R$ {valor}</b></s>\n\n"
                f"Cartão testado: <code>{'|'.join(str(i) for i in selected_cc[:4])}</code>",
            )
            save()
            return

        if is_live[0] is False:
            cur.execute(
                "UPDATE cards_sold SET is_checked = ? WHERE number = ?",
                [False, selected_cc[0]],
            )

            cur.execute(
                "UPDATE users SET balance = balance + ? WHERE id = ?",
                [valor, m.from_user.id],
            )

            await c.send_message(
                ADMIN_CHAT,
                f"<b>FULL DADOS 🔄 O usuário {mention} pediu reembolso</b>\n\n"
                "Status: <b>✅ Aprovado</b>\n"
                f"Valor: <b>R$ {valor}</b>\n\n"
                f"Cartão testado: <code>{'|'.join(str(i) for i in selected_cc[:4])}</code>",
            )

            return await m.edit_message_text(
                f"✅ Seu reembolso foi aprovado e o saldo de R$ {valor} devolvido a sua conta.\n\n"
                f"CC: <code>{'|'.join(str(i) for i in selected_cc[:4])}</code>",
                reply_markup=kb,
            )
        if is_live[0] is None:
            kb = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton("🔄 Tentar novamente", callback_data=m.data)]
                ]
            )

            return await m.edit_message_text(
                "❕ Ops, ocorreu um erro e não pude checar o status da CC. Tente novamente ou comunique o administrador.\n\n"
                f"CC: <code>{'|'.join(str(i) for i in selected_cc[:4])}</code>",
                reply_markup=kb,
            )            


@Client.on_callback_query(filters.regex(r"^start_exchange$"))
async def start_exchange(c: Client, m: CallbackQuery):
    _, name_exchange = cur.execute(
        "SELECT gate_chk, gate_exchange FROM bot_config"
    ).fetchone()
    await m.message.delete()
    selected_cc = ""
    card = ""
    tm = cur.execute("SELECT time_exchange FROM bot_config").fetchone()[0]
    td = timedelta(minutes=tm)
    now = (datetime.now() - td).strftime("%Y-%m-%d %H:%M:%S")

    all_ccs = cur.execute(
        "SELECT number FROM cards_sold WHERE owner = ? and bought_date >= ? and is_checked = 1",
        [m.from_user.id, now],
    ).fetchall()

    ccs = "\n".join(f"<code>{cc[0]}</code>" for cc in all_ccs)

    troca_info = f"""<b>↘️ Envie somente o número da CC que você deseja trocar em resposta a esta mensagem.</b>

<b>⏳ Lista de CCs disponíveis para troca:</b>
{ccs}
<b>🛑 Para cancelar, use /cancel</b>."""

    await m.message.reply_text(troca_info, reply_markup=ForceReply())

    kb = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton("Menu", callback_data="start")]]
    )

    try:
        sent = await c.wait_for_message(
            m.message.chat.id, filters=filters.text, timeout=120
        )
    except TimeoutError:
        await m.message.reply_text(
            "❕ Não recebi uma resposta para o comando anterior e ele foi automaticamente cancelado.",
            reply_markup=kb,
        )
        return
    else:
        if sent.text.startswith("/cancel"):
            return await m.message.reply_text(
                "✅ Comando cancelado com sucesso.",
                reply_markup=kb,
            )

        # Obtendo novamente o status para caso o usuário tenha esperado quase 120s para responder.
        td = timedelta(minutes=tm)
        now = (datetime.now() - td).strftime("%Y-%m-%d %H:%M:%S")

        selected_cc = cur.execute(
            "SELECT number, month, year, cvv, level, added_date, vendor, bank, country, cpf, name, owner, plan, bought_date FROM cards_sold WHERE owner = ? AND bought_date >= ? AND number = ? AND plan != 'troca' AND plan != 'live'",
            [m.from_user.id, now, sent.text.split("|")[0]],
        ).fetchone()

        if not selected_cc:
            await m.message.reply_text(
                "❗️ A CC informada não é válida ou já passou o seu tempo de troca.",
                reply_markup=kb,
            )
        else:
            sent = await m.message.reply_text(
                "⏰ Aguarde, estou verificando o status da CC informada...",
            )

            is_live = await gates[name_exchange](
                "|".join(str(i) for i in selected_cc[:4])
            )

            if is_live[0]:
                await sent.edit_text(
                    "❕ A CC informada está live, eu não posso trocá-la.",
                    reply_markup=kb,
                )
                cur.execute(
                    "UPDATE cards_sold SET plan = ? WHERE number = ?",
                    ["live", selected_cc[0]],
                )
                mention = create_mention(m.from_user)

                await c.send_message(
                    ADMIN_CHAT,
                    f"<b> ⚠️ Troca do usuário {mention} não realizada, {'|'.join(str(i) for i in selected_cc[:4])} cc esta live</b>",
                )
                save()
                return

            if is_live[0] is False:
                await sent.edit_text("⏰ Realizando troca...")
                cur.execute("DELETE FROM cards_sold WHERE number = ?", [selected_cc[0]])

                search_for = "level" if selected_cc[10] == "unit" else "bin"
                search = {
                    "bin": selected_cc[0][:6],
                    "level": selected_cc[4],
                }

                new_ccs = cur.execute(
                    f"SELECT number, month, year, cvv, level, added_date, vendor, bank, country, cpf, name FROM cards WHERE {search_for} = ? and pending = 0 ORDER BY RANDOM() LIMIT 20",
                    [search[search_for]],
                ).fetchall()

                if not new_ccs:
                    return await sent.edit_text(
                        "<b>⚠️ Sem ccs desse nivel disponiveis para troca.</b>",
                        reply_markup=kb,
                    )
                live = 0
                for cc in new_ccs:
                    cur.execute(
                        "UPDATE cards SET pending = 1 WHERE number = ?", [cc[0]]
                    )
                    card = "|".join(str(i) for i in cc[:4])
                    rt = await chking(card)
                    if rt[0]:  # live
                        base = f"""<b>💳 Produto</b>\n\n<code>{card}</code>"""

                        list_dados = cc + (m.from_user.id, "troca", True)

                        insert_buy_sold(list_dados)

                        cur.execute(
                            "DELETE FROM cards WHERE number = ?",
                            [cc[0]],
                        )

                        await sent.edit_text(base)
                        await sent.reply_text(
                            "♻ Troca realizada com sucesso.</b>", reply_markup=kb
                        )
                        values = "number, month, year, cvv, level, added_date, vendor, bank, country, cpf, name, owner, plan, bought_date"
                        cur.execute(
                            f"INSERT INTO cards_dies({values}) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                            selected_cc,
                        )
                        mention = create_mention(m.from_user)
                        base = f"""<b>♻ O usuário {mention} trocou </b>\n<del>{"|".join(str(i) for i in selected_cc[:4])}</del>\n<code>{card}</code>"""
                        await c.send_message(ADMIN_CHAT, base)
                        live += 1
                        break

                    elif rt[0] is None:
                        cur.execute(
                            "UPDATE cards SET pending = 0 WHERE number = ?", [cc[0]]
                        )
                    else:  # die
                        ...
                if live == 0:
                    await m.edit_message_text("<b>⚠️ Chame o suporte</b>", reply_markup=kb)

                save()
            if is_live[0] is None:
                return await sent.edit_text(
                    "❕ Ops, ocorreu um erro e não pude checar o status da CC. Tente novamente ou comunique o administrador.",
                    reply_markup=kb,
                )
