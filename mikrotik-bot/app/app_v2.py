import os
import logging
import paramiko


from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    CallbackContext,
    CallbackQueryHandler,
    Updater,
)
from logging import (
    basicConfig,
    getLogger,
    INFO
)


from mikrotik_941 import *
from mikrotik_840 import *
from mikrotik_942 import *
from mikrotik_940 import *
from mikrotik_841 import *
from mikrotik_aws import *
from mikrotik_Lunox import *
from mikrotik_gatot import *

status_script = False 
router_name = None
script_name = None
waiting_for_add_script = False
waiting_for_remove_script = False
waiting_for_run_script = False
waiting_command = False
note = None
datetime_value = None

waiting_command = False
waiting_ip = None
current_command = None

router_set = {
     "router_840" : "x.x.x.x",
     "841_dc" : "x.x.x.x",
     "941_drc" : "x.x.x.x",
     "router940" : "x.x.x.x",
     "router942" : "x.x.x.x",
     "gatot" : "x.x.x.x",
     "lunox" : "x.x.x.x",
     "aws" : "x.x.x.x",
}

BOT_TOKEN = os.getenv("BOT_TOKEN")
BOT_USERNAME = os.getenv("BOT_NAME")
GROUP_ID_1 = os.getenv("BOT_GROUP_ID_1")
GROUP_ID_2 = os.getenv("BOT_GROUP_ID_2")
GROUP_ID_3 = os.getenv("BOT_GROUP_ID_3")
#BOT_THREAD_ID_1 = os.getenv("BOT_THREAD_ID_1")
BOT_THREAD_ID_2 = os.getenv("BOT_THREAD_ID_2")


#Define categories and their respective buttons#
CATEGORIES = {
    "Data Centar": ["DC", "DRC"],
    "Cloud" : ["AWS, Lunox, Gatot"]
}

#Sub-categories
SUBCATEGORIES = {

    "DC Sentul": [
        "interconnect_dc_stat", "Database_dc_status", "block_ip_public_dc",
        "show_block_ip_public_dc"
    ],
    "DRC Surabaya": [
        "interconnect_drc_stat", "Database_drc_status", "block_ip_public_drc",
        "show_block_ip_public_drc"
    ],
    "AWS": [
        "dc_cbn_status", "nginx_dc_status", "drc_cbn_status", "nginx_cbn_status"
    ]
}

# Enable Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
paramiko.common.logging.basicConfig(level=paramiko.common.DEBUG)

# Set Higher Logging Level for Httpx to Avoid All GET and POST Requests Being Logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

async def start_command(update: Update, context: CallbackContext):
    message_type = update.message.chat.type
    chat_id = update.message.chat_id
    text = update.message.text
    thread_id = update.message.message_thread_id

    if BOT_USERNAME in text and str(chat_id) == GROUP_ID_1 :
        keyboard = [
            [InlineKeyboardButton(category, callback_data=category)]
            for category in CATEGORIES.keys()
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Pilih kategori:", reply_markup=reply_markup)

    elif BOT_USERNAME in text and str(chat_id) == GROUP_ID_2:
        keyboard = [
            [InlineKeyboardButton(category, callback_data=category)]
            for category in CATEGORIES.keys()
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Pilih kategori:", reply_markup=reply_markup)

# Inline button handler
#Inline button handler with Back button
async def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()#

    query_data = query.data
    print(f"Callback data: {query_data}")

#    # Check if the callback data is a category
    if query_data in CATEGORIES:
        # Simpan kategori yang dipilih agar bisa kembali nanti
        context.user_data['last_category'] = query_data
        items = CATEGORIES[query_data]
        keyboard = [
            [InlineKeyboardButton(item.capitalize(), callback_data=item)] for item in items
        ]
#       # Add Back button to return to main categories
        keyboard.append([InlineKeyboardButton("Back", callback_data="main_menu")])
        reply_markup = InlineKeyboardMarkup(keyboard)#

        if query_data == "MITIGASI":
            try:
                function_to_call = globals().get(query_data)
                if callable(function_to_call):
                    result = function_to_call(router_set)
                    await query.edit_message_text(text=result)
                else:
                    await query.edit_message_text(text=f"Fungsi untuk {query_data} tidak ditemukan.")
            except Exception as e:
                await query.edit_message_text(text=f"Terjadi kesalahan: {str(e)}\n\n{result}")
        else:
            await query.edit_message_text(text=f"Kategori {query_data} dipilih. Pilih sub-kategori:", reply_markup=reply_markup)

    # Check if the callback data is a subcategory
    elif query_data in SUBCATEGORIES:
        # Simpan sub-kategori yang dipilih
        context.user_data['last_subcategory'] = query_data
        items = SUBCATEGORIES[query_data]
        keyboard = [
            [InlineKeyboardButton(item, callback_data=item)] for item in items
        ]
        # Add Back button to return to the previous category
        keyboard.append([InlineKeyboardButton("Back", callback_data="back_to_category")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text=f"Sub-kategori {query_data} dipilih. Pilih item:", reply_markup=reply_markup)

    # Handle going back to the main menu
    elif query_data == "main_menu":
        keyboard = [
            [InlineKeyboardButton(category, callback_data=category)]
            for category in CATEGORIES.keys()
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Pilih kategori:", reply_markup=reply_markup)

    # Handle going back to the previous category
    elif query_data == "back_to_category":
        # Ambil kategori terakhir yang disimpan sebelum masuk sub-kategori
        category = context.user_data.get("last_category")
        if category:
            items = CATEGORIES.get(category, [])
            keyboard = [
                [InlineKeyboardButton(item.capitalize(), callback_data=item)] for item in items
            ]
            # Add Back button to return to the main categories
            keyboard.append([InlineKeyboardButton("Back", callback_data="main_menu")])
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(text=f"Kategori {category} dipilih. Pilih sub-kategori:", reply_markup=reply_markup)
        else:
            await query.edit_message_text(text="Kategori tidak ditemukan, silakan kembali ke menu utama.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Back", callback_data="main_menu")]]))

    else:
        try:
            function_to_call = globals().get(query_data)
            if callable(function_to_call):
                result = function_to_call(router_set)
                await query.edit_message_text(text=result)
            else:
                await query.edit_message_text(text=f"Fungsi untuk {query_data} tidak ditemukan.")
        except Exception as e:
            await query.edit_message_text(text=f"Terjadi kesalahan: {str(e)}")

