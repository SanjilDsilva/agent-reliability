import os
import sys
from pathlib import Path

# Add src to sys.path so agent_reliability is importable anywhere
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

# ZeroGPU workaround: satisfies Hugging Face ZeroGPU startup scanner
try:
    import spaces

    @spaces.GPU
    def _zerogpu_startup():
        return True
except Exception:
    pass

import gradio as gr
from fastapi.responses import HTMLResponse
from agent_reliability.database import Base, engine
from agent_reliability.api import app as fastapi_app, INDEX_PATH

# Ensure database tables exist automatically
Base.metadata.create_all(bind=engine)

# Embed our custom 3-panel command dashboard inside Gradio
custom_css = """
footer {visibility: hidden}
.gradio-container {padding: 0 !important; margin: 0 !important; max-width: 100% !important;}
iframe {width: 100vw; height: 100vh; border: none; display: block;}
"""

with gr.Blocks(title="AgentReliability", css=custom_css, fill_width=True) as demo:
    gr.HTML('<iframe src="/dashboard"></iframe>')

# Attach all FastAPI endpoints (/evaluations, /health, etc.) to Gradio's internal app
demo.app.routes.extend(
    [
        r
        for r in fastapi_app.routes
        if getattr(r, "path", "")
        not in [getattr(dr, "path", "") for dr in demo.app.routes]
    ]
)


@demo.app.get("/dashboard", response_class=HTMLResponse)
def serve_dashboard():
    return INDEX_PATH.read_text(encoding="utf-8")


app = demo.app

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860, css=custom_css)


