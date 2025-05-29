import type { NextApiRequest, NextApiResponse } from "next";
import { supabase } from "@/lib/supabase";
import { sendTemplateEmail } from "@/lib/postmark";

// Regex patterns
const TASK_LINE_REGEX = /^([➕✅❌])\s+(.*?)\s+(\d+[hd])$/gm;

export default async function handleTaskList(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== "POST") {
    return res.status(405).json({ error: "Method not allowed" });
  }
  try {
    const payload = await req.body;

    const fromEmail = payload.From;
    const subject = payload.Subject?.trim().toUpperCase();
    const body = payload.TextBody?.trim() || "";

    // Ensure user exists
    const { data: user, error: userError } = await supabase
      .from("users")
      .select("*")
      .eq("email", fromEmail)
      .single();

    if (userError) {
      console.error("Supabase error fetching user:", userError);
    }
    let userId: string;
    if (!user) {
      const { data: newUser, error: insertError } = await supabase
        .from("user")
        .insert({ email: fromEmail })
        .select()
        .single();

      if (insertError) {
        console.error("Supabase error inserting user:", insertError);
      }

      userId = newUser.id;
    } else {
      userId = user.id;
    }

    // Handle commands
    if (subject === "START") {
      await sendTemplateEmail(fromEmail, 40220172, {}); // START template
      console.log("Welcome email sent");
    }

    if (subject === "LIST") {
      const { data: tasks } = await supabase
        .from("tasks")
        .select("task, frequency")
        .eq("user_id", userId);

      await sendTemplateEmail(fromEmail, 40219047, {
        tasks,
      });

      console.log("Task list sent");
    }

    // Parse task updates in body
    const updates = [...body.matchAll(TASK_LINE_REGEX)];

    for (const match of updates) {
      const symbol = match[1];
      const task = match[2].trim();
      const frequency = match[3].trim();

      if (symbol === "➕") {
        await supabase.from("tasks").upsert(
          {
            user_id: userId,
            task,
            frequency,
          },
          { onConflict: "user_id,task" }
        );
      }

      if (symbol === "✅") {
        const { error: deleteError } = await supabase
          .from("tasks")
          .delete()
          .eq("user_id", userId)
          .eq("task", task);

        if (deleteError) {
          console.error(`Error deleting task '${task}':`, deleteError);
        }
      }

      if (symbol === "❌") {
        const { error: updateError } = await supabase
          .from("task")
          .update({ frequency })
          .eq("user_id", userId)
          .eq("task", task);

        if (updateError) {
          console.error(`Error updating task '${task}':`, updateError);
        }
      }
    }
    res.status(200).json({ message: "Reminders processed successfully" });
  } catch (error) {
    console.error("Webhook error:", error);
    res.status(500).json({ error: "Internal Server Error" });
  }
}
