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

demo = gr.Blocks(title="AgentReliability")

# Remove Gradio's internal root template handler which causes a blank page without components
demo.app.router.routes = [
    r for r in demo.app.router.routes if getattr(r, "path", "") != "/"
]

# Serve our 3-panel command dashboard directly on the root URL '/'
@demo.app.get("/", response_class=HTMLResponse)
def serve_dashboard():
    return INDEX_PATH.read_text(encoding="utf-8")


# Attach all FastAPI endpoints (/evaluations, /health, etc.)
for route in fastapi_app.routes:
    if getattr(route, "path", "") not in [getattr(dr, "path", "") for dr in demo.app.routes]:
        demo.app.routes.append(route)

app = demo.app

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)


