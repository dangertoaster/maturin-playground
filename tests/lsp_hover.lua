-- Headless LSP probe: verifies that docstrings on mixedtape's
-- Rust-native symbols render via a Python language server (ty).
--
-- Requires: neovim 0.11+ and the `ty` language server on PATH
-- (or at ~/.local/share/nvim/mason/bin/ty).
--
-- Run from the repository root:
--   nvim --headless -u NONE -l tests/lsp_hover.lua
--
-- Exits 0 and prints the hover documentation for each probed symbol;
-- exits 1 if the server never attaches or any hover times out.

local probe = vim.fn.getcwd() .. "/tests/lsp_probe.py"
local ty = vim.fn.exepath("ty")
if ty == "" then
  ty = vim.fn.expand("~/.local/share/nvim/mason/bin/ty")
end

-- (0-indexed line, 0-indexed col) positions of symbols in lsp_probe.py,
-- targeting the import lines where symbol positions are unambiguous.
local targets = {
  { line = 2, col = 35, name = "levenshtein" },
  { line = 2, col = 50, name = "shingle" },
  { line = 3, col = 30, name = "parse_selector" },
  { line = 3, col = 47, name = "matches" },
  { line = 4, col = 32, name = "sha256_data" },
  { line = 5, col = 45, name = "ChunkedHasher (public deep import)" },
  { line = 4, col = 47, name = "streaming (public submodule)" },
}
local results, done = {}, false

-- ty auto-discovers the project .venv; no explicit settings needed.
vim.lsp.config["ty"] = {
  cmd = { ty, "server" },
  root_dir = vim.fn.getcwd(),
  filetypes = { "python" },
}
vim.lsp.enable("ty")

vim.api.nvim_create_autocmd("LspAttach", {
  callback = function(ev)
    local client = vim.lsp.get_client_by_id(ev.data.client_id)
    local function hover(i)
      if i > #targets then
        done = true
        return
      end
      local t = targets[i]
      client:request("textDocument/hover", {
        textDocument = { uri = vim.uri_from_fname(probe) },
        position = { line = t.line, character = t.col },
      }, function(err, res)
        if err or not res or not res.contents then
          results[t.name] = "<no hover: " .. tostring(err) .. ">"
        else
          local c = res.contents
          results[t.name] = type(c) == "table" and (c.value or vim.inspect(c)) or tostring(c)
        end
        hover(i + 1)
      end, ev.buf)
    end
    -- give the server a moment to index before the first request
    vim.defer_fn(function() hover(1) end, 6000)
  end,
})

vim.cmd.edit(probe)
-- `-u NONE` disables filetype detection; set it manually so the
-- ty config's `filetypes` matches and the server attaches.
vim.bo.filetype = "python"
vim.api.nvim_exec_autocmds("FileType", { buffer = 0 })

local deadline = vim.uv.now() + 60000
while not done and vim.uv.now() < deadline do
  vim.wait(300, function() return done end, 50)
end

for _, t in ipairs(targets) do
  print("=== " .. t.name .. " ===")
  print(results[t.name] or "<timed out>")
end
os.exit(done and 0 or 1)
