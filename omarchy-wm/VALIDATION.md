# Export validation

Validated using Hyprland 0.57.2 and native Noctalia 5.5.0.

- Hyprland `--verify-config`: config accepted.
- Noctalia configuration validator: config accepted.
- Noctalia plugin lint: zero errors and warnings.
- Python AST, Lua parser, shell syntax, TOML and JSON checks passed.
- Isolated temporary-home installation: correct recipient paths and complete backups.
- Isolated restore: original file contents restored; newly introduced targets removed.
- Separate plugin installer: paths containing spaces handled and repeat install backed up.
- Wallpaper: all source pixels and 5120×1440 resolution retained; metadata empty.
- Text review and scans: no source-account path, personal alias, location, hostname, hardware
  identifier, GitHub account string, email, MAC address, credential pattern or non-loopback
  IPv4 address found in the selected export.

For the public-download update, workspace rules, layout shortcuts, window rules, decorations,
and inputs were compared with the active source configuration and matched. Live read-only
queries confirmed centered master with fraction `0.3337`, slave insertion, reserved center,
and dwindle on the remaining numbered workspaces. The dwindle fallback was made explicit
in the exported config so installation does not depend on a recipient's default layout.
Public repository/release links identify the hosting account as expected; no source-machine
identity was added to the configuration.

The source user's live WM configuration and services were not changed. No real recipient
Omarchy session was available for graphical activation testing. The export does not establish
that a different recipient's displays, lock/auth setup, app packages or inference engines
will work without following the guide and validating locally. The plugin backend reference
received syntax checks; no model server was launched as part of this export.