# Response Handling
def handle_response(text: str) -> str:
    processed = text.lower()

    global router_name, script_name, waiting_for_add_script, waiting_for_remove_script, status_script, waiting_for_run_script

    if "hay" in processed:
        return "Halo! Saya adalah Antony, bot yang selalu siap membantumu."

    if "hallo" in processed:
        return "Halo! Saya adalah Antony, bot yang selalu siap membantumu."

    if "apa kabar" in processed:
        return "Antony baik baik baik saja."

    if "kata kata hari ini" in processed: 
        return "Dingin tetapi tetap subuh"

    return "Antony tidak tau, coba tulis kembali"
    
# Response Handler Command
def handle_response_group(text: str, username: str) -> str:

    global waiting_command, waiting_ip, current_command

    processed_group = text.lower()


    if "tolong kaki saya sakit" in processed_group:
        return "kau diam ! "
    
    if "hay" in processed_group:
        return "Halo! Saya adalah Antony, bot yang selalu siap melawan kejahatan"


    if "help" in processed_group:
        c1 = "##################\n# HELP COMMANDS #\n##################\n" 

        c71 = "\n### DC 840 ###"
        c72 = "1. internet cbn dc status"
        c73 = "2. internet sigma dc status"
        c75 = "3. block ip public dc"
        c76 = "4. show block public dc"
        
        c77 = "\n### DC 841 ###"
        c78 = "1. dc interconnect stat"
        c80 = "2. Database dc status"


        c38 = "\n### 940 ###"
        c39 = "1. internet cbn drc status"
        c28 = "2. block ip public cbn drc"
        c82 = "3. show block public cbn drc"
        
        c22 = "\n### DRC 942 ###"
        c23 = "1. internet sigma drc status"
        c26 = "2. block ip public sigma drc "
        c27 = "3. show block public sigma drc"

        c44 = "\n### DRC 941  ###"
        c45 = "1. drc interconnect stat"
        c47 = "2. Database drc status"

        c52 = "\n### Router AWS ###"
        c53 = "1. aws dc cbn status"
        c54 = "2. aws nginx dc status"
        c55 = "3. aws drc cbn status"
        c65 = "4. aws nginx drc status"
        
        c60 = "\n### Router gatot ###"
        c61 = "1. gatot dc cbn status"
        c62 = "2. gatot nginx dc status"
        c63 = "3. gatot drc cbn status"
        c64 = "4. gatot nginx drc status"
        
        c66 = "\n### Router Lunox ###"
        c67 = "1. cloud dc cbn status"
        c68 = "2. cloud nginx dc status"
        c69 = "3. cloud cbn status"
        c70 = "4. cloud nginx drc status"

        
        return "\n".join([c71,c72,c73,c75,c76,c77,c78,c80,c38,c39,c28,c82,c22,c23,c26,c27,c44,c45,c47,c52,c53,c54,c55,c65,c60,c61,c62,c63,c64,c66,c67,c68,c69,c70])

