# Crimson Gold WM export

Shareable Hyprland + Noctalia configuration, dragon wallpaper, and matching Kitty colors.

**Installing agent: read [AGENTS.md](AGENTS.md) first.** It covers dependencies, installation,
monitor and keyboard setup, color customization, checks, and rollback.

This is a complete alternate desktop profile on Omarchy. It replaces the user's Hyprland,
Noctalia, and Kitty configurations with backups. It uses Noctalia for the bar, launcher,
notifications, lock screen, and wallpaper. The installer does not restart the current session.
It requires Hyprland 0.57.2+ with Lua support and native Noctalia 5.5.0+.

```sh
python3 install.py --check
python3 install.py --install
```

The custom LLM bar plugin is delivered in a separate archive. The core profile works without it.
See [PRIVACY.md](PRIVACY.md) for exclusions and [VALIDATION.md](VALIDATION.md) for checks performed.
