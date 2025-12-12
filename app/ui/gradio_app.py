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

# Check Gradio version for compatibility
# HuggingFace uses older Gradio without 'type' parameter support
import os
try:
    version_parts = gr.__version__.split('.')
    GRADIO_VERSION = (int(version_parts[0]), int(version_parts[1]))
    SUPPORTS_TYPE_PARAM = GRADIO_VERSION >= (5, 0) and not os.getenv("SPACE_ID")
    print(f"Gradio version: {gr.__version__}, SUPPORTS_TYPE_PARAM: {SUPPORTS_TYPE_PARAM}")
except Exception as e:
    print(f"Version detection failed: {e}")
    SUPPORTS_TYPE_PARAM = False

# ============ CHAT INTERFACE ============

def format_quality_metrics(metrics: Dict[str, Any]) -> str:
    """Format quality metrics for display"""
    if not metrics:
        return ""
    
    # Get metric values
    groundedness = metrics.get('groundedness', 0.0)
    answer_rel = metrics.get('answer_relevance', 0.0)
    context_rel = metrics.get('context_relevance', 0.0)
    faithfulness = metrics.get('faithfulness', 0.0)
    formatting = metrics.get('formatting', 0.0)
    overall = metrics.get('overall_quality', 0.0)
    
    # Create visual bars
    def make_bar(score: float) -> str:
        filled = int(score * 10)
        bar = "█" * filled + "░" * (10 - filled)
        return bar
    
    # Color based on overall quality
    if overall >= 0.8:
        emoji = "✅"
        quality_text = "Excellent"
    elif overall >= 0.6:
        emoji = "👍"
        quality_text = "Good"
    elif overall >= 0.4:
        emoji = "⚠️"
        quality_text = "Fair"
    else:
        emoji = "❌"
        quality_text = "Low"
    
    return f"""📊 **Response Quality Metrics** {emoji} **{quality_text}** (Overall: {overall:.2f})

**Groundedness** {groundedness:.2f} {make_bar(groundedness)} 
*No hallucinations* 

 **Answer Relevance** {answer_rel:.2f} {make_bar(answer_rel)} 
 *Addresses your question*

**Context Relevance** {context_rel:.2f} {make_bar(context_rel)} 
*Retrieved docs match query* 

**Faithfulness** {faithfulness:.2f} {make_bar(faithfulness)} 
*Accurate to source material*

**Formatting** {formatting:.2f} {make_bar(formatting)} 
*Professional structure*
"""


