import sys
from pathlib import Path

# Add root directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import gradio as gr
import requests
import json
from typing import List, Dict, Any
from app.config import settings

# Your existing config
API_URL = "http://localhost:8000"
API_KEY = settings.API_KEY

# ============ CHAT INTERFACE ============

def query_bot(user_query: str, history: List[Dict[str, Any]]) -> tuple[str, List[Dict[str, Any]]]:
    """Query bot using messages format for Gradio 5.x compatibility"""
    try:
        response = requests.post(
            f"{API_URL}/api/v1/query",
            json={
                "query": user_query,
                "session_id": "gradio-session",
                "user_id": "gradio-user"
            },
            headers={"X-API-Key": API_KEY},
            timeout=30
        )
        
        if response.status_code != 200:
            error_msg = f"Error: {response.status_code}"
            history.append({"role": "user", "content": user_query})
            history.append({"role": "assistant", "content": error_msg})
            return "", history
        
        data = response.json()
        bot_response = data.get("response", "No response")
        history.append({"role": "user", "content": user_query})
        history.append({"role": "assistant", "content": bot_response})
        return "", history
        
    except Exception as e:
        history.append({"role": "user", "content": user_query})
        history.append({"role": "assistant", "content": f"Error: {str(e)}"})
        return "", history


# ============ DOCUMENT UPLOAD INTERFACE ============

def upload_document(file):
    """Upload document via API"""
    if file is None:
        return "No file selected"
    
    try:
        # Get file content
        with open(file.name, 'rb') as f:
            files = {'file': (file.name, f)}
            
            response = requests.post(
                f"{API_URL}/api/v1/documents/ingest-file",
                files=files,
                headers={"X-API-Key": API_KEY},
                timeout=60
            )
        
        if response.status_code == 200:
            data = response.json()
            return f"Document uploaded!\n\nID: {data.get('document_id')}\nChunks: {data.get('chunks_count', 'N/A')}"
        else:
            return f"Upload failed: {response.status_code}\n{response.text}"
            
    except Exception as e:
        return f"Error: {str(e)}"


# ============ GRADIO INTERFACE ============

with gr.Blocks(title="Dealer Bot") as demo:
    gr.Markdown("# 🤖 Dealer Bot")
    gr.Markdown("RAG-based Q&A system for dealer support")
    
    with gr.Tabs():
        # ========== TAB 1: CHAT ==========
        with gr.Tab("💬 Chat"):
            gr.Markdown("Ask questions about dealer services, maintenance, etc.")
            
            chatbot = gr.Chatbot(
                label="Conversation",
                height=300,
                show_label=True,
                type="messages"
            )
            
            with gr.Row():
                user_input = gr.Textbox(
                    label="Your Question",
                    placeholder="Type your question here...",
                    lines=1,
                    scale=4
                )
                submit_btn = gr.Button("Send", scale=1)

            gr.Markdown("### Example Questions")
            
            with gr.Row():
                q1_btn = gr.Button("Can I get service performed at my job site?", variant="secondary")
                q2_btn = gr.Button("Is emergency 24/7 service available?", variant="secondary")
                q3_btn = gr.Button("Can dealers run penetration tests?", variant="secondary")            

            # On submit
            submit_btn.click(
                fn=query_bot,
                inputs=[user_input, chatbot],
                outputs=[user_input, chatbot]
            )
            onEnter = user_input.submit(
                fn=query_bot,
                inputs=[user_input, chatbot],
                outputs=[user_input, chatbot]
            )
            # Example question buttons
            q1_btn.click(
                fn=lambda history: query_bot("Can I get service performed at my job site?", history),
                inputs=[chatbot],
                outputs=[user_input, chatbot]
            )
            
            q2_btn.click(
                fn=lambda history: query_bot("Is emergency 24/7 service available?", history),
                inputs=[chatbot],
                outputs=[user_input, chatbot]
            )
            
            q3_btn.click(
                fn=lambda history: query_bot("Can dealers run penetration tests?", history),
                inputs=[chatbot],
                outputs=[user_input, chatbot]
            )
        
        # ========== TAB 2: DOCUMENT UPLOAD (NEW!) ==========
        with gr.Tab("📄 Upload Documents"):
            with gr.Column():
                gr.Markdown("### Select a PDF file add to knowledge base:")
                
                file_input = gr.File(
                    label="Choose only 1 file",
                    file_count="single",
                    file_types=[".pdf"]
                )
                
                upload_btn = gr.Button("📤 Upload Document", variant="primary")
                
                output_text = gr.Textbox(
                    label="Upload Status",
                    lines=4,
                    interactive=False
                )
            
            # On upload
            upload_btn.click(
                fn=upload_document,
                inputs=file_input,
                outputs=output_text
            )
        
        # ========== TAB 3: INFO ==========
        with gr.Tab("ℹ️ About"):
            gr.Markdown("""
            ## Dealer Bot Features
            
            - **4 Intelligent Agents:**
              - Intent Classifier (understand user intent)
              - Anomaly Detection (security checks)
              - RAG Agent (search documents)
              - Response Synthesis (generate answers)
            
            - **Document Management:** Upload your knowledge base
            - **Semantic Search:** Find relevant information quickly
            - **Security:** Malicious query detection
            
            ## How to use:
            1. **Chat Tab:** Ask questions about dealers, warranty, maintenance
            2. **Upload Tab:** Add new documents to knowledge base

            """)


if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False
    )