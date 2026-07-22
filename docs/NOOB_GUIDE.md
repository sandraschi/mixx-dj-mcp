# So You Want To Be a DJ

A guide for absolute beginners. If you've never touched DJ equipment in your life, start here.

## What Is DJing?

DJing means playing music for people and making it sound good. Your job is to:
1. Pick songs people want to hear
2. Play them one after another without awkward silence
3. Make the transition between songs sound smooth
4. Adjust the energy level for the crowd

That's it. Everything else (scratching, effects, beat juggling) is extra.

## What Hardware Do You Need?

**Minimum:** A laptop. That's it. Mixxx runs on any Windows, Mac, or Linux computer. You can DJ with your keyboard and mouse.

**Better:** A DJ controller (USB). These have jog wheels, faders, and buttons that make DJing feel like DJing. Mixxx supports 200+ controllers automatically.

**Best of all:** It's all free. Mixxx costs nothing. The controller costs whatever you want to spend.

## Step 1: Play One Song After Another

1. Open Mixxx
2. Find a song in your library and drag it to Deck 1
3. Press the Play button (or spacebar)
4. When the song is almost over, drag another song to Deck 2
5. Press play on Deck 2

Congratulations. You're a DJ. The guests at your party will hear music without gaps.

## Step 2: Beatmatch By Ear (Counting 1-2-3-4)

Every dance song has a beat. Listen to any song and count: **1-2-3-4, 1-2-3-4**. That's the beat.

When you want to mix from one song to another, match the tempos so they don't clash.

- Look at the BPM (Beats Per Minute) display — it tells you the speed
- If Deck 1 is at 128 BPM and Deck 2 is at 124 BPM, they'll sound wrong together
- Adjust Deck 2's speed slider until the BPM numbers match
- Hit Sync to do this automatically

## Step 3: Use mixx-dj-mcp With AI

This is the fun part. Instead of clicking buttons in Mixxx, you tell your AI assistant what to do. The AI talks to Mixx-DJ-MCP, which talks to Mixxx.

### How To Set It Up

1. Install Mixx-DJ-MCP (see `INSTALL.md`)
2. Configure Mixxx OSC (one time, takes 30 seconds)
3. Start the server
4. Open Claude Desktop, Cursor, or opencode
5. Start talking

### Example Prompts To Use

**For your birthday party:**

> "Play a happy upbeat song for my birthday party."

The AI searches your library, picks a fitting track, loads it to a deck, and plays it.

> "Make this song louder."

The AI adjusts the gain on the deck playing the song.

> "What song should I play next?"

The AI looks at what's playing, checks your library, and suggests the next track based on BPM, key, and genre.

> "Transition to the next track with a filter sweep."

The AI starts the next track and applies a smooth low-pass/high-pass filter transition.

> "Load the last Daft Punk album track to deck 2 and sync it."

The AI searches your library, loads it, and matches the tempo to whatever's playing.

**For building a set:**

> "Create a crate called 'Peak Time' with tech house between 124-128 BPM in D minor."

> "Sequence a 1-hour set from my 'Peak Time' crate for a Friday night gig."

> "Pick my best 5 vinyl records for a dark warehouse techno set."

**For learning:**

> "Explain what a beat loop is."

> "Show me how to use the crossfader."

> "What does sync do?"

## Safety Tips

- **Keep volume reasonable.** Your ears are more important than the party. If it hurts, turn it down.
- **Don't play explicit lyrics at kids' parties.** Unless the birthday kid's parents are cool with it. Ask first.
- **Watch the levels.** Mixxx shows a volume meter. If it's in the red (clipping), turn something down.
- **Save your ears.** Wear earplugs at loud clubs. Tinnitus (ringing in the ears) is permanent.

## Glossary

| Term | Meaning |
|------|---------|
| **BPM** | Beats Per Minute — how fast a song is. 120 is normal. 140 is fast. 90 is slow. |
| **Cue** | A marker that says "start playing from this point." Set a cue at the first beat of a song so you always start at the right place. |
| **Loop** | A section of the song that repeats over and over. Useful for extending a drum break or giving yourself more time to mix. |
| **Crossfader** | The slider in the middle of the mixer. Slide left to hear Deck 1, right for Deck 2, middle for both. |
| **Sync** | A button that automatically matches two songs' tempos. Press it and the BPMs line up. |
| **Deck** | A player that holds one song. Two decks = two songs at once. Four decks = four songs (advanced). |
| **Hot Cue** | A saved cue point you can jump to instantly. Set hot cue 1 at the chorus, hot cue 2 at the drop. |
| **EQ** | Equalizer — adjusts bass, mids, and treble. Turn down the bass on the outgoing song for a smoother transition. |
| **Gain** | Volume boost before the main fader. Makes quiet songs louder. |
| **Phrase** | A section of a song, usually 8 or 16 bars. DJs mix on phrase boundaries so the changes feel natural. |
| **Harmonic Mixing** | Playing songs in compatible musical keys so they don't clash. Camelot wheel makes this easy. |
| **Stems** | Separated parts of a song (vocals, drums, bass, other). Lets you remix on the fly — drop the vocals, bring in just the drums. |

## What To Do Next

1. Start Mixxx and play around for 10 minutes
2. Connect mixx-dj-mcp and ask your AI to do something simple
3. Try mixing two songs together manually (use a crossfader)
4. Read `docs/AI_TRANSITIONS.md` for creative transition ideas
5. Practice. Nobody was good on day one.

**Most important rule:** Have fun. It's called DJing, not DJ-work.
