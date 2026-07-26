# Build Log — mixx-dj-mcp

## Build 2026-07-26-1 — Help page (docs pass, no release)

**Status**: ✅ web_sota build OK (source only; dist gitignored)

| Step | Result |
|---|---|
| `npm run build` in `web_sota` | Pass — Help.tsx, tsc + vite |
| Commits | `64e8995` on `master` |

**Notes:**
- New route `/help` (NDI primer tab for users who never heard of NDI)
- NSIS installer not rebuilt — run full `build-native` when cutting 0.2.1 release
- Cross-repo docs: mixxxxx `e429e2aaf9` (NDI.md, SKINS.md, NOTES)

---

## Build 2026-07-24-1 — NSIS installer (v0.1.0)

**Status**: ✅ SUCCESS

## Build 2026-07-25-1 — NSIS + MCPB (v0.2.0)

**Status**: ✅ SUCCESS

**Artifacts**:
- NSIS installer: `Mixx-DJ-MCP_0.2.0_x64-setup.exe` (115.5 MB)
- MCPB bundle: `mixx-dj-mcp.mcpb` (15.2 KB)
- Release: https://github.com/sandraschi/mixx-dj-mcp/releases/tag/v0.2.0

### Artifacts

| File | Size | Path |
|------|------|------|
| NSIS installer | 106.1 MB | `native/target/release/bundle/nsis/Mixx-DJ-MCP_0.1.0_x64-setup.exe` |
| Backend (PyInstaller) | 103.4 MB | `dist/mixx-dj-mcp-backend.exe` |
| MCPB bundle | 15.5 KB | `dist/mixx-dj-mcp.mcpb` |

### Pipeline

| Step | Duration | Result |
|------|----------|--------|
| Frontend build (web_sota) | ~5s | ✅ Pass |
| PyInstaller backend | ~3 min | ✅ Pass (frozen binary smoke test PASSED) |
| Tauri Rust build | ~1 min 40s | ✅ Pass |
| NSIS makensis | ~30s | ✅ Pass |

### Build gates

| Gate | Value |
|------|-------|
| API_BASE port verification | 11116 ✅ |
| TypeScript lint (tsc --noEmit) | ✅ Pass |
| PyInstaller >= 5 MB | 103.4 MB ✅ |
| NSIS >= 1 MB | 106.1 MB ✅ |

### Notes

- First NSIS build for mixx-dj-mcp
- Icons generated from `app-icon.svg` placeholder
- `tauri.conf.json` `beforeBuildCommand` removed to prevent recursive build loop
- `run_server.py` fixed to check `MIXX_MCP_PORT` env var (was only checking `MCP_PORT`, causing Tauri-spawned frozen exe to fall to stdio mode)
- `build.ps1` fixed to use `bun x tsc` instead of `npx tsc` for TypeScript gate
- `justfile` `build-native` recipe fixed to call `build.ps1` instead of bare `npx tauri build`
