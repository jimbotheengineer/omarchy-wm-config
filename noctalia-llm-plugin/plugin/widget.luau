--!nonstrict
local SCRIPT = "__LLM_CONTROL_HELPER__"
local info = { engine = "vllm", state = "unknown", busy = false }
local commandRunning = false
local statusPending = false

local function name(engine)
  return engine == "ninfer" and "NInfer" or "vLLM"
end

local function render()
  local title = name(info.engine)
  local state = info.state
  barWidget.setText(title)
  local tooltip = {
    { title, state == "ready" and "ready on :8000" or state },
    { "Left click", state == "ready" and "stop active server" or "start saved server" },
    { "Right click", "engine, model and template menu" },
  }
  if info.active_model then
    table.insert(tooltip, { "Active model", info.active_model })
    table.insert(tooltip, { "Vision", info.active_vision or "off" })
    if info.active_context then table.insert(tooltip, { "Context", tostring(info.active_context) .. " tokens" }) end
  end
  if info.pending and info.selected then
    table.insert(tooltip, { "Pending default", name(info.selected.engine) .. " / " .. info.selected.model
      .. " / " .. info.selected.template .. " / vision " .. (info.selected.vision or "off") })
    if info.selected.context then
      table.insert(tooltip, { "Pending context", tostring(info.selected.context) .. " tokens" })
    end
  end
  if info.busy or commandRunning then
    table.insert(tooltip, { "Controls locked", "operation or benchmark in progress" })
  end
  if info.busy or commandRunning or state == "loading" or state == "stopping" then
    barWidget.setGlyph("loader")
    barWidget.setColor("secondary")
    barWidget.setGlyphColor("secondary")
    table.insert(tooltip, { "Startup", "clicks disabled until ready" })
  elseif state == "ready" then
    barWidget.setGlyph("brain")
    barWidget.setColor("secondary")
    barWidget.setGlyphColor("secondary")
  elseif state == "failed" or state == "unknown" then
    barWidget.setGlyph("player-stop")
    barWidget.setColor("error")
    barWidget.setGlyphColor("error")
  else
    barWidget.setGlyph("power")
    barWidget.setColor("on_surface", "script")
    barWidget.setGlyphColor("on_surface", "script")
  end
  barWidget.setTooltip(tooltip)
end

local function refreshStatus()
  if statusPending then return end
  statusPending = true
  local accepted = noctalia.runAsync({ "python3", SCRIPT, "status" }, function(result)
    statusPending = false
    local data = result.exitCode == 0 and noctalia.json.decode(result.stdout or "") or nil
    if data then
      info = data
    else
      info = { engine = info.engine, state = "unknown", busy = false }
    end
    render()
  end)
  if not accepted then statusPending = false end
end

local function runControl(action)
  if commandRunning or info.busy or info.state == "loading" or info.state == "stopping" then
    noctalia.notify("LLM server", "An operation, startup or benchmark is in progress; please wait")
    return
  end
  commandRunning = true
  render()
  local accepted = noctalia.runAsync({ "python3", SCRIPT, action }, function(result)
    commandRunning = false
    if result.exitCode ~= 0 then
      noctalia.notifyError("LLM control failed", noctalia.string.trim(result.stderr or ""))
    else
      noctalia.notify("LLM server", action == "stop" and "Server stopped" or "Saved server is starting")
    end
    refreshStatus()
    render()
  end)
  if not accepted then
    commandRunning = false
    noctalia.notifyError("LLM server", "Could not launch the control command")
    render()
  end
end

function update()
  noctalia.setUpdateInterval(1500)
  refreshStatus()
end

function onClick()
  if info.state == "unknown" then
    refreshStatus()
    noctalia.notify("LLM server", "Checking server status; please wait")
    return
  end
  runControl(info.running and "stop" or "start")
end

function onRightClick()
  noctalia.togglePanel("local/llm-control:chooser")
end

function onIpc(event, _payload)
  if event == "start" or event == "stop" then runControl(event)
  elseif event == "toggle" then onClick()
  elseif event == "refresh" then refreshStatus() end
end

render()
refreshStatus()
