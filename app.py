import html
import os
import sys
from pathlib import Path

# Disable Gradio SSR Node.js reverse proxy so Python serves all API routes directly
os.environ["GRADIO_SSR_MODE"] = "False"

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
from agent_reliability.database import Base, engine
from agent_reliability.api import app as fastapi_app, INDEX_PATH

# Ensure database tables exist automatically
Base.metadata.create_all(bind=engine)

# Prepare 3-panel command dashboard
raw_html = INDEX_PATH.read_text(encoding="utf-8")
escaped_html = html.escape(raw_html)

custom_css = """
footer { display: none !important; }
.gradio-container { max-width: 100% !important; margin: 0 !important; padding: 0 !important; }
iframe { width: 100%; height: 98vh; border: none; display: block; }
"""

with gr.Blocks(title="AgentReliability", fill_width=True) as demo:
    gr.HTML(
        f'<iframe srcdoc="{escaped_html}" style="width: 100%; height: 98vh; border: none;"></iframe>'
    )

# Prepend all REST API endpoints (/evaluations, /health, etc.) so they take priority
api_routes = [r for r in fastapi_app.routes if getattr(r, "path", "") != "/"]
demo.app.router.routes = api_routes + demo.app.router.routes

app = demo.app

if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        css=custom_css,
        _app=demo.app,
        ssr_mode=False,
    )


