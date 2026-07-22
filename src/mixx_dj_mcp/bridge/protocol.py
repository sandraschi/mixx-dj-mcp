"""
Mixxx OSC Protocol Mapping (Makefile-style reference).

Mixxx uses OSC (Open Sound Control) for external control surfaces.
The OSC protocol maps directly to Mixxx's internal Control Objects (COs).

OUTGOING (Mixxx sends status updates to us on port 11118):
  /deck[N]/play             - Play state (1.0 = playing, 0.0 = stopped)
  /deck[N]/bpm              - Current BPM
  /deck[N]/rate             - Current rate/pitch adjustment (-1.0 to 1.0)
  /deck[N]/volume           - Channel volume (0.0-1.0)
  /deck[N]/pregain          - Channel pregain (0.0-5.0)
  /deck[N]/sync_enabled     - Sync lock state
  /deck[N]/loop_enabled     - Loop enabled state
  /deck[N]/keylock          - Keylock state
  /deck[N]/pfl              - Headphone cue (pre-fader listen) state
  /deck[N]/track_samples    - Track position in samples
  /deck[N]/track_samplerate - Track sample rate
  /crossfader               - Crossfader position

INCOMING (we send commands to Mixxx on port 11119):
  Deck Transport:
    /deck[N]/play           - Toggle play (1.0) or stop (0.0)
    /deck[N]/stop           - Stop playback (1.0)
    /deck[N]/LoadTrack      - Load track by file path (string)
    /deck[N]/cue_set        - Set cue at current position (1.0)
    /deck[N]/cue_play       - Play from cue point (1.0)
    /deck[N]/seek           - Seek to position in seconds (float)

  Tempo/Sync:
    /deck[N]/rate           - Set rate (-1.0 to 1.0)
    /deck[N]/rate_temp      - Temporary pitch bend (float seconds)
    /deck[N]/sync_enabled   - Toggle sync lock (1.0/0.0)
    /deck[N]/sync_leader    - Set as sync leader (1.0/0.0)
    /deck[N]/quantize       - Toggle quantize (1.0/0.0)

  Loops/Hotcues:
    /deck[N]/loop_enabled     - Toggle loop (1.0/0.0)
    /deck[N]/beatloop_[SIZE]  - Activate beat loop (SIZE = 1,2,4,8,16,32,64)
    /deck[N]/hotcue_[N]_activated - Activate hotcue (N = 1-8)

  EQ/Filter:
    /deck[N]/filterHigh    - High EQ knob (0.0-1.0)
    /deck[N]/filterMid     - Mid EQ knob (0.0-1.0)
    /deck[N]/filterLow     - Low EQ knob (0.0-1.0)
    /deck[N]/filterFilter  - Filter resonance (0.0-1.0)

  Channel:
    /deck[N]/pregain       - Pregain/trim (0.0-5.0)
    /deck[N]/volume        - Channel volume (0.0-1.0)
    /deck[N]/pfl           - Headphone cue on/off (1.0/0.0)

  Mixer:
    /crossfader            - Crossfader position (-1.0 to 1.0)
    /talkover              - Microphone talkover (1.0/0.0)
    /microphone/gain       - Microphone gain (0.0-1.0)

  Effects:
    /EffectRack[N]_EffectUnit[N]/enabled    - Toggle effect unit (1.0/0.0)
    /EffectRack[N]_EffectUnit[N]/chain_load - Load effect chain by name (string)
    /EffectRack[N]_EffectUnit[N]/chain_clear - Clear chain (1.0)
    /EffectRack[N]_EffectUnit[N]/meta       - Meta/param knob (0.0-1.0)
    /EffectRack[N]_EffectUnit[N]/parameter[N] - Specific parameter (0.0-1.0)

  Library:
    /library/search          - Search library (string query)
    /library/load_selected   - Load selected track to deck (float deck)
    /library/crate/[name]/select - Browse crate
    /library/playlist/[name]/select - Browse playlist
"""

OSC_IN_PORT = 11119
OSC_OUT_PORT = 11118

CO_ADDRESS_PATTERNS = {
    "play": "/deck/{deck}/play",
    "stop": "/deck/{deck}/stop",
    "load_track": "/deck/{deck}/LoadTrack",
    "cue_set": "/deck/{deck}/cue_set",
    "cue_play": "/deck/{deck}/cue_play",
    "seek": "/deck/{deck}/seek",
    "rate": "/deck/{deck}/rate",
    "rate_temp": "/deck/{deck}/rate_temp",
    "sync_enabled": "/deck/{deck}/sync_enabled",
    "sync_leader": "/deck/{deck}/sync_leader",
    "loop_enabled": "/deck/{deck}/loop_enabled",
    "beatloop": "/deck/{deck}/beatloop_{beats}",
    "hotcue": "/deck/{deck}/hotcue_{num}_activated",
    "pregain": "/deck/{deck}/pregain",
    "volume": "/deck/{deck}/volume",
    "pfl": "/deck/{deck}/pfl",
    "filter_high": "/deck/{deck}/filterHigh",
    "filter_mid": "/deck/{deck}/filterMid",
    "filter_low": "/deck/{deck}/filterLow",
    "crossfader": "/crossfader",
    "crossfader_curve": "/crossfader/curve",
    "talkover": "/talkover",
    "mic_gain": "/microphone/gain",
    "quantize": "/deck/{deck}/quantize",
    "keylock": "/deck/{deck}/keylock",
    "scratch": "/deck/{deck}/scratch",
    "effect_enabled": "/EffectRack{rack}_EffectUnit{unit}/enabled",
    "effect_chain_load": "/EffectRack{rack}_EffectUnit{unit}/chain_load",
    "effect_chain_clear": "/EffectRack{rack}_EffectUnit{unit}/chain_clear",
    "effect_meta": "/EffectRack{rack}_EffectUnit{unit}/meta",
    "effect_param": "/EffectRack{rack}_EffectUnit{unit}/parameter{param}",
    "library_search": "/library/search",
    "library_load_selected": "/library/load_selected",
}

DECK_OBSERVED_COS = [
    "play",
    "bpm",
    "rate",
    "volume",
    "pregain",
    "sync_enabled",
    "sync_leader",
    "loop_enabled",
    "keylock",
    "quantize",
    "pfl",
    "filterHigh",
    "filterMid",
    "filterLow",
    "track_samples",
    "track_samplerate",
]
