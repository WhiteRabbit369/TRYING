import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# Configuration (We will set these in Railway environment variables later)
TELEGRAM_TOKEN = os.getenv("8340372053:AAHm5qLBna7AOBYqUhMb6NOf2cWi59kP8KM")
TELEGRAM_CHANNEL_ID = int(os.getenv("-1003419266237"))
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

async def forward_to_discord(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Check if the message is from our specific channel
    if update.channel_post and update.channel_post.chat_id == TELEGRAM_CHANNEL_ID:
        content = update.channel_post.text
        
        # Prepare the payload for Discord
        payload = {"content": content}
        
        # Send to Discord Webhook
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
        if response.status_code == 204:
            print("Message successfully forwarded to Discord!")
        else:
            print(f"Failed to send: {response.status_code}, {response.text}")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    
    # Listen for posts in channels
    channel_handler = MessageHandler(filters.ChatType.CHANNEL & filters.TEXT, forward_to_discord)
    app.add_handler(channel_handler)
    
    print("Bot is running...")
    app.run_polling()