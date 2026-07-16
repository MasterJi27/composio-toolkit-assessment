// agent.ts — Vercel AI SDK + Composio

import { google } from "@ai-sdk/google";
import { Composio } from "@composio/core";
import { VercelProvider } from "@composio/vercel";
import { stepCountIs, streamText } from "ai";
import * as dotenv from "dotenv";

dotenv.config();

async function main() {
  // Initialize Composio with the VercelProvider (matching the tutorial)
  const composio = new Composio({ 
    provider: new VercelProvider(),
    apiKey: process.env.COMPOSIO_API_KEY
  });
  
  const userId = "user_z8lchl";

  // Create a tool router session
  const session = await composio.create(userId);
  const tools = await session.tools();

  console.log("Running agent with Gemini and Composio Tool Router...");

  const stream = await streamText({
    model: google("gemini-1.5-pro"), // Using Gemini since you have the Gemini API key
    prompt: "Star the composiohq/composio repo on GitHub",
    stopWhen: stepCountIs(10),
    tools,
  });

  for await (const textPart of stream.textStream) {
    process.stdout.write(textPart);
  }
}

main().catch(console.error);
