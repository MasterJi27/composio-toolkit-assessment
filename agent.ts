import { google } from "@ai-sdk/google";
import { generateText } from "ai";
import { createComposioToolSet } from "@composio/core";

// Initialize Composio ToolSet
const composioToolSet = createComposioToolSet({
    apiKey: process.env.COMPOSIO_API_KEY,
});

async function main() {
    // Get GitHub tools from Composio
    const tools = await composioToolSet.getTools({ actions: ["github_star_a_repository_for_the_authenticated_user"] });

    console.log("Running agent with Gemini...");

    // Execute the agent
    const result = await generateText({
        model: google("gemini-2.5-pro"),
        prompt: "Star the composiohq/composio repo on GitHub",
        tools: tools,
        maxSteps: 5
    });

    console.log("\nAgent response:");
    console.log(result.text);
}

main().catch(console.error);
