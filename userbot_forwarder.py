import json
import re
from os import getenv
from dotenv import load_dotenv
from pyrogram import Client, filters
from pyrogram.types import Message

load_dotenv(".env")

API_ID = int(getenv("API_ID", 0))
API_HASH = getenv("API_HASH", "")
REMOVE_TAG = getenv("REMOVE_TAG", "True") in {"true", "True", 1}

with open("chat_list.json", "r") as f:
    CONFIG = json.load(f)


def parse_chat_id(chat) -> tuple[int, int | None]:
    """Returns (chat_id, topic_id)"""
    if isinstance(chat, str) and "#" in chat:
        parts = chat.split("#")
        return int(parts[0]), int(parts[1])
    return int(chat), None


def predicate_text(words: list, text: str) -> bool:
    for word in words:
        pattern = r"( |^|[^\w])" + re.escape(word) + r"( |$|[^\w])"
        if re.search(pattern, text or "", re.IGNORECASE):
            return True
    return False


# source chat IDs list banao handler ke liye
source_ids = [parse_chat_id(c["source"])[0] for c in CONFIG]

app = Client("userbot_session", api_id=API_ID, api_hash=API_HASH)


@app.on_message(filters.chat(source_ids))
async def forward_message(client: Client, message: Message):
    source_id = message.chat.id
    topic_id = message.message_thread_id

    for config in CONFIG:
        src_id, src_topic = parse_chat_id(config["source"])

        if src_id != source_id:
            continue
        if src_topic != topic_id:
            continue

        text = message.text or message.caption or ""

        if config.get("filters"):
            if not predicate_text(config["filters"], text):
                continue
        if config.get("blacklist"):
            if predicate_text(config["blacklist"], text):
                continue

        for dest in config["destination"]:
            dest_id, dest_topic = parse_chat_id(dest)
            try:
                if REMOVE_TAG:
                    await message.copy(dest_id, message_thread_id=dest_topic)
                else:
                    await message.forward(dest_id, message_thread_id=dest_topic)
                print(f"✅ Forwarded: {source_id} → {dest_id}")
            except Exception as e:
                print(f"❌ Failed {source_id} → {dest_id}: {e}")


print("🚀 Userbot starting...")
app.run()
