--!nonstrict
local SCRIPT = "__LLM_CONTROL_HELPER__"
local models = {}
local engines = {}
local defaults = {}
local saved = nil
local chosenEngine = nil
local chosenModel = nil
local chosenTemplate = nil
local chosenVision = "off"
local chosenContext = 115200
local contextValid = true
local contextInputVersion = 0
local contextLimits = { min = 4096, max = 1048576, step = 256 }
local status = { state = "unknown", running = false, busy = false }
local busy = false
local loading = false
local statusPending = false
local message = ""

local function engineName(engine)
  return engine == "ninfer" and "NInfer" or "vLLM"
end

local function selectedModel()
  for _, model in ipairs(models[chosenEngine] or {}) do
    if model.id == chosenModel then return model end
  end
  return nil
end

local function selectedTemplate()
  local model = selectedModel()
  if model then
    for _, template in ipairs(model.templates) do
      if template.id == chosenTemplate then return template end
    end
  end
  return nil
end

local function changed()
  return saved ~= nil and (saved.engine ~= chosenEngine or saved.model ~= chosenModel
    or saved.template ~= chosenTemplate or (saved.vision or "off") ~= chosenVision
    or (chosenEngine == "ninfer" and (saved.context or 115200) ~= chosenContext))
end

local function vramEstimate(model)
  if not model or not model.vram then return nil end
  local profile = model.vram
  local mode = chosenVision == "on" and "on" or "off"
  local weights = profile.weights_gib[mode] or profile.weights_gib.off
  local other = profile.other_gib[mode] or profile.other_gib.off
  local pages = math.ceil(chosenContext / 64) * 64
  local kv = pages * profile.kv_bytes_per_token * profile.mtp_kv_ratio / (1024 * 1024 * 1024)
  return weights, kv, other
end

local function draw()
  local locked = busy or status.busy
  local transitioning = status.state == "loading" or status.state == "stopping"
  local server = status.active_engine and engineName(status.active_engine) or "none"
  local active = status.active_model and (server .. " • " .. status.active_model
    .. " • vision " .. (status.active_vision or "off")
    .. " • " .. tostring(status.active_context or "?") .. " tokens") or server
  local rows = {
    ui.label({ text = "LLM engine, model & template", fontWeight = "bold", fontSize = 19 }),
    ui.label({ text = "Active: " .. active .. " • " .. status.state .. (status.pending and " • saved default pending" or "") }),
    ui.label({ text = status.busy and "Controls locked while benchmark/operation runs" or "One server at a time • both use :8000 / local-llm" }),
    ui.label({ text = "Engine (saving does not restart the server)" }),
  }
  local buttons = {}
  for _, engine in ipairs(engines) do
    local id = engine.id
    table.insert(buttons, ui.button({ key = "engine-" .. id, text = engine.label,
      selected = chosenEngine == id, enabled = not locked, controlSize = "sm",
      onClick = function()
        chosenEngine = id
        local choice = defaults[id]
        chosenModel = choice and choice.model or nil
        chosenTemplate = choice and choice.template or nil
        chosenVision = choice and choice.vision or "off"
        chosenContext = choice and choice.context or (defaults.ninfer and defaults.ninfer.context) or 115200
        contextValid = true
        contextInputVersion += 1
        message = "Selection not saved yet"
        draw()
      end,
    }))
  end
  table.insert(rows, ui.row({ gap = 8 }, buttons))
  table.insert(rows, ui.label({ text = "Model (untested profiles may fail to start)" }))
  for _, model in ipairs(models[chosenEngine] or {}) do
    local id = model.id
    table.insert(rows, ui.button({ key = "model-" .. id, text = model.label,
      selected = chosenModel == id, enabled = not locked, controlSize = "sm",
      onClick = function()
        chosenModel = id
        chosenTemplate = model.templates[1] and model.templates[1].id or nil
        chosenVision = "off"
        message = "Selection not saved yet"
        draw()
      end,
    }))
  end
  local model = selectedModel()
  table.insert(rows, ui.label({ text = "Chat template" }))
  if model then
    for _, template in ipairs(model.templates) do
      local id = template.id
      table.insert(rows, ui.button({ key = "template-" .. model.id .. "-" .. id,
        text = template.label, selected = chosenTemplate == id, enabled = not locked, controlSize = "sm",
        onClick = function()
          chosenTemplate = id
          message = "Selection not saved yet"
          draw()
        end,
      }))
    end
  end
  if model and model.vision then
    table.insert(rows, ui.label({ text = "Vision (requires a restart to apply)" }))
    local buttons = {}
    for _, mode in ipairs({ "off", "on" }) do
      local id = mode
      table.insert(buttons, ui.button({ key = "vision-" .. id, text = id == "on" and "Vision on" or "Vision off",
        selected = chosenVision == id, enabled = not locked, controlSize = "sm",
        onClick = function()
          chosenVision = id
          message = "Selection not saved yet"
          draw()
        end,
      }))
    end
    table.insert(rows, ui.row({ gap = 8 }, buttons))
  end
  if chosenEngine == "ninfer" then
    table.insert(rows, ui.label({ text = "Context size (tokens; restart to apply)" }))
    table.insert(rows, ui.row({ gap = 8 }, {
      ui.slider({ key = "context-slider", min = contextLimits.min, max = contextLimits.max,
        step = contextLimits.step, value = chosenContext, flexGrow = 1,
        enabled = not locked, onChange = function(value)
          local number = tonumber(value)
          if number then
            chosenContext = math.floor(number / contextLimits.step + 0.5) * contextLimits.step
            contextValid = true
            contextInputVersion += 1
            message = "Selection not saved yet"
            draw()
          end
        end,
      }),
      ui.input({ key = "context-input-" .. tostring(contextInputVersion),
        value = tostring(chosenContext), width = 105, placeholder = "tokens",
        enabled = not locked, onChange = function(value)
          local number = tonumber(value)
          contextValid = number ~= nil and number == math.floor(number)
            and number >= contextLimits.min and number <= contextLimits.max
            and number % contextLimits.step == 0
          if contextValid then chosenContext = number end
          message = contextValid and "Selection not saved yet" or "Use 4,096–1,048,576 tokens in steps of 256"
          draw()
        end,
      }),
    }))
    table.insert(rows, ui.label({ text = "4K–1M • steps of 256 • above 262K exceeds the native window and may not fit VRAM" }))
    local weights, kv, other = vramEstimate(model)
    if weights then
      table.insert(rows, ui.label({ text = string.format(
        "Estimated VRAM: weights %.1f + KV %.1f + other %.1f = %.1f GiB",
        weights, kv, other, weights + kv + other) }))
      table.insert(rows, ui.label({ text = "Approximate NInfer allocation; other GPU apps and temporary Vision memory are extra" }))
    end
  end
  table.insert(rows, ui.row({ gap = 8 }, {
    ui.button({ text = "Save default", variant = "primary", controlSize = "sm",
      enabled = changed() and contextValid and not locked and selectedTemplate() ~= nil, onClick = "saveSelection" }),
    ui.button({ text = status.running and "Switch / restart to apply" or "Start saved server", controlSize = "sm",
      enabled = contextValid and not locked and not transitioning and saved ~= nil and not changed() and (not status.running or status.pending), onClick = "applySelection" }),
  }))
  table.insert(rows, ui.row({ gap = 8 }, {
    ui.button({ text = "Stop active server", controlSize = "sm", enabled = status.running and not locked and not transitioning, onClick = "stopServer" }),
    ui.button({ text = "Live logs", controlSize = "sm", onClick = "openLogs" }),
    ui.button({ text = "Refresh", controlSize = "sm", onClick = "refresh" }),
  }))
  if message ~= "" then table.insert(rows, ui.label({ text = message, maxLines = 3 })) end
  panel.render(ui.column({ padding = 12, gap = 6 }, rows))