def query_bot(user_query: str, history: List[Dict[str, Any]]):
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
            return "", history, gr.update(value="", visible=True)
        
        data = response.json()
        bot_response = data.get("response", "No response")
        quality_metrics = data.get("quality_metrics", {})
        
        # Format quality metrics for display
        metrics_display = format_quality_metrics(quality_metrics)
        
        history.append({"role": "user", "content": user_query})
        history.append({"role": "assistant", "content": bot_response})
        
        return "", history, gr.update(value=metrics_display, visible=True)
        
    except Exception as e:
        history.append({"role": "user", "content": user_query})
        history.append({"role": "assistant", "content": f"Error: {str(e)}"})
        return "", history, gr.update(value=f"Error: {str(e)}", visible=True)


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
            
            # Left column: Chat interface
            with gr.Column():
                # Create chatbot - try with type parameter first, fallback without it
                try:
                    chatbot = gr.Chatbot(
                        label="Conversation",
                        height=400,
                        show_label=True,
                        type="messages"
                    )
                except TypeError:
                    # Older Gradio versions don't support 'type' parameter
                    chatbot = gr.Chatbot(
                        label="Conversation",
                        height=400,
                        show_label=True
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
                    q4_btn = gr.Button("My account is flagged for fraud, what is going on?", variant="secondary")
                
                # Quality metrics (shown after question)
                quality_display = gr.Markdown(
                    label="Response Quality",
                    value="📊 **Response Quality Metrics**\n\nMetrics will appear here after you ask a question.",
                    visible=False
                )            

            # On submit
            submit_btn.click(
                fn=query_bot,
                inputs=[user_input, chatbot],
                outputs=[user_input, chatbot, quality_display]
            )
            onEnter = user_input.submit(
                fn=query_bot,
                inputs=[user_input, chatbot],
                outputs=[user_input, chatbot, quality_display]
            )
            # Example question buttons
            q1_btn.click(
                fn=lambda history: query_bot("Can I get service performed at my job site?", history),
                inputs=[chatbot],
                outputs=[user_input, chatbot, quality_display]
            )
            
            q2_btn.click(
                fn=lambda history: query_bot("Is emergency 24/7 service available?", history),
                inputs=[chatbot],
                outputs=[user_input, chatbot, quality_display]
            )
            
            q3_btn.click(
                fn=lambda history: query_bot("Can dealers run penetration tests?", history),
                inputs=[chatbot],
                outputs=[user_input, chatbot, quality_display]
            )

            q4_btn.click(
                fn=lambda history: query_bot("My account is flagged for fraud, what is going on?", history),
                inputs=[chatbot],
                outputs=[user_input, chatbot, quality_display]
            )
        
        # ========== TAB 2: DOCUMENT UPLOAD (NEW!) ==========
        # with gr.Tab("📄 Upload Documents"):
        #     with gr.Column():
        #         gr.Markdown("### Select a PDF file add to knowledge base:")
                
        #         file_input = gr.File(
        #             label="Choose only 1 file",
        #             file_count="single",
        #             file_types=[".pdf"]
        #         )
                
        #         upload_btn = gr.Button("📤 Upload Document", variant="primary")
                
        #         output_text = gr.Textbox(
        #             label="Upload Status",
        #             lines=4,
        #             interactive=False
        #         )
            
        #     # On upload
        #     upload_btn.click(
        #         fn=upload_document,
        #         inputs=file_input,
        #         outputs=output_text
        #     )
        
        # ========== TAB 3: INFO ==========
        with gr.Tab("ℹ️ About"):
            gr.Markdown("""
            ## Dealer Bot Features
            
            - **4 Intelligent Agents:**
              - Intent Classifier (understand user intent)
              - Anomaly Detection (security checks)
              - RAG Agent (search documents)
              - Response Synthesis (generate answers)
            
            - **Semantic Search:** Find relevant information quickly
            - **Security:** Malicious query detection
            
            ## How to use:
            **Chat Tab:** Ask questions about dealers, warranty, maintenance
            
            ---
            
            ## Tech Stack
            
            ### Backend
            - **Framework:** FastAPI (REST API)
            - **Server:** Uvicorn (ASGI)
            - **Language:** Python 3.11
            
            ### AI/ML
            - **LLM:** OpenAI GPT-3.5-turbo
            - **Orchestration:** LangChain, LangGraph
            - **Embeddings:** 
              - SentenceTransformer (all-MiniLM-L6-v2) for semantic similarity
              - OpenAI text-embedding-3-small for RAG
            
            ### LLM Calls (2 per query)
            
            **1. Intent Classification (Conditional)**
            - **Model:** GPT-3.5-turbo
            - **When:** Only when rules-based confidence < 0.8
            - **Parameters:**
              - Temperature: 0.3 (deterministic)
              - Max Tokens: 100
              - Timeout: 30s
            - **Purpose:** Verify/refine intent classification
            
            **2. Response Synthesis (Always)**
            - **Model:** GPT-3.5-turbo
            - **Parameters:**
              - Temperature: 0.3 (consistent responses)
              - Max Tokens: 1000
              - Timeout: 30s
            - **Purpose:** Generate final response with context
            
            ### Vector Database
            - **Database:** ChromaDB 1.3.6 (PersistentClient)
            - **Storage:** Local persistent storage at `data/vectors/`
            
            ### NLP & Evaluation
            - **Metrics:** NLTK (BLEU, ROUGE scores)
            - **Quality Metrics:** 5 real-time metrics with semantic similarity scaling
              - Groundedness, Answer Relevance, Context Relevance, Faithfulness, Formatting
            
            ### Frontend
            - **UI Framework:** Gradio 5.x
            - **Interface:** Chat with real-time quality metrics display
            
            ### Deployment
            - **Local:** Python venv with Windows startup scripts
            - **Cloud:** HuggingFace Spaces (Docker, ephemeral storage)


            """)


if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False
    )