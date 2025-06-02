import random
import json
import os
from datetime import datetime, timedelta
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()
# Initialize Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

user_id = os.getenv("USER_ID")
categories = ["payments", "work", "health", "personal", "family"]
frequencies = ["m", "h", "d"]

# Load tasks from tasks.json
with open("tasks.json", "r", encoding="utf-8") as f:
    all_tasks = json.load(f)

def random_datetime_within_last_week():
    now = datetime.now()
    days_ago = random.randint(0, 6)
    hours_ago = random.randint(0, 23)
    minutes_ago = random.randint(0, 59)
    dt = now - timedelta(days=days_ago, hours=hours_ago, minutes=minutes_ago)
    return dt

def insert_random_tasks():
    for category in categories:
        available_tasks = all_tasks[category]
        num = random.randint(1, 10)
        chosen_tasks = random.sample(available_tasks, k=min(num, len(available_tasks)))
        remaining_tasks = [task for task in available_tasks if task not in chosen_tasks]
        insert_task_to_db(chosen_tasks, category, True)
        insert_task_to_db(remaining_tasks, category)


def insert_task_to_db(tasks, category, completed = False):
    try:
        for task_text in tasks:
            num = random.randint(1, 10)
            frequency_str = random.choice(frequencies)
            frequency = f"{num}{frequency_str}"
            created_at = random_datetime_within_last_week()
            last_reminded_at = created_at + timedelta(hours=random.randint(1, 48))
            completed_at = (last_reminded_at +
                            timedelta(hours=random.randint(1, 48))) if completed else None

            task_data = {
                "user_id": user_id,
                "task": task_text,
                "category": category,
                "frequency": frequency,
                "created_at": created_at.isoformat(),
                "last_reminded_at": last_reminded_at.isoformat(),
                "completed_at": completed_at.isoformat() if completed else None,
            }

            res = supabase.table("tasks").insert(task_data).execute()
    except Exception as e:
        print("Error occurred:", str(e))

if __name__ == "__main__":
    insert_random_tasks()
