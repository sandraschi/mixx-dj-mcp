# Mixx-DJ-MCP — Community Announcement (for Mixxx Zulip / Forums)

**Title**: Mixx-DJ-MCP: Control Mixxx from Your AI Coding Assistant

**Body**:

Hey Mixxx community! I built something I think some of you might find useful.

**Mixx-DJ-MCP** is a free/open-source server that lets you control Mixxx through natural language — from Claude Code, Cursor, opencode, or any MCP-compatible AI assistant.

What this means in practice:
- "Load the last Daft Punk track onto deck 2 and sync it"
- "Set an 8-bar loop on deck 1 and bring in the next track"
- "Search my library for tech house around 128 BPM"
- "Turn off the low EQ on deck 3 and add reverb to deck 1"

It works through Mixxx's built-in **OSC control surface** (Preferences → MIDI/OSC). No plugins, no patches to Mixxx itself — just configure the OSC ports and go.

**What's included:**
- 40+ DJ operations (transport, hot cues, loops, effects, EQ, sync, library)
- A full web dashboard (React/Vite) for visual deck monitoring
- Ready-to-go Tauri desktop app build
- MCPB package for Claude Desktop

**Stack:** FastMCP 3.4+ / Python / OSC / React 19 / Tauri 2.0
**License:** MIT
**GitHub:** https://github.com/sandraschi/mixx-dj-mcp

This is v0.1.0 — very fresh. I'd love feedback, bug reports, and feature requests. The OSC protocol is stable (Mixxx's built-in), so the core should work reliably. The webapp and Tauri packaging are scaffolding waiting for community input on what matters most.

Would anyone be interested in testing this with their setup? I'm especially curious about:
- Controller mapping combinations (MIDI + OSC + MCP)
- Latency with real-time OSC control
- Missing operations that would make this genuinely useful for live use

Happy to walk through setup on Zulip if anyone wants to try it.