end

local function refreshStatus()
  if statusPending then return end
  statusPending = true
  local accepted = noctalia.runAsync({ "python3", SCRIPT, "status" }, function(result)
    statusPending = false
    local info = result.exitCode == 0 and noctalia.json.decode(result.stdout or "") or nil
    if info then status = info
    else message = "Status failed: " .. noctalia.string.trim(result.stderr or "") end
    draw()
  end)
  if not accepted then statusPending = false end
end

function refresh()
  if loading or busy then return end
  loading = true
  local accepted = noctalia.runAsync({ "python3", SCRIPT, "list" }, function(result)
    loading = false
    local data = result.exitCode == 0 and noctalia.json.decode(result.stdout or "") or nil
    if not data then
      message = "Could not list profiles: " .. noctalia.string.trim(result.stderr or "")
      draw()
      return
    end
    models = data.models
    engines = data.engines
    defaults = data.defaults
    contextLimits = data.context or contextLimits
    saved = data.selected
    chosenEngine = saved.engine
    chosenModel = saved.model
    chosenTemplate = saved.template
    chosenVision = saved.vision or "off"
    chosenContext = saved.context or (defaults.ninfer and defaults.ninfer.context) or 115200
    contextValid = true
    contextInputVersion += 1
    refreshStatus()
    draw()
  end)
  if not accepted then loading = false end
end

function saveSelection()
  if busy or status.busy or not contextValid or selectedTemplate() == nil then return end
  busy = true
  draw()
  local command = { "python3", SCRIPT, "select", chosenEngine, chosenModel, chosenTemplate, chosenVision }
  if chosenEngine == "ninfer" then table.insert(command, tostring(chosenContext)) end
  local accepted = noctalia.runAsync(command, function(result)
    busy = false
    if result.exitCode == 0 then
      saved = { engine = chosenEngine, model = chosenModel, template = chosenTemplate,
        vision = chosenVision, context = chosenEngine == "ninfer" and chosenContext or nil }
      defaults[chosenEngine] = saved
      message = "Saved. Use Start / Switch to apply (interrupts requests)."
      refreshStatus()
    else
      message = "Save failed: " .. noctalia.string.trim(result.stderr or "")
      noctalia.notifyError("LLM selection", message)
    end
    draw()
  end)
  if not accepted then busy = false; message = "Could not launch save command"; draw() end
end

local function control(action)
  if busy or status.busy or status.state == "loading" or status.state == "stopping" then return end
  busy = true
  message = action == "stop" and "Stopping server…" or "Starting saved server; please wait for ready."
  draw()
  local accepted = noctalia.runAsync({ "python3", SCRIPT, action }, function(result)
    busy = false
    if result.exitCode == 0 then
      message = action == "stop" and "Server stopped." or "Server is starting. Restart Pi to load the new context and Vision setting."
    else
      message = "Control failed: " .. noctalia.string.trim(result.stderr or "")
      noctalia.notifyError("LLM control", message)
    end
    refreshStatus()
    draw()
  end)
  if not accepted then busy = false; message = "Could not launch control command"; draw() end
end

function applySelection()
  if saved == nil or changed() then return end
  control(status.running and "restart" or "start")
end

function stopServer() control("stop") end

function openLogs()
  local engine = status.active_engine or chosenEngine
  local service = engine == "ninfer" and "ninfer-local.service" or "vllm-local.service"
  noctalia.runInTerminal("journalctl --user -fu " .. service)
end

function update()
  noctalia.setUpdateInterval(1500)
  refreshStatus()
end

function onOpen()
  refresh()
  draw()
end

function onIpc(event, _payload)
  if event == "refresh" then refresh() end
end
