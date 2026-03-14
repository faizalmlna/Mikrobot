import os
import re
import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

# ========= FILE & SCRIPT SSH=========
from mikrotik_vbox import (
    ping_status as vbox_ping,
    traceroute_status as vbox_traceroute,
    traffic_status as vbox_traffic,
)

from mikrotik_vmware720 import (
    ping_status as vmware_ping,
    traceroute_status as vmware_traceroute,
    traffic_status as vmware_traffic,
)


# ======================
# CONFIG
# ======================
BOT_TOKEN = os.getenv("BOT_TOKEN")
BOT_USERNAME = os.getenv("BOT_NAME")
GROUP_ID_1 = int(os.getenv("BOT_GROUP_ID_1"))
GROUP_ID_2 = int(os.getenv("BOT_GROUP_ID_2"))
THREAD_ID_1 = int(os.getenv("BOT_THREAD_ID_1"))

router_set = {
    "vmware_720": "172.17.4.1",
    "testing": "172.17.4.120",
    #"neoc" : "172.24.1.1"
}

logging.basicConfig(level=logging.INFO)

# ======================
# HELP
# ======================
HELP_TEXT = """
📌 *NetBot Commands*

🖥 *VMWARE*
• `internet  status vmware`
• `traceroute vmware`
• `traffic monitor vmware`

🖥 *VBOX*
• `internet vbox status`
• `traceroute vbox`
• `traffic monitor vbox`


📂 *Menu*
• `/start` → buka menu
• `/help` → daftar perintah

⌨ *Manual (Group)*
• `@aqbkn_bot help`
• `@aqbkn_bot internet vmware status`
"""

    

# ======================
# MENU
# ======================
CATEGORIES = {
    "VBOX": "menu_vbox",
    "VMWARE": "menu_vmware",
}

SUBCATEGORIES = {
    "menu_vbox": [
        ("Ping", "vbox_ping"),
        ("Traceroute", "vbox_traceroute"),
        ("Live Traffic", "vbox_traffic"),
        ("⬅ Back", "back_main"),
    ],
    "menu_vmware": [
        ("Ping", "vmware_ping"),
        ("Traceroute", "vmware_traceroute"),
        ("Live Traffic", "vmware_traffic"),
        ("⬅ Back", "back_main"),
    ],
}

# ======================
# PARSER PING
# ======================
def parse_ping(output, router_name):
    if not output or "ERROR" in output or "Unable" in output:
        return (
            f"NETBOT – {router_name}\n\n"
            f"Internet Status : DOWN\n"
            f"Reason          : SSH connection failed\n"
            f"Target          : 8.8.8.8"
        )

    loss = re.search(r"packet-loss=([0-9]+)%", output)
    avg = re.search(r"avg-rtt=([0-9.]+)", output)
    maxr = re.search(r"max-rtt=([0-9.]+)", output)

    packet_loss = loss.group(1) if loss else "N/A"
    avg_rtt = avg.group(1) if avg else "N/A"
    max_rtt = maxr.group(1) if maxr else "N/A"

    status = "UP" if packet_loss != "100" else "DOWN"

    return (
        f"NETBOT – {router_name}\n\n"
        f"Internet Status : {status}\n"
        f"Packet Loss     : {packet_loss}%\n"
        f"Avg RTT         : {avg_rtt} ms\n"
        f"Max RTT         : {max_rtt} ms\n"
        f"Target          : 8.8.8.8"
    )


# ======================
# PARSER TRACEROUTE
# ======================
def parse_traceroute(output, router_name, target="8.8.8.8"):

    if not output or "ERROR" in output:
        return (
            f"NETBOT – {router_name}\n\n"
            f"Internet Status : DOWN\n"
            f"Reason          : SSH / traceroute failed\n"
            f"Target          : {target}"
        )

    blocks = output.split("Columns:")
    last_block = blocks[-1]
    lines = last_block.splitlines()

    hop_count = 0
    target_line = None

    for line in lines:
        line = line.strip()
        if re.match(r"^\d+\s+", line):
            hop_count += 1

        if target in line:
            target_line = line

    if not target_line:
        return (
            f"NETBOT – {router_name}\n\n"
            f"Internet Status : DEGRADED\n"
            f"Reason          : Target not reached\n"
            f"Target          : {target}"
        )

    cols = re.split(r"\s{2,}", target_line)

    try:
        loss = cols[2]
        avg = cols[5]
        worst = cols[7]
    except IndexError:
        return (
            f"NETBOT – {router_name}\n\n"
            f"Internet Status : DEGRADED\n"
            f"Reason          : Unable to parse traceroute\n"
            f"Target          : {target}"
        )

    status = "UP"
    if loss == "100%":
        status = "DOWN"
    elif loss != "0%":
        status = "DEGRADED"

    return (
        f"NETBOT – {router_name}\n\n"
        f"Internet Status : {status}\n"
        f"Target          : {target}\n"
        f"Hops            : {hop_count}\n"
        f"Packet Loss     : {loss}\n"
        f"Avg RTT         : {avg} ms\n"
        f"Worst RTT       : {worst} ms"
    )


