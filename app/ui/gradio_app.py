"""
Simple Gradio UI for Dealer Bot
Minimal dependencies - no oauth issues
"""

import gradio as gr
import requests
import os

API_URL = os.getenv("API_URL", "http://localhost:8000")
API_KEY = os.getenv("API_KEY", "default-dev-key")


def chat(user_message, history):
    """Query the bot and return response"""
    try:
        response = requests.post(
            f"{API_URL}/api/v1/query",
            json={"query": user_message},
            headers={"X-API-Key": API_KEY},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            bot_response = data.get("response", "No response")
            
            # Add sources if available
            sources = data.get("sources", [])
            if sources:
                bot_response += "\n\n**Sources:**"
                for i, source in enumerate(sources[:3], 1):
                    doc = source.get("document", "")[:200]
                    score = source.get("similarity_score", 0)
                    bot_response += f"\n{i}. [{score:.2f}] {doc}..."
        else:
            bot_response = f"Error: {response.status_code}"
    except Exception as e:
        bot_response = f"Error: {str(e)}"
    
    return bot_response


# Create simple chat interface
demo = gr.ChatInterface(
    chat,
    examples=[
        "What is maintenance?",
        "My account is flagged for fraud",
        "How do I troubleshoot an error?",
        "What's covered under warranty?"
    ],
    title="🤖 Dealer Bot",
    description="Ask questions about products, maintenance, warranty, and more!",
)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)