import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# Config from Environment Variables
# Configuration (We will set these in Railway environment variables later)
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHANNEL_ID = int(os.getenv("TELEGRAM_CHANNEL_ID"))
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL_1")
DISCORD_WEBHOOK_URL_2 = os.getenv("DISCORD_WEBHOOK_URL_2")
async def handle_channel_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Add this line right at the start of the function:
    print(f"New post detected in channel: {update.channel_post.chat_id}")
    
    if not update.channel_post or update.channel_post.chat_id != TELEGRAM_CHANNEL_ID:
        return

    post = update.channel_post
    caption = post.caption if post.caption else (post.text if post.text else "")
    
    file_to_send = None
    file_name = "file"

    # Identify Media Type
    if post.photo:
        # Get the highest resolution photo
        file_to_send = await post.photo[-1].get_file()
        file_name = "image.jpg"
    elif post.video:
        file_to_send = await post.video.get_file()
        file_name = "video.mp4"

    if file_to_send:
        # Download file to memory/temporary storage
        file_path = await file_to_send.download_to_drive()
        
        # Send to Discord as a file
        with open(file_path, 'rb') as f:
            files = {'file': (file_name, f)}
            payload = {"content": caption}
            response = requests.post(DISCORD_WEBHOOK_URL, data=payload, files=files)

            with open(file_path, 'rb') as f:
            files = {'file': (file_name, f)}
            response2 = requests.post(DISCORD_WEBHOOK_URL_2, data=payload, files=files)

            print(f"Server 1 Status: {response.status_code}")
            print(f"Server 2 Status: {response2.status_code}")
        
        # Clean up: Remove the downloaded file after sending
        os.remove(file_path)
    else:
        # Just text
        payload = {"content": caption}
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
        response2 = requests.post(DISCORD_WEBHOOK_URL_2, json=payload)

        print(f"Server 1 Status: {response.status_code}")
        print(f"Server 2 Status: {response2.status_code}")


if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    
    # Listen for text, photos, and videos
    app.add_handler(MessageHandler(filters.ChatType.CHANNEL & (filters.TEXT | filters.PHOTO | filters.VIDEO), handle_channel_post))
    
    print("Bot is monitoring media and text...")
    app.run_polling()

    try:
        with open(file_path, "rb") as f:
            response = requests.post(
                DISCORD_WEBHOOK_URL_1,
                data={"content": caption},
                files={"file": (file_name, f)}
            )
        print("Server 1:", response.status_code)
    except Exception as e:
        print("Server 1 error:", e)

    try:
        with open(file_path, "rb") as f:
            response = requests.post(
                DISCORD_WEBHOOK_URL_2,
                data={"content": caption},
                files={"file": (file_name, f)}
            )
        print("Server 2:", response.status_code)
    except Exception as e:
        print("Server 2 error:", e)

    os.remove(file_path)

else:
    try:
        response = requests.post(
            DISCORD_WEBHOOK_URL_1,
            json={"content": caption}
        )
        print("Server 1:", response.status_code)
    except Exception as e:
        print("Server 1 error:", e)

    try:
        response = requests.post(
            DISCORD_WEBHOOK_URL_2,
            json={"content": caption}
        )
        print("Server 2:", response.status_code)
    except Exception as e:
        print("Server 2 error:", e)

app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

app.add_handler(
MessageHandler(
filters.ChatType.CHANNEL
& (filters.TEXT | filters.PHOTO | filters.VIDEO),
handle_channel_post
)
)

print("Bot is running...")
print("Forwarding to two Discord servers...")

app.run_polling()
