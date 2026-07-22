# AI Transitions

Mixx-DJ-MCP includes an AI-powered transition engine that suggests and applies creative transitions between decks. It uses a local LLM (Ollama) to analyze loaded track metadata and recommend the best-sounding transition for the moment.

## How It Works

1. You have tracks loaded on two decks (say Deck 1 and Deck 2)
2. Call `mixx_transition(operation="suggest", deck_a=1, deck_b=2)`
3. The server reads BPM, key, artist, and title from Mixxx's OSC feedback
4. Sends this to Ollama (`llama3.2:3b`) which picks the best transition
5. Apply with `mixx_transition(operation="apply", effect="filter_sweep")`

## Available Effects

| Effect | Description | Best For |
|--------|-------------|----------|
| `echo_out` | Progressive echo/delay on outgoing track | Smooth, atmospheric transitions |
| `filter_sweep` | Low-pass on outgoing, high-pass on incoming | Most genres — the workhorse transition |
| `stem_swap` | Drop vocals from A, bring instrumental of B | Vocal tracks — sounds like a remix |
| `hard_cut` | Instant switch, club style | High-energy, quick BPM changes |
| `spin_back` | Outgoing spins down like vinyl brake | Retro/hip-hop sets |
| `flanger` | Flanger sweep across both decks | Electronic, psychedelic |
| `reverb_kill` | Reverb + delay on outgoing, then kill | Dramatic, big-room drops |
| `long_blend` | Slow EQ fade over 16-32 bars | Deep house, ambient, chill |

## Suggested Prompts

These are prompts you can give your AI assistant to get creative transitions:

### Simple Requests

> "Transition from deck 1 to deck 2 with a filter sweep."

> "Do an echo out on deck 2 in 8 beats."

> "Hard cut to deck 3 at the drop."

### Style-Based Requests

> "Suggest a transition between what's playing on deck 1 and what's cued on deck 2."

> "I'm playing a dark techno set. What transition fits between these two tracks?"

> "We're at peak time — hit me with a reverb kill transition."

### AI Suggestions

> "Listen to both tracks and tell me which transition you'd use."

> "Auto-choose the best transition for these two tracks and apply it."

The LLM considers:
- BPM difference (small gap = blend, large gap = hard cut)
- Key compatibility (harmonic keys = long blend, dissonant = echo out)
- Genre affinity (similar genres = stem_swap, different = filter_sweep)
- Energy level (both high = hard_cut, one low = long_blend)

## Full Workflow Example

```
User: "Load tech house track on deck 2 and suggest a transition"

AI:  mixx_library(operation="search", query="tech house")
     mixx_library(operation="load_selected", deck=2)
     mixx_transition(operation="suggest", deck_a=1, deck_b=2)
     → "Suggested: filter_sweep — Low-pass filter on outgoing,
        high-pass on incoming. Great for matching tech house energy."

User: "Do it"

AI:  mixx_transition(operation="apply", effect="filter_sweep", deck_a=1, deck_b=2)
     mixx_deck(operation="sync_enable", deck=2, enable=True)
     → "Applied filter_sweep from deck 1 to deck 2. Deck 2 synced."
```

## Auto-Crossfader Mode

Enable the AI-assisted crossfader for automated transition handling:

```python
mixx_transition(operation="auto_crossfader", enable=True)
```

When enabled, the server watches deck states and applies appropriate transitions as tracks approach their end.

## Prerequisites

- Ollama running at `http://localhost:11434`
- Model: `llama3.2:3b` (pull with `ollama pull llama3.2:3b`)
- Without Ollama: falls back to `filter_sweep` as default
