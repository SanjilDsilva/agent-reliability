import os
import sys
from pathlib import Path

# Add src to sys.path so agent_reliability is importable anywhere
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

import gradio as gr
from agent_reliability.database import Base, engine
from agent_reliability.api import app as fastapi_app

# Ensure database tables exist automatically
Base.metadata.create_all(bind=engine)

# Mount our custom 3-panel dashboard on root, and Gradio on /gradio
with gr.Blocks(title="AgentReliability") as demo:
    gr.Markdown("# 🛡️ AgentReliability Evaluation Harness")
    gr.Markdown(
        "Welcome! The interactive 3-panel dashboard is running at the root URL: [Open Dashboard](/) \n\n"
        "REST API is available at `/evaluations` and interactive OpenAPI docs at `/docs`."
    )

app = gr.mount_gradio_app(fastapi_app, demo, path="/gradio")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 7860))
    uvicorn.run(app, host="0.0.0.0", port=port)

