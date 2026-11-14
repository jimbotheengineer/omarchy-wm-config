# Tiling layout and controls

This profile includes the window-management setup as well as the wallpaper and colors.
The workspace rules, shortcuts, window rules, gaps, and decorations are included in
the desktop ZIP and applied by its installer.

## Workspace map

| Workspaces | Display | Layout |
| --- | --- | --- |
| 1, 2, 3, 7 | First display | Centered master |
| 4, 5, 6, 8 | Second display | Dwindle |
| `gaming` | Primary display | Dwindle, with game-specific window/fullscreen rules |

All eight numbered workspaces are persistent. With one display, both display assignments
point to it so the full set remains available. Display names are chosen on the computer
where you install the profile. Specific display modes, HDR calibration, and physical
arrangement are not imposed by the export.

## Centered master

Workspaces 1, 2, 3, and 7 use a master window in the center with other windows arranged
to its sides. The configured master fraction is `0.3337`, approximately one third of
the available width. With three tiled windows this creates a left, center, and right
column. The center remains reserved even with fewer side windows. New windows use
the slave position rather than automatically replacing the master.

**Super+M** swaps with the master, selects centered orientation, and sets the master
fraction to `0.5`. **Super+Shift+M** returns the centered master fraction to `0.3337`.
These controls apply only on a master-layout workspace.

## Dwindle

Dwindle is explicitly selected as the default layout for workspaces without a master
override. Existing split directions are preserved. **Super+J** toggles a split while
on a dwindle workspace.

## Window and workspace controls

The number shortcuts use physical number-row keys, so their positions remain usable
on keyboards where the digit characters need Shift.

| Shortcut | Action |
| --- | --- |
| Super+Arrow | Focus a window in that direction |
| Super+Shift+Arrow | Move a window in that direction |
| Super+left mouse drag | Drag the active window |
| Super+right mouse drag | Resize the active window |
| Super+Alt+Space | Toggle floating |
| Super+F | Toggle fullscreen |
| Super+D | Toggle maximized fullscreen mode |
| Super+1 / 2 / 3 | Focus the configured display |
| Super+Shift+1 / 2 / 3 | Move the active window to that display |
| Super+Alt+1..4 | Focus absolute workspace 1..4 |
| Super+Control+1..4 | Focus a monitor-relative workspace slot |
| Super+Shift+Control+1..4 | Move a window to a monitor-relative workspace slot |
| Super+Shift+Alt+1..4 | Move a window to a monitor-relative slot without following |
| Super+Control+Left / Right | Focus the previous / next workspace on the display |
| Super+Control+Shift+Left / Right | Move a window to the previous / next workspace |
| Super+Control+Down | Focus an empty workspace on the display |
| Super+S | Toggle the special workspace |
| Super+Alt+S | Move the active window to the special workspace |

You can also switch using the bar's workspace widget or the scroll bindings in
`config/hypr/config/binds.lua`.

## Included behavior and appearance

The profile keeps the application rules for picture-in-picture, dialogs, utility
windows, file manager placement, game exceptions, fullscreen handling, and terminal
opacity. It also keeps terminal swallowing for the configured terminal classes.
Some applications intentionally float or go fullscreen instead of tiling.

Inner gaps are 3, outer gaps 8, border width 2, and corner rounding 10. Kitty owns its
85% background opacity. These settings are independent of the layout algorithm.

## Customize the layout

After installation, the relevant files are under `~/.config/hypr/config/`:

- `workspaces.lua`: choose each workspace's display and layout.
- `misc.lua`: change the default layout, centered-master fraction, new-window placement,
  and split-preservation behavior.
- `binds.lua`: change layout, focus, move, resize, and workspace shortcuts.
- `variables.lua`: set display assignments and the number of monitor-relative shortcut slots.
- `windowrules.lua`: adjust application exceptions to tiling.
- `decorations.lua`: change gaps, border width, rounding, and blur.

Keep the backup created by the installer. Validate edits with `Hyprland --verify-config`
and check `hyprctl configerrors` after reloading. For automated setup, the separate
[agent guide](AGENTS.md) covers installation and recipient-side verification.
