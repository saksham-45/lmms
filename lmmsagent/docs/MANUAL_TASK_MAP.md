# LMMS 0.4.12 Manual Task Map (Compatibility-Aware)

Source used: `/Users/saksham/Downloads/lmms-manual-0.4.12.pdf`

For full chapter-family coverage mapped from the manual TOC, see:
`/Users/saksham/grp/docs/lmmsagent/lmms/lmmsagent/docs/MANUAL_FEATURE_COVERAGE.md`

This map transfers beginner workflows from the old manual into the current agent stack while marking what is:

- **Automated now** via typed AgentControl tools.
- **Guided/manual** in current build (UI step still needed).
- **Deferred** for future implementation.

## 1) Compose from score sheet

Manual section: `Editing and Composing Songs -> Composing a song from score sheet`

- Automated now:
  - set tempo
  - create instrument track
  - load Triple Oscillator
  - create pattern clip
- Guided/manual:
  - entering exact notes from score in Piano Roll
  - detailed quantization/octave editing
- Deferred:
  - score-sheet parsing into note events

## 2) Add rhythm in Beat+Bassline workflow

Manual section: `Beat+Bassline Editor -> process flow for composing a rhythm`

- Automated now:
  - create sample track
- Guided/manual:
  - choosing drum samples in browser
  - step programming in BB editor timeline
- Deferred:
  - direct BB timeline tool APIs

## 3) Automation contrast (distance/loudness)

Manual section: `Adding Automation`

- Automated now:
  - create snapshot
  - create automation track
- Guided/manual:
  - ctrl-drag knob linking
  - draw automation curve shape in automation editor
- Deferred:
  - typed automation-curve editing tool

## 4) Multiple instruments / dialogue split

Manual section: `Further experimentation -> Using multiple instruments`

- Automated now:
  - create secondary instrument track
  - load SF2 Player (if available)
- Guided/manual:
  - select SF2 patch
  - clone clip and prune note ranges
- Deferred:
  - clip clone/cut operations as typed tools

## 5) Working with samples

Manual section: `Appendix D -> Working with samples`

- Automated now:
  - create sample track
  - load sample by path (when provided)
- Guided/manual:
  - classify usage as melodic vs percussion
  - sample prep and browser navigation
- Deferred:
  - automatic pitched-sample instrument pipeline

## 6) Export song

Manual section: `Exporting the Song`

- Automated now:
  - guidance only
- Guided/manual:
  - export dialog flow (Ctrl+E)
  - choose sample-rate/bitrate/codec based on destination
- Deferred:
  - typed export/render API

## Safety policy applied

- Snapshots required before risky write operations in guided workflows.
- `undo_last_action` and `rollback_to_snapshot` available.
- Old manual assumptions are treated as advisory, not authoritative.

## Practical use

These workflows are exposed as **beginner playbooks** through planner matching. Ask with prompts like:

- `beginner help`
- `compose from score sheet`
- `add rhythm`
- `volume automation`
- `multiple instruments`
- `working with samples`
- `export song`
- `edit existing song`
- `sample as melodic instrument`
- `sample as percussion instrument`
- `sidechain through mixer`
- `lfo controller modulation`
