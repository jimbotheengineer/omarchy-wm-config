# Crimson Gold WM export

Shareable Hyprland + Noctalia configuration, dragon wallpaper, and matching Kitty colors.

This package contains the desktop configuration and wallpaper. The optional LLM bar plugin
is a separate download. [Tiling layouts, workspace assignments, and controls](TILING.md)
are included with the profile.

This is a complete alternate desktop profile on Omarchy. It replaces the user's Hyprland,
Noctalia, and Kitty configurations with backups. It uses Noctalia for the bar, launcher,
notifications, lock screen, and wallpaper. The installer does not restart the current session.
It requires Hyprland 0.57.2+ with Lua support and native Noctalia 5.5.0+.

Run `python3 install.py --check` from this folder to validate the configuration and see
the affected files. Resolve any missing applications before using `python3 install.py --install`.
Keep the backup path printed by the installer. Check that the session loads the Lua entry point
and that another desktop shell will not start alongside Noctalia, then log out and back in.

To restore the previous configuration, use `python3 install.py --restore /path/to/your/backup`,
then log out and back in. Session-launcher and service changes must be restored separately.

The core profile works without the LLM plugin. See [PRIVACY.md](PRIVACY.md) for exclusions
and [VALIDATION.md](VALIDATION.md) for checks performed. Setup automation has its own
[agent guide](AGENTS.md), including detailed color customization and rollback instructions.
