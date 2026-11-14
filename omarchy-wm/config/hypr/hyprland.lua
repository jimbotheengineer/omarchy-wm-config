-- Standalone Hyprland + Noctalia profile for Omarchy.
local root = (os.getenv("XDG_CONFIG_HOME") or (os.getenv("HOME") .. "/.config")) .. "/hypr/"
package.path = root .. "?.lua;" .. root .. "?/init.lua;" .. package.path
-- Clear this profile's cached modules so config reloads pick up edits.
for key in pairs(package.loaded) do
    if key:match("^config%.") or key == "noctalia" then package.loaded[key] = nil end
end
require("config.animations")
require("config.colors")
require("config.decorations")
require("config.variables")
require("config.environment")
require("config.inputs")
require("config.binds")
require("config.misc")
require("config.monitors")
require("config.windowrules")
require("config.workspaces")
require("noctalia").apply_theme()
require("config.autostart")