#ROUTER-40-DC COMMAND################################################################################################################################################################################

        
    if 'internet cbn dc status' in processed_group:
        try:
            output = internet_cbn_dc_status(router_set)
            print(output)
            return output
        except Exception as e:
            return str(e)
        
    if 'internet sigma dc status' in processed_group:
        try:
            output = internet_sigma_dc_status(router_set)
            print(output)
            return output
        except Exception as e:
            return str(e)
    
    if 'block ip public dc' in processed_group and not waiting_command:
        try:
            waiting_command = True
            current_command = 'block_ip_public_dc'  # Set current command
            return "Please enter the IP address to block."
        
        except Exception as e:
            return str(e)

    # If we are waiting for the IP address, process it
    if waiting_command and current_command == 'block_ip_public_dc' and waiting_ip is None:
        waiting_ip = text  # Store the IP address
        try:

            output = block_ip_public_dc(router_set, waiting_ip)
            waiting_command = False  # Reset state after command execution
            waiting_ip = None  # Clear the IP after use
            current_command = None  # Clear current command
            return output
        except Exception as e:
            waiting_command = False  # Reset state in case of error
            waiting_ip = None
            current_command = None
            return str(e)

        
    # Message for Check Total User Connected
    if 'show block public dc' in processed_group:
        try:
            output = show_block_ip_public_dc(router_set)
            print(output)
            return output
        except Exception as e:
            return str(e)
  
#FW-DC COMMAND################################################################################################################################################################################
        
    if 'dc interconnect stat' in processed_group:
        try:
            output = interconnect_dc_status(router_set)
            print(output)
            return output
        except Exception as e:
            return str(e)
        

    if 'Database dc status' in processed_group:
        try:
            output = Database_dc_status(router_set)
            print(output)
            return output
        except Exception as e:
            return str(e) 
        
#ROUTER-40-DRC CBN COMMAND################################################################################################################################################################################

        
    if 'internet cbn drc status' in processed_group:
        try:
            output = internet_cbn_drc_status(router_set)
            print(output)
            return output
        except Exception as e:
            return str(e)
        
    
    if 'block ip public cbn drc' in processed_group and not waiting_command:
        try:
            # Set the state to waiting for IP input
            waiting_command = True
            current_command = 'block_ip_public_drc_40'  # Set current command
            return "Please enter the IP address to block."
        
        except Exception as e:
            return str(e)

    # If we are waiting for the IP address, process it
    if waiting_command and current_command == 'block_ip_public_drc_40' and waiting_ip is None:
        waiting_ip = text  # Store the IP address
        try:

            output = block_ip_public_drc_40(router_set, waiting_ip)
            waiting_command = False  # Reset state after command execution
            waiting_ip = None  # Clear the IP after use
            current_command = None  # Clear current command
            return output
        except Exception as e:
            waiting_command = False  # Reset state in case of error
            waiting_ip = None
            current_command = None
            return str(e)

        
    # Message for Check Total User Connected
    if 'show block public cbn drc' in processed_group:
        try:
            output = show_block_ip_public_drc_40(router_set)
            print(output)
            return output
        except Exception as e:
            return str(e)
        

#ROUTER-42-DRC 942 COMMAND################################################################################################################################################################################

        
    if 'internet 942 drc status' in processed_group:
        try:
            output = internet_942_drc_status(router_set)
            print(output)
            return output
        except Exception as e:
            return str(e)
        
    
    if 'block ip public 942 drc' in processed_group and not waiting_command:
        try:
            # Set the state to waiting for IP input
            waiting_command = True
            current_command = 'block_ip_public_drc_942'  # Set current command
            return "Please enter the IP address to block."
        
        except Exception as e:
            return str(e)

    # If we are waiting for the IP address, process it
    if waiting_command and current_command == 'block_ip_public_drc_942' and waiting_ip is None:
        waiting_ip = text  # Store the IP address
        try:

            output = block_ip_public_drc_942(router_set, waiting_ip)
            waiting_command = False  # Reset state after command execution
            waiting_ip = None  # Clear the IP after use
            current_command = None  # Clear current command
            return output
        except Exception as e:
            waiting_command = False  # Reset state in case of error
            waiting_ip = None
            current_command = None
            return str(e)

        
    # Message for Check Total User Connected
    if 'show block public 942 drc' in processed_group:
        try:
            output = show_block_ip_pubic_drc_942(router_set)
            print(output)
            return output
        except Exception as e:
            return str(e)

