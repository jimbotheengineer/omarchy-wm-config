# Installing and customizing this WM profile

## Scope and files

The requested result is a Crimson Gold Hyprland + Noctalia desktop on an existing Omarchy
installation, using the included dragon wallpaper. Work as the recipient's desktop user.
Inspect this bundle before running its scripts. Do not copy the source machine's home tree,
install another distribution's repositories, or import anyone's account/session state.

This is a **standalone profile**, not a small override layered on Omarchy defaults.
`config/hypr/hyprland.lua` loads this bundle's modules and starts Noctalia. It does not load
Omarchy's default shell or default keybindings. Core Omarchy programs remain installed, but
default shell/menu integration and some desktop startup helpers are replaced by this profile.
If the recipient needs those integrations, adapt the profile deliberately and retest.

| File | Purpose |
| --- | --- |
| `config/hypr/hyprland.lua` | Entry point and Lua module reload handling |
| `config/hypr/config/variables.lua` | App commands and recipient monitor assignments |
| `config/hypr/config/monitors.lua` | Preferred-mode portable display setup |
| `config/hypr/config/workspaces.lua` | Eight numbered workspaces and gaming workspace |
| `config/hypr/config/binds.lua` | Keyboard/mouse shortcuts |
| `config/hypr/config/decorations.lua` | Gaps, borders, blur, opacity and rounding |
| `config/hypr/config/misc.lua` | Layout and rendering behavior |
| `config/hypr/config/windowrules.lua` | Application/window behavior and Noctalia layer effects |
| `config/hypr/noctalia.lua` | Current generated Hyprland color adapter |
| `config/noctalia/config.toml` | Bar layout, shell options, wallpaper and theme selection |
| `config/noctalia/palettes/Crimson Gold.json` | Persistent color palette, dark/light and terminal colors |
| `config/kitty/` | Matching terminal theme and 85% background opacity |
| `wallpapers/dragon.png` | Original-resolution wallpaper with metadata removed |
| `optional/community-widgets.toml` | Optional Bongo Cat and timer bar arrangement |

Paths above are bundle-relative. After installation, `config/` maps to the recipient's
`$XDG_CONFIG_HOME` or `~/.config`. The wallpaper is installed beneath `$XDG_DATA_HOME` or
`~/.local/share`, at `wm-profile/wallpapers/dragon.png`.

## 1. Inspect the recipient and prepare

1. Confirm Omarchy is already installed. Read the recipient's existing Hyprland entry point,
   launch command, display layout and shell autostart mechanism. Check whether it uses a
   `hyprland.lua` entry point or an older `hyprland.conf`/explicit `--config` session command.
2. Check `Hyprland --version`, `Hyprland --help`, `noctalia --version`, and `noctalia --help`.
   This export was validated with Hyprland **0.57.2** and native Noctalia **5.5.0**. Older
   Hyprlang configs and Noctalia v4 Quickshell settings are incompatible. Later versions still
   require validation; the minimum-version check alone does not prove compatibility.
3. Update through the recipient's normal Omarchy workflow if needed. Native Noctalia's
   documented Arch package is `noctalia`. Do not substitute `noctalia-shell` v4.
4. Install missing application dependencies or change their launcher commands before installing.
   The exported defaults use `kitty`, `dolphin`, `brave`, `gnome-text-editor`,
   `gnome-calculator`, `btop`, `hyprpicker`, `uwsm`, and `dbus-update-activation-environment`.
   Some may already be present. Brave may need the recipient's existing browser installation
   mechanism; using their installed browser in `variables.lua` is equally valid. For standard
   Arch packages, a typical missing-app install is:

   ```sh
   sudo pacman -S --needed noctalia kitty dolphin gnome-text-editor gnome-calculator btop hyprpicker
   ```

5. Keep a working terminal and a way to access a TTY. Inventory duplicate shell providers:
   Omarchy Shell, Waybar, other notification daemons, wallpaper processes, lock/idle managers,
   and polkit agents. Read their actual autostart entries or user-unit enablement. Choose one
   owner for each role before the next login. This profile starts Noctalia itself and enables
   its polkit agent; do not also enable `noctalia.service`. Do not disable unrelated services.