# ======================
# PARSER TRAFFIC
# ======================
def parse_traffic(output, router_name, interface="ether1"):
    if not output or "ERROR" in output:
        return (
            f"NETBOT – {router_name}\n\n"
            f"Traffic Status : ERROR\n"
            f"Interface      : {interface}"
        )
    rx_rate = re.search(r"rx-bits-per-second:\s*([0-9.]+\s*[a-zA-Z]+)", output)
    tx_rate = re.search(r"tx-bits-per-second:\s*([0-9.]+\s*[a-zA-Z]+)", output)

    rx_rate_val = rx_rate.group(1) if rx_rate else "N/A"
    tx_rate_val = tx_rate.group(1) if tx_rate else "N/A"

    return (
        f"NETBOT – {router_name}\n\n"
        f"Interface : {interface}\n\n"
        f"RX        : {rx_rate_val}\n"
        f"TX Rate    : {tx_rate_val}"
    )



#====== RUN SCRIPT ===========
    #===============VBOX================================
async def run_vbox_ping(update, context):
    msg = await update.effective_message.reply_text("⏳ Ping VBOX...")
    loop = asyncio.get_running_loop()

    raw = await loop.run_in_executor(None,vbox_ping , router_set)
    result = parse_ping(raw, "MIKROTIK VBOX")

    await msg.edit_text(result)

async def run_vbox_traceroute(update, context):
    msg = await update.effective_message.reply_text("⏳ Traceroute VBOX…")
    loop = asyncio.get_running_loop()

    raw = await loop.run_in_executor(None,vbox_traceroute , router_set)
    result = parse_traceroute(raw, "MIKROTIK VBOX")

    await msg.edit_text(result)

async def run_vbox_traffic(update, context):
    msg = await update.effective_message.reply_text("📡 Live Traffic VBOX…")

    loop = asyncio.get_running_loop()

    for i in range(5):
        raw = await loop.run_in_executor(
            None,
            vbox_traffic,
            router_set
        )

        result = parse_traffic(
            raw,
            "MIKROTIK VBOX",
            "ether1"
        )
        result += "\u200b" * i

        await msg.edit_text(result)

        await asyncio.sleep(1)

#=======VMWARE==============================
async def run_vmware_ping(update, context):
    msg = await update.effective_message.reply_text("⏳ Ping VMWARE...")
    loop = asyncio.get_running_loop()

    raw = await loop.run_in_executor(None,vmware_ping , router_set)
    result = parse_ping(raw, "MIKROTIK VMWARE")

    await msg.edit_text(result)

async def run_vmware_traceroute(update, context):
    msg = await update.effective_message.reply_text("⏳ Traceroute VMWARE…")
    loop = asyncio.get_running_loop()

    raw = await loop.run_in_executor(None,vmware_traceroute , router_set)
    result = parse_traceroute(raw, "MIKROTIK VMWARE")

    await msg.edit_text(result)

async def run_vmware_traffic(update, context):
    msg = await update.effective_message.reply_text("📡 Live Traffic VBOX…")

    loop = asyncio.get_running_loop()

    for i in range(5):
        raw = await loop.run_in_executor(
            None,
            vmware_traffic,
            router_set
        )

        result = parse_traffic(
            raw,
            "MIKROTIK VMWARE",
            "ether1"
        )
        result += "\u200b" * i

        await msg.edit_text(result)

        await asyncio.sleep(1)


#=======================================

