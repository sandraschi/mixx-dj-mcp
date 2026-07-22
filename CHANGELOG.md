# Changelog

## 0.1.0 (2026-07-22)

- OSC bridge to Mixxx (python-osc, ports 11118/11119)
- Deck control (17 ops): play_pause, stop, load, cue_set, cue_play, loop_activate, loop_beat, beatloop, rate_set, rate_temp, sync_enable, sync_leader, seek, scratch, hotcue_activate, quantize, keylock
- Library (8 ops): search, browse_crate, browse_playlist, load_selected, get_track_info, get_bpm, get_key, get_replay_gain
- Effects (7 ops): list_effects, chain_load, chain_clear, parameter_set, meta_set, quick_effect_set, effect_enable
- Mixer (8 ops): crossfader_set, crossfader_curve, gain_set, eq_set, volume_set, headphone_cue, talkover, mic_gain
- 3 Prefab UI cards: show_deck_status_card, show_mixer_status_card, show_library_status_card
- FastAPI REST API: /api/health, /api/deck/status, /api/settings, /api/v1/diagnostics
- CORS configured for Tauri WebView + Tailscale + LAN
- 41 pytest tests (bridge, deck, effects, mixer)
- SOTA webapp: React 19 / Vite 6 / Tailwind 4 / Zustand 5 / Framer Motion / Lucide (7 pages)
- Tauri 2.0 NSIS build pipeline (native/)
- MCPB packaging (mcpb/)
- CI via GitHub Actions (.github/workflows/ci.yml)
- Playwright E2E + CUA-NSIS smoke test
- llms.txt + llms-full.txt documentation
- Session context injection (.claude-plugin, .cursorrules)

### Documentation updates (2026-07-22)

- README updated with accurate tool counts, operation names, port table, and working command examples
- CHANGELOG corrected to reflect actual v0.1.0 shipping state
- llms-full.txt rewritten with real tool signatures, OSC address mappings from protocol.py, and verified config
- PRD.md updated: v0.1.0 marked as shipped, v0.2 roadmap defined
