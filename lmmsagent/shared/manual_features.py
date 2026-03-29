from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class FeatureArea:
    id: str
    title: str
    manual_refs: List[str]
    keywords: List[str]
    automated_now: List[str] = field(default_factory=list)
    guided_now: List[str] = field(default_factory=list)
    deferred: List[str] = field(default_factory=list)
    example_prompts: List[str] = field(default_factory=list)


FEATURE_AREAS: List[FeatureArea] = [
    FeatureArea(
        id="main_window_navigation",
        title="Main Window and global navigation",
        manual_refs=[
            "LMMS Main Window",
            "Main Menu Bar",
            "Tool Bar",
            "The Side Bar",
        ],
        keywords=["main window", "toolbar", "side bar", "browser", "projects tab", "samples tab"],
        automated_now=[
            "open_tool (song editor, mixer, piano roll, automation editor, controller rack, project notes)",
            "list_tool_windows",
            "get_project_state",
        ],
        guided_now=[
            "drag-drop operations in sidebar",
            "window docking/arrangement",
        ],
        deferred=["typed API for browser tab selection and drag-drop"],
        example_prompts=["open mixer", "show song editor", "what windows are open"],
    ),
    FeatureArea(
        id="song_editor_tracks",
        title="Song Editor and track arrangement",
        manual_refs=[
            "The Song Editor window",
            "Working with tracks in Song Editor",
            "Context menus in Song Editor",
        ],
        keywords=["song editor", "track", "arrangement", "pattern track", "sample track", "automation track"],
        automated_now=[
            "create_track",
            "rename_track",
            "select_track",
            "mute_track",
            "solo_track",
            "create_pattern",
            "list_tracks",
            "get_track_details",
            "find_track_by_name",
        ],
        guided_now=[
            "timeline drag/resize/split/clone gestures",
            "right-click context menu item selection",
        ],
        deferred=["typed clip move/split/clone/edit operations"],
        example_prompts=["create instrument track", "rename track bass to Sub Bass", "solo drum track"],
    ),
    FeatureArea(
        id="piano_roll_composition",
        title="Piano Roll note editing and composition",
        manual_refs=[
            "The Piano Roll Editor",
            "Note Length",
            "Note Volume",
            "Note Panning",
            "Composing in the Piano Roll Editor",
        ],
        keywords=["piano roll", "notes", "melody", "chord", "arpeggio", "quantize"],
        automated_now=[
            "add_notes",
            "add_steps",
            "create_pattern",
            "open_tool (piano roll)",
        ],
        guided_now=[
            "precise note-drawing by mouse",
            "humanize/quantize workflows",
            "clipboard-heavy edits across bars",
        ],
        deferred=["full typed piano-roll note selection/move/resize APIs"],
        example_prompts=["open piano roll", "add notes C4 E4 G4", "create pattern Melody A"],
    ),
    FeatureArea(
        id="beat_bassline",
        title="Beat+Bassline rhythm workflow",
        manual_refs=[
            "The Beat+Bassline Editor",
            "Creating Beats",
            "Editing Beats",
            "The process flow for composing a rhythm",
        ],
        keywords=["beat", "bassline", "bb editor", "rhythm", "drums", "steps"],
        automated_now=[
            "create_track(type=sample)",
            "load_sample",
            "add_steps",
            "open_tool (bb editor if available in your build name map)",
        ],
        guided_now=[
            "step-grid editing nuances",
            "pattern-level rhythm design decisions",
        ],
        deferred=["native typed BB timeline and per-step accent/swing API"],
        example_prompts=["add rhythm", "create sample track", "load sample kick"],
    ),
    FeatureArea(
        id="instrument_plugins",
        title="Instrument plugins and presets",
        manual_refs=[
            "Instrument Sound controls",
            "The ENV/LFO tab",
            "The Func tab",
            "The FX tab",
            "The MIDI tab",
            "Appendix A: Instrument Plugins",
        ],
        keywords=["instrument", "plugin", "preset", "triple oscillator", "sf2", "zynaddsubfx"],
        automated_now=[
            "list_instruments",
            "resolve_plugin(type=instrument)",
            "load_instrument",
        ],
        guided_now=[
            "preset browser deep navigation",
            "fine-grained per-plugin envelope/LFO configuration",
        ],
        deferred=["typed per-plugin parameter schema and preset save/load"],
        example_prompts=["load instrument triple oscillator", "list instruments"],
    ),
    FeatureArea(
        id="fx_mixer_and_effects",
        title="FX Mixer and effect processing",
        manual_refs=[
            "The FX Mixer",
            "The channel structure",
            "The Effects Chain pane",
            "Appendix A: Effect Plugins",
            "Appendix E: Adding Special Effects",
        ],
        keywords=["mixer", "fx", "effect", "reverb", "delay", "eq", "sidechain"],
        automated_now=[
            "open_tool(mixer)",
            "list_effects",
            "add_effect",
            "remove_effect",
        ],
        guided_now=[
            "effect chain ordering fine-tuning",
            "side-chain routing in mixer",
            "A/B listening workflow",
        ],
        deferred=["set_effect_param implementation", "typed routing graph edits"],
        example_prompts=["show mixer", "add effect reverb", "remove effect compressor"],
    ),
    FeatureArea(
        id="automation_and_controllers",
        title="Automation Editor and Controller Rack",
        manual_refs=[
            "The Automation Editor",
            "Controller Rack",
            "LFO Controllers",
            "Peak Controller",
            "Appendix C: Editing the Automation Curve",
        ],
        keywords=["automation", "lfo", "controller", "peak controller", "curve"],
        automated_now=[
            "create_track(type=automation)",
            "create_snapshot",
            "undo_last_action",
            "rollback_to_snapshot",
        ],
        guided_now=[
            "curve drawing and shape editing",
            "controller-to-target linkage",
            "song-global automation attachment",
        ],
        deferred=["typed automation point edit API", "typed controller binding API"],
        example_prompts=["create automation track", "undo", "rollback to snapshot"],
    ),
    FeatureArea(
        id="import_and_samples",
        title="Import, samples, and audio assets",
        manual_refs=[
            "Working with sample tracks",
            "Appendix D: Working with samples",
            "Import workflows in practical chapters",
        ],
        keywords=["sample", "import", "audio", "wav", "mp3", "midi", "hydrogen"],
        automated_now=[
            "import_audio",
            "import_midi",
            "import_hydrogen",
            "search_project_audio",
            "resolve_sample",
            "load_sample",
        ],
        guided_now=[
            "manual sample trimming and pitch preparation",
            "browser-only sample audition workflows",
        ],
        deferred=["typed sample trim/normalize/slice API"],
        example_prompts=["import midi /path/file.mid", "load sample 808 kick"],
    ),
    FeatureArea(
        id="beginner_song_building",
        title="Beginner song-building playbooks",
        manual_refs=[
            "Editing and Composing Songs",
            "Composing a song from score sheet",
            "Adding Rhythm",
            "Adding Automation",
            "Exporting the Song",
        ],
        keywords=["beginner", "playbook", "compose from score", "add rhythm", "export song"],
        automated_now=[
            "planner playbooks for score/rhythm/automation/multiple instruments/samples/export",
            "guided interactive mode (confirm each step)",
        ],
        guided_now=[
            "manual confirmation checkpoints",
            "UI-only checks before export",
        ],
        deferred=["fully autonomous full-song generation without confirmation"],
        example_prompts=["beginner help", "compose from score sheet", "export song"],
    ),
    FeatureArea(
        id="shortcuts_and_power_use",
        title="Keyboard shortcuts and power-user workflow",
        manual_refs=["Appendix B: Keyboard shortcuts"],
        keywords=["shortcut", "hotkey", "keyboard", "workflow speed"],
        automated_now=["documented guidance only"],
        guided_now=["human-operated keyboard workflow in LMMS UI"],
        deferred=["typed shortcut simulation layer (not planned for v1)"],
        example_prompts=["beginner help", "show me shortcut-friendly flow"],
    ),
]


