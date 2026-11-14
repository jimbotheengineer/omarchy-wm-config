# Separate Noctalia LLM control plugin

Anonymous export of the custom vLLM/NInfer bar widget and chooser. Read [AGENTS.md](AGENTS.md).

Plugin ID: `local/llm-control`. Native Noctalia 5.5.0, plugin API 24.

`plugin/` contains the frontend. `backend-reference/` contains sanitized controller/launcher
source and example user units. No model weights, Python environments, local selections,
credentials, logs or backend builds are included. The core WM archive does not depend on this.

This is **not a turnkey LLM server installer**. Prepare the backend on the recipient first,
then point the plugin installer at its absolute helper path.
