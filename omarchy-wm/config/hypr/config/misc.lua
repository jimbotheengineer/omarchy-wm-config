hl.config({
    general = {
        -- Pin the source profile's fallback layout instead of relying on defaults.
        layout = "dwindle",
    },
    dwindle = {
        preserve_split = true,
    },
    master = {
        -- On centered-master workspaces, three windows form equal-width
        -- left, center, and right columns on the ultrawide.
        orientation = "center",
        -- Slightly above 1/3 compensates for the two inter-column gaps and
        -- integer rounding.
        mfact = 0.3337,
        new_status = "slave",
        -- Always reserve the middle third for the master, even with fewer
        -- than three windows open.
        slave_count_for_center_master = 0,
    },
    ecosystem = {
        no_update_news = true,
        no_donation_nag = true,
    },
    misc = {
        col = {
            splash = CACHYLGREEN,
        },
        middle_click_paste = false,
        enable_swallow = true,
        swallow_regex = "(kitty|ghostty|[Kk]onsole|Alacritty|gnome-terminal|xfce[0-9]?-terminal)",
        vrr = 0, -- enable only after checking recipient display support
    },
    render = {
        -- Direct scanout bypasses the SDR-to-HDR color transform for some
        -- fullscreen XWayland games; overlays looked correct because they
        -- temporarily forced the compositor path.
        direct_scanout = 0,
        -- Use the option below if you find games constantly black screening for a couple seconds whenever direct scanout enables/disables
        -- non_shader_cm = 0,
    },
    xwayland = {
        force_zero_scaling = true
    },
})