#FW-DRC COMMAND################################################################################################################################################################################

        
    if 'drc interconnect stat' in processed_group:
        try:
            output = interconnect_drc_status(router_set)
            print(output)
            return output
        except Exception as e:
            return str(e)

    if 'Database drc status' in processed_group:
        try:
            output = Database_drc_status(router_set)
            print(output)
            return output
        except Exception as e:
            return str(e)
       

#AWS COMMAND################################################################################################################################################################################

        
    if 'aws dc cbn status' in processed_group:
        try:
            output = dc_cbn_status(router_set)
            print(output)
            return output
        except Exception as e:
            return str(e)

    if 'aws nginx dc status' in processed_group:
        try:
            output = nginx_dc_status(router_set)
            print(output)
            return output
        except Exception as e:
            return str(e)

    if 'aws drc cbn status' in processed_group:
        try:
            output = drc_cbn_status(router_set)
            print(output)
            return output
        except Exception as e:
            return str(e)


    if 'aws nginx drc status' in processed_group:
        try:
            output = nginx_drc_status(router_set)
            print(output)
            return output
        except Exception as e:
            return str(e)
        

    

#gatot  COMMAND################################################################################################################################################################################

        
    if 'gatot dc cbn status' in processed_group:
        try:
            output = gatot_dc_cbn_status(router_set)
            print(output)
            return output
        except Exception as e:
            return str(e)

    if 'gatot nginx dc status' in processed_group:
        try:
            output = gatot_nginx_dc_status(router_set)
            print(output)
            return output
        except Exception as e:
            return str(e)

    if 'gatot drc cbn status' in processed_group:
        try:
            output =  gatot_drc_cbn_status(router_set)
            print(output)
            return output
        except Exception as e:
            return str(e)


    if 'gatot nginx drc status' in processed_group:
        try:
            output =  gatot_nginx_drc_status(router_set)
            print(output)
            return output
        except Exception as e:
            return str(e)
    
#lunox  COMMAND################################################################################################################################################################################

        
    if 'lunox dc cbn status' in processed_group:
        try:
            output = lunox_dc_cbn_status(router_set)
            print(output)
            return output
        except Exception as e:
            return str(e)

    if 'lunox nginx dc status' in processed_group:
        try:
            output = lunox_nginx_dc_status(router_set)
            print(output)
            return output
        except Exception as e:
            return str(e)

    if 'lunox drc cbn status' in processed_group:
        try:
            output =  lunox_drc_cbn_status(router_set)
            print(output)
            return output
        except Exception as e:
            return str(e)


    if 'lunox nginx drc status' in processed_group:
        try:
            output =  lunox_nginx_drc_status(router_set)
            print(output)
            return output
        except Exception as e:
            return str(e)
#############################################################################################################################################################################################

# Messages Handler
async def handle_message(update: Update, context):
    message_type = update.message.chat.type
    chat_id = update.message.chat_id
    text = update.message.text
    username = update.message.from_user.username
    thread_id = update.message.message_thread_id

    print(f'User ({update.message.chat.id}) in {message_type}: "{text}"')

    if BOT_USERNAME in text:
        await context.bot.send_chat_action(chat_id=chat_id, action="typing")

    # respon on group and private
    if message_type == "private":
        response = handle_response(text)

        if not response:
            return

        print("Bot:", response)
        await update.message.reply_text(response)

    else:
        if BOT_USERNAME in text and str(chat_id) == GROUP_ID_1 :
                        
            response_group = handle_response_group(text,username)

            if not response_group:
                return

            print("Bot:", response_group)
            await update.message.reply_text(response_group)

        elif BOT_USERNAME in text and str(chat_id) == GROUP_ID_2:
                        
            response_group = handle_response_group(text,username)

            if not response_group:
                return

            print("Bot:", response_group)
            await update.message.reply_text(response_group)

        elif BOT_USERNAME in text and str(chat_id) == GROUP_ID_3:
            response_group = handle_response_group(text,username)

            if not response_group:
                return

            print("Bot:", response_group)
            await update.message.reply_text(response_group)
            

        elif BOT_USERNAME in text:
            
            response_restricted_group = (
                "Maafkan NetBot. NetBot hanya merespon dari group tertentu ."
            )
            
            print("Bot:", response_restricted_group)
            await update.message.reply_text(response_restricted_group)

# Error Handler
async def error(update: Update, context):
    print(f"Update {update} caused error {context.error}")

if __name__ == "__main__":
    print("NetBot sudah bangun....")
    app = Application.builder().token(BOT_TOKEN).build()

#    app.add_handler(CommandHandler("start", start_command))
#    app.add_handler(CallbackQueryHandler(button))

    # Message Handler
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    # Error Handler
    app.add_error_handler(error)

    # Polling the bot
    print("NetBot memulai....")
    app.run_polling(poll_interval=3)
