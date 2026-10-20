-- Self-contained neovim config for the LSP hover smoke test.
--
-- Deliberately minimal: no plugins, no mason, just the `ty` language
-- server from the project's own .venv (installed via `make setup`).
-- Used by tests/integration/test_lsp_hover.py via `nvim -u <this file>`.

-- The hover runner script exports these before us; fall back to sane
-- defaults when run by hand from the repo root.
local root = vim.env.MIXEDTAPE_ROOT or vim.fn.getcwd()
local ty = vim.env.MIXEDTAPE_TY or (root .. "/.venv/bin/ty")

vim.lsp.config["ty"] = {
  cmd = { ty, "server" },
  root_dir = root,
  filetypes = { "python" },
}
vim.lsp.enable("ty")