Official references: [Omarchy dotfiles](https://omarchy.org/manual/dotfiles/),
[Noctalia installation](https://docs.noctalia.dev/noctalia/getting-started/installation/), and
[Hyprland configuration](https://wiki.hypr.land/Configuring/Start/).

## 2. Customize hardware and applications

Edit the **bundle** before installation so the dry run checks the final configuration.

- `variables.lua`: choose available terminal, file manager, browser, editor, and calculator.
  Commands with arguments are allowed. `uwsm app --` is used by the bindings; remove that
  prefix only for a recipient session that does not use UWSM.
- `monitors.lua`: the shipped rule selects preferred modes with automatic position and scale.
  Use `hyprctl -j monitors all` on the recipient to choose any specific mode, arrangement,
  rotation or scale. Add HDR/VRR only after checking their hardware. The source machine's
  connector assignments and calibration were omitted.
- The installer generates `MONITOR1..3` using connected output names when run inside the
  recipient's active Hyprland session. With one output, missing assignments reuse that output.
  Without a live session, the fallback is monitor index `"0"`; review assignments after login.
  For predictable monitor order, edit the installed variables after inspecting the actual outputs.
- `workspaces.lua`: workspaces 1, 2, 3 and 7 use centered master on the first monitor;
  4, 5, 6 and 8 use the second. On a single-monitor recipient all eight use that monitor.
  The first group's center master fraction is about one third.
- `inputs.lua`: set the recipient's `kb_layout` and any keyboard options explicitly if needed.
  The shipped digit shortcuts use physical keycodes and work independently of shifted digit
  symbols. Test them on the recipient's keyboard. Adjust touchpad gestures if unwanted.
- Review `windowrules.lua`: application/game exceptions are retained as behavior preferences;
  public Steam application IDs here are not account identifiers. Remove rules for unneeded apps.
  Default app windows are opaque, with terminal transparency owned by Kitty.
- Source monitor-specific desktop widget and lock-screen placements were excluded. Add the
  desktop clock/audio visualizer through Noctalia Settings and place them on the recipient's
  displays. The base bar does not need community plugins.

## 3. Validate, install and activate

```sh
python3 install.py --check
python3 install.py --install
```

The check stages files, resolves the recipient wallpaper path, detects recipient outputs, and
runs Hyprland's config verifier and Noctalia's config validator. No services are started.
The installer refuses missing launcher commands. Resolve those in the bundle and repeat.

Installation backs up and replaces these targets:

- `~/.config/hypr/`
- `~/.config/noctalia/`
- `~/.config/kitty/`
- `~/.local/state/noctalia/settings.toml`
- `~/.local/share/wm-profile/wallpapers/dragon.png`

XDG configuration/state/data overrides are honored for a normal install. The settings override
file is reset to a minimal schema marker because old GUI overrides otherwise take precedence
over the imported TOML. Other Noctalia histories, credentials and state are left in place on
the recipient; their existing account data is never part of this export.

Record the backup directory printed by the installer. It contains the recipient's previous
configuration and is private to that machine. Do not add it to any shared archive.

Before logging out, finish resolving duplicate shell services/autostart discovered in step 1.
No default shell processes or services are stopped by this installer. On the next login, the
new Hyprland config starts Noctalia. If the session launcher pins an old `.conf` path, update
that **recipient-specific launcher** to the installed Lua entry point and record its previous
value separately for rollback. Do not change a login manager or session launcher blindly.

Once logged in:

```sh
hyprctl configerrors
noctalia config validate
hyprctl -j monitors
```

Check: one bar per display; wallpaper visible; crimson active border; gold accents; terminal
transparency; launcher, notifications and volume; lock/unlock; screenshots saved locally;
focus/move shortcuts; and all workspaces. Screen sharing should use the recipient's existing
Hyprland portal. If clipboard, tray, network or locking fails, inspect Noctalia logs and the
recipient's service/portal setup before changing packages or disabling services.

Useful bindings: Super+Return terminal; Super+Space launcher; Super+Z settings;
Super+X control center; Super+L lock; Super+Shift+S region screenshot; Super+V clipboard;
Super+Q close; Super+F fullscreen; Super+Alt+Space float. Super+1/2/3 focus monitors;
Super+Alt+1..4 selects absolute workspaces; Super+Control+1..4 selects a monitor-relative
workspace. The full bindings file is authoritative.

## 4. Change the color scheme

**Use the custom palette as the persistent source of truth.** The selected scheme is controlled
by `theme.source = "custom"`, `theme.custom_palette = "Crimson Gold"`, and `theme.mode = "dark"`
in Noctalia's TOML. To create a variant, copy `palettes/Crimson Gold.json` to a new filename
and set `custom_palette` to that filename's stem. Keep valid six-digit `#RRGGBB` strings.

| Palette token (dark mode) | Current | Visible role |
| --- | --- | --- |
| `mPrimary` | `#C81D25` | Crimson primary accent, active window border, workspace accent |
| `mOnPrimary` | `#FFFFFF` | Content on primary accent |
| `mSecondary` | `#D4AF37` | Gold icons, clock, network/volume, active window-group border |
| `mOnSecondary` | `#070707` | Content on secondary accent; custom bar group/tray fill |
| `mTertiary` | `#B3922E` | Additional accent |
| `mError` / `mOnError` | `#C81D25` / `#FFFFFF` | Session/destructive accent and content |
| `mSurface` / `mOnSurface` | `#070707` / `#D9D9D9` | Main dark surface, inactive border, normal foreground |
| `mSurfaceVariant` / `mOnSurfaceVariant` | `#222222` / `#D9D9D9` | Alternate surface and foreground |
| `mOutline` | `#6B5A32` | Outlines |
| `mHover` / `mOnHover` | `#8B0D14` / `#FFFFFF` | Hover background and content |

The palette has both `dark` and `light` objects. Each also has a `terminal` object with
background, foreground, cursor, selection colors, and normal/bright ANSI colors. Update those
too for a complete variant, keeping text readable on its associated background.

Noctalia's enabled built-in `hyprland` and `kitty` templates generate these adapters:

- `~/.config/hypr/noctalia.lua`: active border ← primary, inactive border ← surface;
  active group border ← secondary; locked group border ← error; matching group-bar colors.
- `~/.config/kitty/themes/noctalia.conf`: terminal colors. `kitty.conf` includes this file.

After editing the palette, open Noctalia Settings with Super+Z and reselect/apply the custom
palette (or switch away and back) to regenerate the adapters. Verify both files changed and
run `hyprctl reload`. Open a new Kitty window if its current colors did not reload. Do not
rely on edits to generated adapters for persistent customization: template application can
overwrite them. Before Noctalia is running, an agent may update the copied adapters manually
to match the palette, preserving their existing syntax.

Noctalia's TOML uses **semantic color names**, without `m`: for example
`[widget.clock] color = "secondary"`. To recolor a particular widget independently, change
its `color` to another supported token. The custom capsule group and tray use `on_secondary`
as their fill; the workspace capsule uses `on_primary`. Inspect those fill choices when
changing foreground/background pairs.

Remaining styling controls are separate:

- `config/hypr/config/colors.lua` supplies the base/fallback colors, including the splash
  color. Most border/group colors are then overwritten by `noctalia.lua`, which is applied
  last. Update fallback/splash colors if the entire scheme should change.
- `decorations.lua`: inner gap 3, outer gap 8, border 2, rounding 10, blur size 5/passes 4.
- `kitty.conf`: `background_opacity 0.85`; use `1.0` for opaque terminal backgrounds.
- `config/noctalia/config.toml`: bar scale, thickness, corner radii, margins, widget colors.

Example: for blue/silver accents, change dark `mPrimary` to `#4F8CFF`, `mSecondary` to
`#CBD5E1`, and corresponding `mOn*` values for readable text. Update terminal cursor and ANSI
accents, apply the palette, and verify bar icons, borders, groups, and terminal all agree.
The wallpaper stays the same until separately replaced. Put a new wallpaper file in the
recipient's data directory and change `[wallpaper.default].path`; do not use a source-user path.

## 5. Optional community widgets and separate LLM plugin

The source arrangement included Bongo Cat and a timer bar. Install/enable `noctalia/bongocat`
and `noctalia/timer` using Noctalia's plugin interface. Inspect and merge
`optional/community-widgets.toml` into the active config only after those plugins exist.
Its bar arrays replace the corresponding base arrays. Merge the plugin enable list with any
recipient choices rather than disabling unrelated plugins. Verify the effective config if
Noctalia's GUI settings override those arrays. No notes, timers, recordings or plugin state
from the source account are included.

The custom LLM control plugin has its own archive and `AGENTS.md`. Do not enable it while
installing the core WM. It needs a separately prepared backend, services and model assets.

## 6. Rollback

From the retained bundle directory, with the actual backup path printed during installation:

```sh
python3 install.py --restore "$HOME/.local/state/wm-profile/backups/ACTUAL_BACKUP_DIRECTORY"
```

Restore any recipient session-launcher or service-enablement edits recorded separately, then
log out and back in. The restore script restores prior target contents and removes targets
that did not previously exist. It does not restart the session, install/remove packages,
change enabled services, or undo custom edits outside the listed targets.
