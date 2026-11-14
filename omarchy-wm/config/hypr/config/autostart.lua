-- Do not also launch Omarchy Shell/Waybar or another wallpaper/notification daemon.
hl.on("hyprland.start", function()
    hl.exec_cmd("dbus-update-activation-environment --systemd --all")
    hl.exec_cmd("noctalia")
end)
