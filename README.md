# Omarchy WM configuration export

Crimson Gold Hyprland + Noctalia desktop, with the dragon wallpaper and matching Kitty colors.
The custom LLM bar plugin is separate.

| Package | Start here | Contents |
| --- | --- | --- |
| Core WM | [Agent setup and color guide](omarchy-wm/AGENTS.md) | Hyprland, Noctalia bar, custom palette, Kitty, wallpaper, installer and rollback |
| Optional plugin | [Plugin agent guide](noctalia-llm-plugin/AGENTS.md) | LLM widget/chooser and sanitized backend reference source |

Installing agents should read the relevant guide before running anything. The core profile
requires Hyprland 0.57.2+ with Lua configuration and native Noctalia 5.5.0+. It is a complete
alternate WM/shell profile for an existing Omarchy install. The plugin needs additional local
inference services and model assets; it is not required for the desktop.

For a clone:

```sh
cd omarchy-wm
python3 install.py --check
# Resolve dependencies and review the agent guide, then:
python3 install.py --install
```

The installer backs up the recipient's previous configs and does not restart the session.
See [validation](omarchy-wm/VALIDATION.md), [privacy exclusions](omarchy-wm/PRIVACY.md), and
the agent guide's color-token table and rollback section. Separate ZIP downloads and checksums
are provided with the release.
