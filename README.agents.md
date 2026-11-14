# Agent README: install and customize the Omarchy WM export

This document is for an AI or automation agent working on the recipient's computer.
The main [README.md](README.md) is for human readers. Keep agent workflows in this file
and the package-specific `AGENTS.md` guides.

## Required reading and scope

Read [omarchy-wm/AGENTS.md](omarchy-wm/AGENTS.md) in full before desktop installation.
It contains the dependency list, configuration map, display and keyboard setup,
installation procedure, color-token table, validation steps, and rollback instructions.
Also read [TILING.md](omarchy-wm/TILING.md) for the included layout and shortcut map.

For the optional LLM widget, also read
[noctalia-llm-plugin/AGENTS.md](noctalia-llm-plugin/AGENTS.md) in full. Install the core
desktop independently. Add the custom plugin only when it is within the recipient's
requested scope and its backend is prepared. Do not treat its reference source as a
complete inference server installation.

## Obtain and inspect the files

The repository and release assets are public. Clone the repository for both packages
and this entry point, or download a package ZIP:

- [Desktop ZIP](https://github.com/jimbotheengineer/omarchy-wm-config/releases/latest/download/omarchy-wm.zip)
- [Separate plugin ZIP](https://github.com/jimbotheengineer/omarchy-wm-config/releases/latest/download/noctalia-llm-plugin.zip)
- [SHA256SUMS](https://github.com/jimbotheengineer/omarchy-wm-config/releases/latest/download/SHA256SUMS)

Each ZIP contains its own `AGENTS.md` with the complete package workflow. Verify the
download against `SHA256SUMS`, extract it, and inspect the included scripts/configuration.
Resolve relative file paths against the package directory, not the agent's starting directory.

## Desktop workflow

1. Inspect the recipient's existing Omarchy version, Hyprland session entry point,
   active shell services, output names, keyboard layout, and app commands. Preserve
   existing recipient configuration and any launcher/service changes needed for rollback.
2. Confirm Hyprland 0.57.2+ with Lua support, native Noctalia 5.5.0+, Python 3, and the
   launchers used by the bundle. Follow the detailed package guide for missing dependencies.
3. Customize the copied bundle for the recipient. Use their output names and paths.
   Review `variables.lua`, `monitors.lua`, `inputs.lua`, and the workspace rules. Preserve
   the included centered-master tiling, workspace grouping, layout shortcuts, and window
   rules unless the recipient requests changes. This profile replaces the standard
   Omarchy shell/bindings rather than layering on them.
4. From `omarchy-wm/`, run `python3 install.py --check`. Resolve missing commands and
   validation errors before proceeding. Run `python3 install.py --install` within the
   authorized installation scope. Save the printed backup path locally.
5. Resolve duplicate shell/bar, wallpaper, notification, lock/idle, and polkit providers
   using the actual recipient autostart setup. Follow the package guide for session
   activation. The installer does not restart processes or change service enablement.
6. After activation, check `hyprctl configerrors`, `noctalia config validate`, and
   display/workspace behavior. Verify the wallpaper, bar, launcher, terminal, locking,
   notifications, screenshots, and shortcuts. Open three ordinary windows on a master
   workspace and verify the centered master and side columns. Report checks that remain
   unverified.

The full [package guide](omarchy-wm/AGENTS.md) is authoritative for details, including
XDG paths, optional community widgets, service ownership, and recovery.

## Color customization workflow

Use [the package color guide](omarchy-wm/AGENTS.md#4-change-the-color-scheme) for the
complete token map and generation behavior.

1. Copy `config/noctalia/palettes/Crimson Gold.json` to a new palette filename if
   making a named variant. Set `theme.source`, `theme.custom_palette`, and `theme.mode`
   in Noctalia's TOML to select it.
2. Change the `dark` and/or `light` palette objects. `mPrimary` is the main accent,
   `mSecondary` the gold/secondary accent, and `mSurface` the background. Keep the
   corresponding `mOn*` foreground colors readable. Update the nested terminal palette too.
3. Apply/reselect the custom palette in Noctalia so the Hyprland and Kitty templates
   regenerate. Inspect `~/.config/hypr/noctalia.lua` and
   `~/.config/kitty/themes/noctalia.conf`, then reload Hyprland and verify a Kitty window.
4. Keep widget colors expressed as semantic tokens such as `secondary` and `error`.
   Check capsule fills and foregrounds together. Adjust fallback/splash colors, terminal
   opacity, gaps, and rounding separately when requested.

Edit the persistent palette rather than relying on manual changes to generated adapters.
Do not change the included wallpaper unless requested.

## Privacy and completion

Do not copy source-account state, credentials, logs, histories, private model settings,
or recipient backups into the repository or a shared archive. The export intentionally
omits those. See [PRIVACY.md](omarchy-wm/PRIVACY.md).

At handoff, report what was installed/customized, the local backup path, checks performed,
and any remaining recipient-side validation. Keep the core desktop and optional plugin
distinct. Use the documented restore command if rollback is needed.
