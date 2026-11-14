# Crimson Gold for Omarchy

A dark Hyprland desktop with crimson borders, gold accents, a Noctalia bar,
transparent Kitty terminals, the included dragon wallpaper, and the configured tiling layout.

![Included dragon wallpaper](omarchy-wm/wallpapers/dragon.png)

## Download

| Download | What's included |
| --- | --- |
| [Desktop configuration](https://github.com/jimbotheengineer/omarchy-wm-config/releases/latest/download/omarchy-wm.zip) | Hyprland tiling/workspaces/shortcuts, Noctalia, color palette, Kitty theme, wallpaper, and installer |
| [Optional LLM bar plugin](https://github.com/jimbotheengineer/omarchy-wm-config/releases/latest/download/noctalia-llm-plugin.zip) | Separate vLLM/NInfer widget, chooser, and backend reference files |
| [Checksums](https://github.com/jimbotheengineer/omarchy-wm-config/releases/latest/download/SHA256SUMS) | SHA-256 hashes for both ZIP files |

Downloads are public and do not require a GitHub account. You can also browse the
[latest release](https://github.com/jimbotheengineer/omarchy-wm-config/releases/latest).
The desktop works without the LLM plugin. The plugin needs its own local inference
services and models, which are not included.

## Tiling and workspaces

The window layout is included along with the theme:

- Centered-master tiling on workspaces **1, 2, 3, and 7**, with the master column
  about one third of the screen and side columns for other windows.
- Workspaces **4, 5, 6, and 8** assigned to the second display, with a single-display
  fallback that keeps all eight workspaces available.
- A separate gaming workspace, application/window rules, focus and move shortcuts,
  mouse dragging/resizing, and master/dwindle layout controls.
- The configured gaps, borders, rounding, blur, and terminal transparency.

See [tiling details and controls](omarchy-wm/TILING.md) for the workspace map and shortcuts.
Display names and modes are adapted to your hardware during setup.

## Before you install

You need an existing Omarchy installation with **Hyprland 0.57.2 or newer**, Lua
configuration support, **native Noctalia 5.5.0 or newer**, and Python 3.
Noctalia v4/Quickshell configurations are incompatible with this export.

This installs a complete desktop profile, including its own shortcuts and Noctalia
shell. It replaces your Hyprland, Noctalia, and Kitty settings and backs up the
previous files. It does not restart your session. Monitor modes use portable
defaults; you may need to adjust the layout for your displays.

## Install the desktop

Extract `omarchy-wm.zip`, open a terminal in the extracted `omarchy-wm` folder, and run:

```sh
python3 install.py --check
```

Resolve any missing applications reported by the check. You can change the default
apps in `config/hypr/config/variables.lua` before installing. When the check passes:

```sh
python3 install.py --install
```

Save the backup path printed by the installer. Before logging out, check that your
session loads `~/.config/hypr/hyprland.lua` and that another bar, wallpaper tool, or
notification daemon will not start alongside Noctalia. Log out and back in to use
the new desktop.

To restore your previous configuration, run this from the extracted folder,
replacing the placeholder with the backup path printed during installation:

```sh
python3 install.py --restore /path/to/your/backup
```

Then log out and back in. Restore any session-launcher or service changes you made
separately as well.

## Make it yours

Press **Super+Z** to open Noctalia Settings. The persistent custom palette is
`~/.config/noctalia/palettes/Crimson Gold.json`: `mPrimary` controls the crimson
accent and `mSecondary` controls the gold accent. After editing, reselect the
palette in Settings to apply it to the bar, window borders, and terminal theme.

Terminal transparency is set by `background_opacity` in `~/.config/kitty/kitty.conf`.
Set it to `1.0` for an opaque background. Gaps, borders, and rounding are in
`~/.config/hypr/config/decorations.lua`.

## Everyday shortcuts

| Shortcut | Action |
| --- | --- |
| Super+Return | Open terminal |
| Super+Space | Open launcher |
| Super+Z | Open settings |
| Super+X | Open control center |
| Super+V | Open clipboard |
| Super+Shift+S | Capture a screen region |
| Super+L | Lock the screen |
| Super+Q | Close the active window |
| Super+F | Toggle fullscreen |

## More information

See the [privacy notes](omarchy-wm/PRIVACY.md) and
[validation results](omarchy-wm/VALIDATION.md). For setup through an AI assistant,
share the repository and its separate [agent README](README.agents.md).
