# Separate Noctalia LLM control plugin

An optional vLLM/NInfer bar widget and chooser, packaged separately from the desktop.
Left-click starts or stops the saved server; right-click opens engine, model, template,
vision, and context controls.

Plugin ID: `local/llm-control`. Native Noctalia 5.5.0, plugin API 24.

`plugin/` contains the frontend. `backend-reference/` contains sanitized controller/launcher
source and example user units. No model weights, Python environments, local selections,
credentials, logs or backend builds are included. The core WM archive does not depend on this.

You need working local inference services before using the widget. Once the backend is
prepared, run `python3 install.py --helper /absolute/path/to/server-control.py` to check it;
add `--install` to copy the plugin. Enable it in Noctalia Settings and add its bar widget.

The detailed [agent setup guide](AGENTS.md) covers backend adaptation, installation,
bar configuration, validation, and removal.
