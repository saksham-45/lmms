# LMMS Manual Feature Coverage (0.4.12 -> Current Agent)

Source PDF: `/Users/saksham/Downloads/lmms-manual-0.4.12.pdf`  
TOC extraction: `/Users/saksham/grp/docs/lmmsagent/lmms/lmmsagent/docs/MANUAL_TOC_EXTRACTED.md` (192 entries)

This is the full mapping layer for "what LMMS can do" from the manual, and where each capability lands in the agent stack.

## Coverage method

- Parsed full manual TOC and indexed all chapter families.
- Mapped each feature family into one of:
  - **Automated now** (typed AgentControl tool calls)
  - **Guided now** (agent gives step-by-step instructions with confirmations)
  - **Deferred** (needs new typed LMMS API surface)
- Added runtime feature map in code:
  - `/Users/saksham/grp/docs/lmmsagent/lmms/lmmsagent/shared/manual_features.py`

## Feature-area mapping

| Feature area | Manual sections | Automated now | Guided now | Deferred |
|---|---|---|---|---|
| Main Window + Navigation | Main Window, Menu/Toolbar, Sidebar tabs | `open_tool`, `list_tool_windows`, `get_project_state` | browser tab workflows, drag-drop | typed sidebar navigation API |
| Song Editor + Tracks | Song Editor, track workflows, context menus | `create_track`, `rename_track`, `select_track`, `mute_track`, `solo_track`, `create_pattern`, `list_tracks` | clip timeline gestures | clip move/split/clone typed API |
| Piano Roll | Piano Roll interface and composing | `open_tool`, `create_pattern`, `add_notes`, `add_steps` | precise note editing workflow | full typed note selection/edit API |
| Beat+Bassline | BB Editor, rhythm process flow | `create_track(type=sample)`, `load_sample`, `add_steps` | groove design and per-step feel | native typed BB timeline API |
| Instruments + Presets | Instrument window, ENV/LFO, Func, MIDI, plugin appendix | `list_instruments`, `resolve_plugin`, `load_instrument` | deep preset/program editing | typed per-plugin parameter schema |
| FX Mixer + Effects | FX Mixer, effect chain, effects appendix | `open_tool(mixer)`, `list_effects`, `add_effect`, `remove_effect` | chain tuning, side-chain procedure | `set_effect_param`, typed routing graph |
| Automation + Controllers | Automation editor, controller rack, LFO/Peak controller | `create_track(type=automation)`, snapshots/undo/rollback | curve shaping and controller linking | typed automation point API |
| Import + Samples | sample tracks, sample appendix, import workflows | `import_audio`, `import_midi`, `import_hydrogen`, `search_project_audio`, `resolve_sample`, `load_sample` | sample preparation and audition flow | typed trim/slice/normalize APIs |
| Beginner Song Building | compose from score, rhythm, automation, export | playbooks + guided mode over typed tools | manual checkpoints and confirms | autonomous section generation without confirmation |
| Shortcuts + Power-use | keyboard shortcuts appendix | guidance/documentation | human-driven hotkey workflow | shortcut simulation layer |

## Runtime commands added for manual mapping

Use these in text agent to get manual-aware capability responses:

- `manual map`
- `manual map song editor`
- `manual map automation`
- `manual map samples`
- `manual map mixer`
- `manual map piano roll`

The planner now returns capability map notes and recommended prompts per matched section.

## Beginner-first behavior

- If a requested operation is risky/underspecified, the planner asks for clarification.
- Guided mode (`--guided`) can require confirmation before each step.
- Manual version drift is always acknowledged (0.4.12 is old).

## Current gap summary (high priority)

1. Implement `set_effect_param` in AgentControl for real plugin tuning.  
2. Add typed automation point editing (create/move/delete points).  
3. Add typed clip operations in Song Editor (move/split/clone).  
4. Add typed BB Editor grid APIs (step accents/swing/timing).
