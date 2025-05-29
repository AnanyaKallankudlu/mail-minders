import { Client } from "postmark";
import dotenv from "dotenv";
dotenv.config();

export const postmark = new Client(process.env.POSTMARK_SERVER_TOKEN!);

export async function sendTemplateEmail(
  to: string,
  templateAliasOrId: string | number,
  templateModel: Record<string, any>
) {
  return await postmark.sendEmailWithTemplate({
    From: process.env.FROM_EMAIL!,
    To: to,
    TemplateAlias:
      typeof templateAliasOrId === "string" ? templateAliasOrId : undefined,
    TemplateId:
      typeof templateAliasOrId === "number" ? templateAliasOrId : undefined,
    TemplateModel: templateModel,
  });
}
