from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class PlaybookStep:
    title: str
    action: str
    args: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.9
    risk: str = "safe"
    requires_snapshot: bool = False


@dataclass
class Playbook:
    id: str
    title: str
    manual_section: str
    caution: str
    keywords: List[str]
    steps: List[PlaybookStep]


PLAYBOOKS: List[Playbook] = [
    Playbook(
        id="compose_from_score_sheet",
        title="Compose a melody from score sheet (beginner)",
        manual_section="Editing and Composing Songs -> Composing a song from score sheet",
        caution=(
            "Manual is from LMMS 0.4.12. Core workflow still applies, but UI labels and defaults may differ."
        ),
        keywords=["score", "sheet", "compose", "melody", "song from score", "beginner song"],
        steps=[
            PlaybookStep(
                title="Compatibility note",
                action="guide_note",
                args={
                    "note": (
                        "Validate defaults first: check tempo, time signature, and which tracks are auto-created in your LMMS build."
                    )
                },
                confidence=0.99,
            ),
            PlaybookStep(
                title="Set working tempo",
                action="set_tempo",
                args={"tempo": 140},
                confidence=0.96,
            ),
            PlaybookStep(
                title="Open Song Editor",
                action="open_tool",
                args={"name": "song editor", "kind": "window"},
                confidence=0.9,
            ),
            PlaybookStep(
                title="Create an instrument track",
                action="create_track",
                args={"type": "instrument"},
                confidence=0.93,
            ),
            PlaybookStep(
                title="Load Triple Oscillator",
                action="load_instrument",
                args={"plugin": "tripleoscillator"},
                confidence=0.92,
                requires_snapshot=True,
            ),
            PlaybookStep(
                title="Create first pattern clip",
                action="create_pattern",
                args={"tick": 0, "name": "Melody A"},
                confidence=0.86,
            ),
            PlaybookStep(
                title="Enter notes",
                action="guide_note",
                args={
                    "note": (
                        "Open Piano Roll and enter notes measure-by-measure. Use 1/4 note length first, then refine 1/8 notes."
                    )
                },
                confidence=0.94,
            ),
        ],
    ),
    Playbook(
        id="add_rhythm_bb",
        title="Add rhythm with Beat+Bassline workflow",
        manual_section="Beat+Bassline Editor -> process flow for composing a rhythm",
        caution="Beat+Bassline internals changed across LMMS versions; use this as guided workflow.",
        keywords=["rhythm", "drums", "beat", "bassline", "bb editor", "groove"],
        steps=[
            PlaybookStep(
                title="Open Beat+Bassline editor",
                action="guide_note",
                args={"note": "Open Beat+Bassline Editor from toolbar/window menu."},
                confidence=0.95,
            ),
            PlaybookStep(
                title="Create sample track for drums",
                action="create_track",
                args={"type": "sample", "name": "Drum One-shot"},
                confidence=0.9,
            ),
            PlaybookStep(
                title="Load drum sample",
                action="guide_note",
                args={
                    "note": (
                        "From My Samples -> Drums, audition sounds and load kick/snare/hat samples onto tracks."
                    )
                },
                confidence=0.9,
            ),
            PlaybookStep(
                title="Program 4/4 skeleton",
                action="guide_note",
                args={
                    "note": "Start with hits on steps 1, 5, 9, 13 (four beats), then add syncopation."
                },
                confidence=0.9,
            ),
        ],
    ),
    Playbook(
        id="automation_volume_contrast",
        title="Create beginner automation contrast",
        manual_section="Automation Editor + Song-global automation",
        caution="Song-global automation behavior differs by version; prefer automation track for reversible edits.",
        keywords=["automation", "volume automation", "fade", "lfo", "controller"],
        steps=[
            PlaybookStep(
                title="Snapshot before automation",
                action="create_snapshot",
                args={"label": "before_automation"},
                confidence=0.97,
            ),
            PlaybookStep(
                title="Create automation track",
                action="create_track",
                args={"type": "automation", "name": "Volume Automation"},
                confidence=0.92,
            ),
            PlaybookStep(
                title="Link target control",
                action="guide_note",
                args={
                    "note": (
                        "Ctrl-drag the target knob (for example track volume) onto automation track timeline to create linked automation clip."
                    )
                },
                confidence=0.92,
            ),
            PlaybookStep(
                title="Draw step curve",
                action="guide_note",
                args={
                    "note": "Draw low level for first 2 measures, higher level for later measures to create distance contrast."
                },
                confidence=0.9,
            ),
        ],
    ),
    Playbook(
        id="multiple_instruments_dialogue",
        title="Split melody across multiple instruments",
        manual_section="Further experimentation -> Using multiple instruments",
        caution="SF2 patch browsing is plugin-specific; keep the split workflow, adapt patch selection UI.",
        keywords=["multiple instruments", "layer", "sf2", "split melody", "orchestration"],
        steps=[
            PlaybookStep(
                title="Create secondary instrument track",
                action="create_track",
                args={"type": "instrument", "name": "Secondary Voice"},
                confidence=0.93,
            ),
            PlaybookStep(
                title="Load SF2 Player",
                action="load_instrument",
                args={"plugin": "sf2player", "track": "Secondary Voice"},
                confidence=0.86,
                requires_snapshot=True,
            ),
            PlaybookStep(
                title="Clone original clip",
                action="guide_note",
                args={
                    "note": (
                        "Copy original melody clip to Secondary Voice track, then delete non-relevant notes from each track."
                    )
                },
                confidence=0.9,
            ),
        ],
    ),
    Playbook(
        id="sample_workflow",
        title="Work with samples (melodic and percussion)",
        manual_section="Appendix D -> Working with samples",
        caution="Sample browser paths changed since 0.4.12; workflow remains valid.",
        keywords=["sample", "vocal chop", "one-shot", "percussion sample", "audio clip"],
        steps=[
            PlaybookStep(
                title="Create sample track",
                action="create_track",
                args={"type": "sample", "name": "Sample Source"},
                confidence=0.93,
            ),
            PlaybookStep(
                title="Resolve and load sample",
                action="guide_note",
                args={
                    "note": "Use load sample command with an actual file path, or browse My Samples and drag-drop onto track."
                },
                confidence=0.9,
            ),
            PlaybookStep(
                title="Choose melodic vs percussion usage",
                action="guide_note",
                args={
                    "note": (
                        "For melodic use, map pitch in instrument workflow; for percussion, keep one-shot timing in Song/BB editor."
                    )
                },
                confidence=0.88,
            ),
        ],
    ),
    Playbook(
        id="export_song",
        title="Export/render final song",
        manual_section="Editing and Composing Songs -> Exporting the Song",
        caution="Export codec options vary by build and installed codecs.",
        keywords=["export", "render", "bounce", "wav", "ogg", "mp3", "final mix"],
        steps=[
            PlaybookStep(
                title="Save project first",
                action="guide_note",
                args={"note": "Save project before export to avoid losing last-minute edits."},
                confidence=0.98,
            ),
            PlaybookStep(
                title="Open export dialog",
                action="guide_note",
                args={"note": "Use File -> Export (Ctrl+E), choose output format and destination."},
                confidence=0.98,
            ),
            PlaybookStep(
                title="Select quality settings",
                action="guide_note",
                args={
                    "note": (
                        "Pick sample rate/bitrate by balancing quality vs file size; validate with a quick re-import listen pass."
                    )
                },
                confidence=0.94,
            ),
        ],
    ),
    Playbook(
        id="edit_existing_song",
        title="Edit an existing project safely",
        manual_section="Editing and Composing Songs -> Editing an existing song",
        caution="Manual workflow is valid, but exact panel names can vary by LMMS version/theme.",
        keywords=["edit existing song", "edit project", "open project and edit", "revise song"],
        steps=[
            PlaybookStep(
                title="Create recovery snapshot",
                action="create_snapshot",
                args={"label": "before_existing_song_edit"},
                confidence=0.98,
            ),
            PlaybookStep(
                title="Inspect current project state",
                action="get_project_state",
                args={},
                confidence=0.97,
            ),
            PlaybookStep(
                title="Open Song Editor for arrangement pass",
                action="open_tool",
                args={"name": "song editor"},
                confidence=0.95,
            ),
            PlaybookStep(
                title="Open Mixer for level/effect pass",
                action="open_tool",
                args={"name": "mixer"},
                confidence=0.94,
            ),
            PlaybookStep(
                title="Manual pass checklist",
                action="guide_note",
                args={
                    "note": (
                        "Do one pass each for arrangement, sound design, and levels. After each pass, render 20-30s preview and compare."
                    )
                },
                confidence=0.93,
            ),
        ],
    ),
    Playbook(
        id="samples_melodic_instrument",
        title="Use a sample as a melodic instrument",
        manual_section="Appendix D -> Sample Used as a Melody Instrument",
        caution="Sample browser and sampler controls changed since 0.4.12; keep to same concept flow.",
        keywords=["sample melody", "sample instrument", "melodic sample", "sample as instrument"],
        steps=[
            PlaybookStep(
                title="Create instrument track for sampler",
                action="create_track",
                args={"type": "instrument", "name": "Sample Instrument"},
                confidence=0.93,
            ),
            PlaybookStep(
                title="Load AudioFileProcessor",
                action="load_instrument",
                args={"plugin": "audiofileprocessor", "track": "Sample Instrument"},
                confidence=0.88,
                requires_snapshot=True,
            ),
            PlaybookStep(
                title="Resolve and load source sample",
                action="guide_note",
                args={
                    "note": (
                        "Load your sample into the sampler, set a sensible root key, then test pitch across at least one octave."
                    )
                },
                confidence=0.9,
            ),
            PlaybookStep(
                title="Create pattern for melodic test",
                action="create_pattern",
                args={"tick": 0, "name": "Sample Melody Test"},
                confidence=0.85,
            ),
            PlaybookStep(
                title="Write a short phrase",
                action="guide_note",
                args={"note": "Open Piano Roll and write a 1-2 bar phrase to validate tuning and envelope behavior."},
                confidence=0.9,
            ),
        ],
    ),
    Playbook(
        id="samples_percussion_instrument",
        title="Use a sample as a percussion instrument",
        manual_section="Appendix D -> Sample Used as a Percussion Instrument",
        caution="Step-sequencer and sample-track UI differs by version; sequence remains valid.",
        keywords=["sample percussion", "drum sample", "one shot", "sample as drum"],
        steps=[
            PlaybookStep(
                title="Create drum sample track",
                action="create_track",
                args={"type": "sample", "name": "Percussion Sample"},
                confidence=0.94,
            ),
            PlaybookStep(
                title="Load percussion sample",
                action="guide_note",
                args={"note": "Load a short one-shot with clean transient (kick/snare/hat/clap)."},
                confidence=0.91,
            ),
            PlaybookStep(
                title="Program basic rhythm",
                action="add_steps",
                args={"track": "Percussion Sample", "steps": [0, 4, 8, 12]},
                confidence=0.82,
            ),
            PlaybookStep(
                title="Refine groove manually",
                action="guide_note",
                args={"note": "Adjust velocity/timing accents by ear to avoid robotic repetition."},
                confidence=0.88,
            ),
        ],
    ),
    Playbook(
        id="sidechain_through_mixer",
        title="Create side-chain style pumping through mixer",
        manual_section="Appendix E -> Side-chaining through FX-Mixer",
        caution="Routing UI and plugin choices differ by build; use this as controlled guided workflow.",
        keywords=["sidechain", "ducking", "pumping", "mixer routing"],
        steps=[
            PlaybookStep(
                title="Create safety snapshot",
                action="create_snapshot",
                args={"label": "before_sidechain"},
                confidence=0.98,
            ),
            PlaybookStep(
                title="Open mixer",
                action="open_tool",
                args={"name": "mixer"},
                confidence=0.97,
            ),
            PlaybookStep(
                title="Insert controller-capable effect",
                action="guide_note",
                args={
                    "note": (
                        "Insert a gain/volume-capable effect on target channel, then prepare a controller source for ducking signal."
                    )
                },
                confidence=0.86,
            ),
            PlaybookStep(
                title="Link controller to volume",
                action="guide_note",
                args={"note": "Link controller output to target gain/volume parameter and tune depth/release by ear."},
                confidence=0.88,
            ),
            PlaybookStep(
                title="Rollback path reminder",
                action="guide_note",
                args={"note": "If routing gets messy, run rollback_to_snapshot using the last snapshot id."},
                confidence=0.99,
            ),
        ],
    ),
    Playbook(
        id="lfo_controller_modulation",
        title="Apply LFO controller modulation",
        manual_section="Controller Rack -> LFO Controllers",
        caution="Controller rack visuals changed since 0.4.12; concept and signal flow remain same.",
        keywords=["lfo controller", "lfo modulation", "controller rack", "modulate knob"],
        steps=[
            PlaybookStep(
                title="Open controller rack",
                action="open_tool",
                args={"name": "controller rack"},
                confidence=0.95,
            ),
            PlaybookStep(
                title="Prepare target track",
                action="guide_note",
                args={"note": "Pick one target control first (filter cutoff, pan, or volume) to keep modulation predictable."},
                confidence=0.92,
            ),
            PlaybookStep(
                title="Add LFO and bind target",
                action="guide_note",
                args={"note": "Create LFO controller, link it to target control, then tune speed/depth in small increments."},
                confidence=0.9,
            ),
            PlaybookStep(
                title="Snapshot tuned state",
                action="create_snapshot",
                args={"label": "after_lfo_modulation"},
                confidence=0.95,
            ),
        ],
    ),
]


def list_playbooks() -> List[Dict[str, str]]:
    return [
        {
            "id": pb.id,
            "title": pb.title,
            "manual_section": pb.manual_section,
            "caution": pb.caution,
        }
        for pb in PLAYBOOKS
    ]


def find_playbook_for_goal(goal: str) -> Optional[Playbook]:
    text = goal.lower()
    best: Optional[Playbook] = None
    best_score = 0
    for playbook in PLAYBOOKS:
        score = sum(1 for kw in playbook.keywords if kw in text)
        if score > best_score:
            best = playbook
            best_score = score
    return best
