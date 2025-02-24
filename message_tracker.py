from datetime import datetime

# In-memory message counter (chat_id -> user_id -> timestamp_list)
message_counts = {}

def track_message(chat_id, user_id):
    timestamp = datetime.now()
    if chat_id not in message_counts:
        message_counts[chat_id] = {}
    if user_id not in message_counts[chat_id]:
        message_counts[chat_id][user_id] = []
    message_counts[chat_id][user_id].append(timestamp)

def get_message_counts(chat_id):
    return message_counts.get(chat_id, {})