def list_feature_areas() -> List[FeatureArea]:
    return FEATURE_AREAS


def find_feature_areas(query: str, limit: int = 3) -> List[FeatureArea]:
    text = query.lower()
    ranked = []
    for area in FEATURE_AREAS:
        score = 0
        for kw in area.keywords:
            if kw in text:
                score += 3
        for ref in area.manual_refs:
            if ref.lower() in text:
                score += 2
        if area.id.replace("_", " ") in text:
            score += 2
        if score > 0:
            ranked.append((score, area))
    ranked.sort(key=lambda item: item[0], reverse=True)
    return [area for _, area in ranked[:limit]]


def render_feature_area(area: FeatureArea) -> str:
    lines = [
        f"Feature Area: {area.title}",
        f"Manual refs: {', '.join(area.manual_refs)}",
        "Automated now:",
    ]
    lines.extend([f"- {item}" for item in area.automated_now])
    lines.append("Guided/manual now:")
    lines.extend([f"- {item}" for item in area.guided_now])
    lines.append("Deferred:")
    lines.extend([f"- {item}" for item in area.deferred])
    lines.append("Try saying:")
    lines.extend([f"- {item}" for item in area.example_prompts])
    return "\n".join(lines)


def render_feature_catalog() -> str:
    lines = ["LMMS feature map from manual (0.4.12):"]
    for area in FEATURE_AREAS:
        lines.append(f"- {area.title} [{area.id}]")
    lines.append("Use commands like: manual map song editor, manual map automation, manual map samples")
    return "\n".join(lines)
