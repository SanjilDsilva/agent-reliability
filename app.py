import os
import gradio as gr
from agent_reliability.database import Base, engine
from agent_reliability.api import app as fastapi_app

# Ensure database tables exist automatically
Base.metadata.create_all(bind=engine)

# Mount our custom 3-panel dashboard on root, and Gradio on /gradio
demo = gr.Blocks(title="AgentReliability")
app = gr.mount_gradio_app(fastapi_app, demo, path="/gradio")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 7860))
    uvicorn.run(app, host="0.0.0.0", port=port)
