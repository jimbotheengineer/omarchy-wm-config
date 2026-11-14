# Set up the optional custom LLM bar plugin

## Contents and dependencies

This package is separate from the WM export. The frontend contains a bar toggle and a chooser
for engine, model, template, vision and context. It requires native Noctalia 5.5.0 with plugin
API 24, Python 3, and user systemd services. Its namespace/author and personal aliases were
anonymized. Do not reintroduce the source account's paths or service names.

The frontend calls `server-control.py` with `status`, `list`, `select`, `start`, `stop`, and
`restart`. The included backend reference also supports `toggle` and `launch-ninfer`.
The helper returns JSON used directly by both Luau entries. Preserve that contract when
adapting it. Live logs follow `vllm-local.service` or `ninfer-local.service`.

## Prepare the backend first

1. Inspect the recipient's hardware and existing inference setup. Do not start or interrupt
   inference servers as part of the core WM install. Enabling this plugin is a separate step.
2. Read the sanitized reference files before choosing a backend layout:

   | Reference file | Intended recipient location |
   | --- | --- |
   | `backend-reference/llm/control/server-control.py` | `~/llm/control/server-control.py` |
   | `backend-reference/llm/vllm/model-selection.py` | `~/llm/vllm/model-selection.py` |
   | `backend-reference/llm/vllm/start-local.sh` | `~/llm/vllm/start-local.sh` |
   | `backend-reference/systemd/vllm-local.service` | `~/.config/systemd/user/vllm-local.service` |
   | `backend-reference/systemd/ninfer-local.service` | `~/.config/systemd/user/ninfer-local.service` |

3. The reference resolves paths under the recipient's home. It expects local vLLM model and
   template assets under `~/llm/vllm/models/`, a vLLM virtual environment at
   `~/llm/vllm/.venv`, and NInfer checkouts/builds/models under `~/ninfer` and `~/ninfer-all`.
   Model artifacts, templates, engine builds and GPU dependencies are deliberately absent.
   Edit `NINFER_MODELS`, `NINFER_TEMPLATES`, `MODELS`, and launcher options to match actual
   recipient assets and engine versions. Mark profiles unverified until checked there.
   The bundled profiles/VRAM estimates are reference defaults, not hardware guarantees.
4. Reference services are named `vllm-local.service` and `ninfer-local.service`, with model
   alias `local-llm` on loopback port 8000. The NInfer unit conflicts with vLLM so they do not
   remain resident together. Adapt both unit names in the frontend's `panel.luau` if changing
   them. `%h` in example units is systemd's recipient-home specifier. Copy scripts only after
   reviewing them; mark `start-local.sh` executable if used by the service.
5. The helper stops the other engine and unloads resident Ollama models before starting a
   server. It can also update a matching `local-llm` entry in `~/.pi/agent/models.json` if
   that file exists. Review or disable `pi_model_update`/`save_pi_model` if that integration is
   not wanted; an unrelated Pi model config must not be assumed to have this provider/model.
   It also checks for a local benchmark process and serializes controller operations.
6. Review resource limits, context size and GPU options. Defaults were kept as reference;
   tune them for the recipient. No engine should be automatically enabled at login. If user
   units are installed, run `systemctl --user daemon-reload`, and use explicit start/stop
   during recipient backend validation. The plugin installer never copies units or starts them.
7. Check Python syntax, the helper's `list` and `status` JSON, available profiles and template
   paths before connecting the bar. Creating fresh selection/lock files on the recipient is
   expected. Do not copy selection state or private client configuration from another machine.
   Validate each chosen engine's start/stop/restart, health, model/template choice and context
   behavior against the actual builds. Keep only tested choices available in the chooser.

If the recipient already has an inference controller, adapting its JSON interface to this
frontend may be simpler than adopting the reference backend. Do not pretend copying the
widget installs a working vLLM/NInfer stack.

## Install the frontend

With a prepared backend at the intended location:

```sh
python3 install.py --helper "$HOME/llm/control/server-control.py"
python3 install.py --helper "$HOME/llm/control/server-control.py" --install
```

The default invocation checks/lints the staged plugin. `--install` copies the plugin into
`$XDG_DATA_HOME/noctalia/plugins/llm-control` (default `~/.local/share/...`), replacing its
helper-path placeholder with the recipient's absolute path. An existing plugin directory is
moved to a sibling backup first. It does not modify Noctalia's config or enable anything.

Enable the plugin through Noctalia Settings, or:

```sh
noctalia msg plugins enable local/llm-control
```

Merge this into the active Noctalia TOML:

```toml
[widget.vllm]
type = "local/llm-control:toggle"
```

Append `"vllm"` to `[bar.default].end`, preferably just before `"session"`. Preserve the
other entries. GUI overrides in `~/.local/state/noctalia/settings.toml` may take precedence;
use the Settings UI or inspect `noctalia config export merged --credentials omit` locally
when the widget does not appear. That export may contain the recipient's private paths and
location even with credentials omitted; do not share its raw output.

## Verify and customize

```sh
noctalia plugins lint "$HOME/.local/share/noctalia/plugins/llm-control"
noctalia config validate
noctalia msg plugin local/llm-control:toggle all refresh
```

Confirm off/loading/ready/failed states, left-click start/stop, right-click chooser, saving a
default without restarting, applying pending choices, live logs, and transitions between
engines. Use `focused` for action IPC so multi-monitor instances do not duplicate actions:

```sh
noctalia msg plugin local/llm-control:toggle focused start
noctalia msg plugin local/llm-control:toggle focused stop
```

The widget uses semantic theme colors: `secondary` for ready/loading, `error` for failure,
and `on_surface` when off. These follow the WM's Noctalia palette. Change those color names in
`widget.luau` for independent styling, or update the persistent custom palette as described
in the main WM guide. The chooser uses the shell's regular panel theme.

## Remove or roll back

Remove `"vllm"` from bar arrays and disable `local/llm-control` in Noctalia. Restore a saved
plugin directory if one existed. Backend files/services are managed separately: first stop
only the units installed for this plugin, restore their previous versions if backed up, and
reload the user systemd manager. Never delete model assets or modify unrelated services as
part of removing a bar widget.
