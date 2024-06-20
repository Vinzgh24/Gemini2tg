import pathlib
import textwrap
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters, CallbackContext
import google.generativeai as genai
import json
import os
import logging
import PIL.Image
from io import BytesIO
def to_markdown(text):
  text = text.replace('•', '  *')
  return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))
# Used to securely store your API key

with open("config.json") as config_file:
    config = json.load(config_file)
    google_api_key = config.get("GOOGLE_API_KEY")
    telegram_api_key = config.get("TELEGRAM_API_KEY")
if google_api_key is None or telegram_api_key is None:
    raise ValueError("One or all API keys are not found in config file.")

os.environ["GOOGLE_API_KEY"] = google_api_key
os.environ["TELEGRAM_API_KEY"] = telegram_api_key

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
google_api_key=os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=google_api_key)
model = genai.GenerativeModel('gemini-pro')
#modelone = genai.GenerativeModel('gemini-pro-vision')

AUTHORIZED_CHAT_TOPIC = "-1002086404082:4316"  # replace with your actual group and topic

chat = None

def extract_chat_topic(update: Update) -> str:
    chat_id = update.message.chat_id
    message_thread_id = update.message.message_thread_id
    # Create a combined chat_id:topic_id string
    combined_id = f"{chat_id}:{message_thread_id}" if message_thread_id else f"{chat_id}"
    return combined_id

def is_authorized(update: Update) -> bool:
    combined_id = extract_chat_topic(update)
    # Check if the combined ID matches the authorized chat and topic combination
    return combined_id == AUTHORIZED_CHAT_TOPIC

def handle_photo(update: Update, context: CallbackContext):
    # Example function to handle photos, adding for completeness
    if not is_authorized(update):
        update.message.reply_text("You are not authorized to use this bot in this chat.")
        return
    # Handle the photo message
    update.message.reply_text("Received a photo!")
  
#chat = model.start_chat(history=[])
global chat
    
def start(update, context):
    global chat
    if not is_authorized(update):
        update.message.reply_text("You are not authorized to use this bot in this chat.")
        return
      
    update.message.reply_text("Hello! I am your chatbot. Send me a message to start.")
    chat = model.start_chat(history=[])
  
def handle_message(update: Update, context: CallbackContext):
    global chat
    if not is_authorized(update):
        update.message.reply_text("You are not authorized to use this bot in this chat.")
        return

    user_message = update.message.text
    if chat is None:
        chat = model.start_chat(history=[])
    else:
        print(chat.history)
    response = chat.send_message(user_message)
    response_text = response.text if hasattr(response, 'text') else "Sorry, I couldn't process your request."

    update.message.reply_text(response_text)
def handle_photo(update: Update, context: CallbackContext):
    photo = update.message.photo[-1]
    file = context.bot.get_file(photo.file_id)
    file.download('photo.jpg')
    img = PIL.Image.open('photo.jpg')

    user_message = update.message.caption or "What's in the picture? Watch carefully and describe all details."

    vision_model = genai.GenerativeModel('gemini-pro-vision')

    response = vision_model.generate_content([user_message, img], stream=False)
    response.resolve()

    # Send response back to user
    update.message.reply_text(textwrap.indent(response.text, '> '))
def main():
    TOKEN = os.getenv("TELEGRAM_API_KEY")
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    # Add handler for photo messages first
    dp.add_handler(MessageHandler(Filters.photo, handle_photo))
    # Add handler for text messages

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
