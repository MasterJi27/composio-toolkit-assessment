import 'dotenv/config';
import { Composio } from "@composio/core";
import { VercelProvider } from "@composio/vercel";

// Setup Composio with the Vercel Provider exactly as requested
const composio = new Composio({ provider: new VercelProvider() });
const userId = "user_m723jp";

async function main() {
  console.log("Initializing Composio SDK...");
  try {
    // Create a tool router session
    const session = await composio.create(userId);
    const tools = await session.tools();
    
    console.log(`Successfully connected to Composio! Loaded ${Object.keys(tools).length} tools.`);
    console.log("You have completed the Composio Platform Setup!");
    
  } catch (error) {
    console.error("Error connecting to Composio:", error);
  }
}

main();