# ======================
# command /help dan /start
# ======================
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    chat = update.effective_chat
    if chat.type in ["group", "supergroup"]:
        if chat.id not in [GROUP_ID_1, GROUP_ID_2]:
            await update.message.reply_text(
                "❌ Maaf group ini tidak diizinkan menggunakan bot."
            )
            return
            
    keyboard = [
        [InlineKeyboardButton(text, callback_data=data)]
        for text, data in CATEGORIES.items()
    ]
    await update.message.reply_text(
        "📌 Pilih device:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    chat = update.effective_chat
    thread_id = update.message.message_thread_id

    if chat.type in ["group", "supergroup"]:

        if chat.id == GROUP_ID_1 and thread_id == THREAD_ID_1:
            pass

        elif chat.id == GROUP_ID_2:
            pass

        else:
            await update.message.reply_text(
                "❌ Group / thread ini tidak diizinkan."
            )
            return

    await update.message.reply_text(
        HELP_TEXT,
        parse_mode="Markdown"
    )
# ======================
# BUTTON COMMAND
# ======================
import asyncio

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    # ===== MENU =====
    if data == "menu_vbox":
        keyboard = [
            [InlineKeyboardButton(text, callback_data=cb)]
            for text, cb in SUBCATEGORIES["menu_vbox"]
        ]
        await query.edit_message_text(
            "📂 VBOX",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return
    # ===== MENU =====
    if data == "menu_vmware":
        keyboard = [
            [InlineKeyboardButton(text, callback_data=cb)]
            for text, cb in SUBCATEGORIES["menu_vmware"]
        ]
        await query.edit_message_text(
            "📂 VMWARE",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return


    # ===== VBOX → PING =====
    if query.data == "vbox_ping":
        await run_vbox_ping(update, context)
        return

    # ===== VBOX → TRACEROUTE =====
    if query.data == "vbox_traceroute":
        await run_vbox_traceroute(update, context)
        return    

    # ===== VBOX → TRAFFIC =====
    if query.data == "vbox_traffic":
        await run_vbox_traffic(update, context)
        return

    # ===== VMWARE → PING =====
    if query.data == "vmware_ping":
        await run_vware_ping(update, context)
        return

    # ===== VMWARE → TRACEROUTE =====
    if query.data == "vmware_traceroute":
        await run_vmware_traceroute(update, context)
        return    

    # ===== VMWARE → TRAFFIC =====
    if query.data == "vmware":
        await run_vmware_traffic(update, context)
        return


    


# ======================
# CHAT COMMAND
# ======================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not update.message or not update.message.text:
        return

    chat = update.effective_chat
    chat_id = chat.id
    chat_type = chat.type
    thread_id = update.message.message_thread_id
    text = update.message.text.lower()

    # ===== FILTER GROUP + THREAD =====
    if chat_type in ["group", "supergroup"]:

        # group 1 harus di thread tertentu
        if chat_id == GROUP_ID_1 and thread_id == THREAD_ID_1:
            pass

        # group 2 bebas thread
        elif chat_id == GROUP_ID_2:
            pass

        else:
            await update.message.reply_text(
                "❌ Group / thread ini tidak diizinkan menggunakan bot."
            )
            return

        # wajib mention bot di group
        if BOT_USERNAME not in text:
            return
    # =========================
    # PRIVATE CHAT
    # =========================
    if chat_type == "private":

        if text == "help":
            await update.message.reply_text(
                HELP_TEXT,
                parse_mode="Markdown"
            )
            return

        # ===== VBOX =====
        if "internet vbox status" in text:
            await run_vbox_ping(update, context)
            return

        if "traceroute vbox" in text:
            await run_vbox_traceroute(update, context)
            return

        if "traffic monitor vbox" in text:
            await run_vbox_traffic(update, context)
            return

        # ===== VMWARE =====
        if "internet vmware status" in text:
            await run_vmware_ping(update, context)
            return

        if "traceroute vmware" in text:
            await run_vmware_traceroute(update, context)
            return

        if "traffic monitor vmware" in text:
            await run_vmware_traffic(update, context)
            return

        await update.message.reply_text(
            "Perintah tidak dikenali. Ketik `help`.",
            parse_mode="Markdown"
        )
        return

    # =========================
    # GROUP POLICY
    # =========================


    if "help" in text:
        await update.message.reply_text(
            HELP_TEXT,
            parse_mode="Markdown"
        )
        return

    if "internet vbox status" in text:
        await run_vbox_ping(update, context)
        return

    if "traceroute vbox" in text:
        await run_vbox_traceroute(update, context)
        return

    if "traffic monitor vbox" in text:
        await run_vbox_traffic(update, context)
        return

    if "internet vmware status" in text:
        await run_vmware_ping(update, context)
        return

    if "traceroute vmware" in text:
        await run_vmware_traceroute(update, context)
        return

    if "traffic monitor vmware" in text:
        await run_vmware_traffic(update, context)
        return

# ======================
# ERROR HANDLER
# ======================
async def error_handler(update, context):
    logging.error("ERROR:", exc_info=context.error)

# ======================
# MAIN
# ======================
if __name__ == "__main__":
    app = Application.builder().token(BOT_TOKEN).build()

    #app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_error_handler(error_handler)

    app.run_polling()

