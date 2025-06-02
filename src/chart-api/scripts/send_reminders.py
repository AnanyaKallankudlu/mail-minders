import os
import re
from datetime import datetime, timedelta, timezone
from postmarker.core import PostmarkClient
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()
# --- Config ---
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_ANON_KEY"]
POSTMARK_TOKEN = os.environ["POSTMARK_SERVER_TOKEN"]
SENDER_EMAIL = os.environ["FROM_EMAIL"]

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
postmark = PostmarkClient(server_token=POSTMARK_TOKEN)

# --- Frequency Parser ---
def parse_frequency(freq: str) -> timedelta:
    match = re.match(r"(\d+)([mhd])", freq)
    if not match:
        raise ValueError(f"Invalid frequency: {freq}")
    value, unit = match.groups()
    value = int(value)
    if unit == "m":
        return timedelta(minutes=value)
    elif unit == "h":
        return timedelta(hours=value)
    elif unit == "d":
        return timedelta(days=value)
    else:
        raise ValueError(f"Unknown unit in frequency: {freq}")


# --- Send Email ---
def send_reminder(to_email: str, task: str):
    print(f"Sending reminder for {task} to {to_email}")
    postmark.emails.send(
        From=SENDER_EMAIL,
        To=to_email,
        Subject=f"⏰ Reminder: {task}",
        HtmlBody=f"Hey! It’s time to do: {task}",
    )

def get_user_email(user_id):
    response = supabase.from_("users").select("email").eq("id", user_id).single().execute()
    return response.data['email'] if response.data else None

def update_last_reminded(task_id):
    now = datetime.now(timezone.utc)
    supabase.from_("tasks").update({"last_reminded_at": now.isoformat()}).eq("id", task_id).execute()

def fetch_due_tasks():
    """
    Fetch tasks where the current time exceeds the last reminded time + frequency.
    Frequency is stored as '<num>[m|h|d]'.
    """
    response = supabase.from_("tasks").select("id, user_id, task, frequency, created_at, last_reminded_at").execute()
    tasks = response.data if response.data else []

    now = datetime.now(timezone.utc)
    due_tasks = []

    for task in tasks:
        freq = task['frequency']
        created_at = task['created_at']
        last_reminded_at = task['last_reminded_at']

        if not freq:
            continue

        try:
            freq_delta = parse_frequency(freq)
            created_at = datetime.fromisoformat(created_at)
            last_reminded_at = datetime.fromisoformat(last_reminded_at) if last_reminded_at else None
            if last_reminded_at is None and now >= created_at + freq_delta:
                due_tasks.append(task)
            else:
                next_reminder_time = last_reminded_at + freq_delta
                if now >= next_reminder_time:
                    due_tasks.append(task)

        except Exception as e:
            print(f"Skipping invalid frequency '{freq}' for task {task['task']}: {e}")

    return due_tasks

# --- Main ---
def main():
    print("Running reminder check ")
    tasks = fetch_due_tasks()
    for task in tasks:
        user_email = get_user_email(task['user_id'])
        if user_email:
            send_reminder(user_email, task['task'])
            update_last_reminded(task['id'])

if __name__ == "__main__":
    main()