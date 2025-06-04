# Mail-Minders

**Mail-Minders** is a fully email-based task reminder system. No apps, no dashboards—just your inbox. Manage your tasks, set reminders, and receive analyses, all by sending simple emails.

---

## Features

- **Add Tasks:** Email new tasks and set their frequency using simple commands.
- **List Tasks:** Request your current task list via email.
- **Analyze Tasks:** Get visual charts of your completed tasks delivered to your inbox. Go inside the src/chart-api directory to find code that does the analysis.
- **No Apps Needed:** Everything is managed through email—no need for extra apps or dashboards.

---

## How It Works

1. **Send an Email:** Use specific subjects and body formats to interact with Mail-Minders.
2. **Receive Responses:** The system replies with confirmations, lists, or analyses as requested.

### Supported Commands

| Subject | Action                                                  |
| ------- | ------------------------------------------------------- |
| START   | Sends a welcome email                                   |
| LIST    | Sends your current task list                            |
| ANALYZE | Sends analysis charts of your tasks                     |
| ADD     | Parses the email body to add, complete, or update tasks |

#### Example: Adding Tasks

Send an email with:

- **Subject:** `ADD`
- **Body:**
  ```
  ➕ Walk the dog 1d
  ➕ Read book 2h
  ```

#### Example: Completing or Updating Tasks

- `✅ Buy groceries 3d` — Mark as completed (removes the task)
- `❌ Read book 2h` — Update the frequency of a task

---

## API

The main API endpoint is a Next.js route at `/api/postmark-webhook`. It receives POST requests from Postmark (or any email provider webhook) and processes commands as described above.

### Example cURL Request

```bash
curl -X POST http://localhost:3000/api/postmark-webhook \
  -H "Content-Type: application/json" \
  -d '{
    "From": "user@example.com",
    "Subject": "ADD",
    "TextBody": "➕ Walk the dog 1d\n➕ Read book 2h"
  }'
```

---

## Setup

1. **Clone the repository:**

   ```bash
   git clone https://github.com/AnanyaKallankudlu/mail-minders.git
   cd mail-minders
   ```

2. **Install dependencies:**

   ```bash
   pnpm install
   ```

3. **Configure environment variables:**
   - Set up the following environment variables in `.env.local`:

```shell
SUPABASE_ANON_KEY=abcd
SUPABASE_URL=https://abcd.supabase.co
POSTMARK_SERVER_TOKEN=abcd
POSTMARK_TOKEN=abcd
FROM_EMAIL=<postmark-configured-email-address>
ANALYSIS_SERVER=https://abcd
```

4. **Run the development server:**
   ```bash
   pnpm dev
   ```

---

## Database Schema

- **users**: Stores user emails

```sql
create table users (
  id uuid primary key default uuid_generate_v4(),
  email text unique not null,
  created_at timestamptz default now()
);
```

- **tasks**: Stores tasks, their frequency, and user association.

```sql
create table public.tasks (
  id uuid not null default extensions.uuid_generate_v4 (),
  user_id uuid not null,
  task text not null,
  category text not null,
  frequency text not null,
  created_at timestamp with time zone null default now(),
  last_reminded_at timestamp with time zone null,
  completed_at timestamp with time zone null,
  constraint tasks_pkey primary key (id),
  constraint tasks_user_id_task_unique unique (user_id, task),
  constraint unique_user_task unique (user_id, task),
  constraint tasks_user_id_fkey foreign KEY (user_id) references users (id)
)
```

Ensure your Supabase tables have the correct columns and unique constraints (e.g., unique on `user_id, task` for tasks).

---

## Contributing

Contributions are welcome! Please open issues or submit pull requests for improvements.

---
