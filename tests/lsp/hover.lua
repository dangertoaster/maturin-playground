-- Headless hover runner: opens tests/lsp/probe.py with ty attached and
-- prints the hover documentation for each probed symbol.
--
-- Not meant to be run directly; driven by
-- tests/integration/test_lsp_hover.py, which sets MIXEDTAPE_ROOT /
-- MIXEDTAPE_TY and supplies the config via `nvim -u`. Manual run:
--   MIXEDTAPE_ROOT=$PWD nvim --headless -u tests/lsp/nvim/init.lua -l tests/lsp/hover.lua
--
-- Output protocol, one record per symbol:
--   === <name>
--   <hover text, possibly multi-line>
--   === END
-- Exits 0 iff every symbol produced a hover.

local root = vim.env.MIXEDTAPE_ROOT or vim.fn.getcwd()
local probe = root .. "/tests/lsp/probe.py"

-- (0-indexed line, 0-indexed col) positions of symbols in probe.py,
-- targeting the import lines where symbol positions are unambiguous.
local targets = {
  { line = 2, col = 35, name = "levenshtein" },
  { line = 2, col = 50, name = "shingle" },
  { line = 3, col = 30, name = "parse_selector" },
  { line = 3, col = 47, name = "matches" },
  { line = 4, col = 32, name = "sha256_data" },
  { line = 4, col = 47, name = "streaming" },
  { line = 5, col = 45, name = "ChunkedHasher (public deep import)" },
}
local results, done = {}, false

vim.api.nvim_create_autocmd("LspAttach", {
  callback = function(ev)
    local client = vim.lsp.get_client_by_id(ev.data.client_id)
    if client.name ~= "ty" then
      return
    end
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
          results[t.name] = nil
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
-- the minimal config doesn't enable filetype detection; set it manually
-- so the ty config's `filetypes` matches and the server attaches
vim.bo.filetype = "python"
vim.api.nvim_exec_autocmds("FileType", { buffer = 0 })

local deadline = vim.uv.now() + 60000
while not done and vim.uv.now() < deadline do
  vim.wait(300, function() return done end, 50)
end

local failures = 0
for _, t in ipairs(targets) do
  print("=== " .. t.name)
  if results[t.name] then
    print(results[t.name])
  else
    failures = failures + 1
    print("<no hover>")
  end
  print("=== END")
end
os.exit(failures == 0 and 0 or 1)
