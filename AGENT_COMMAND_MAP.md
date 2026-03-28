# LMMS Agent Command Map

This file maps natural-language agent commands to the LMMS source paths that
can execute them.

It is based on:

- `README.md`
- `doc/wiki/LMMS-Architecture.md`
- `doc/wiki/Plugin-development.md`
- `src/gui/MainWindow.cpp`
- `src/core/Track.cpp`
- `src/tracks/InstrumentTrack.cpp`
- `src/tracks/SampleTrack.cpp`
- `src/core/ImportFilter.cpp`
- `src/gui/FileBrowser.cpp`
- `src/gui/instrument/InstrumentTrackWindow.cpp`
- `src/core/EffectChain.cpp`
- `src/gui/PluginBrowser.cpp`
- `plugins/AgentControl/*`


## 1. Commands that are valid now

These already have a real code path in `plugins/AgentControl`.

### `add 808`
### `add kick`

Agent behavior:

- Create a new `SampleTrack`
- Load a kick sample
- Add clips at steps `1, 5, 9, 13`

Source hooks:

- `plugins/AgentControl/AgentControl.cpp`
- `src/tracks/SampleTrack.cpp`
- `src/core/Track.cpp`


### `import <filename>`

Agent behavior:

- Resolve the file in Downloads
- Create a new `SampleTrack`
- Create one `SampleClip`
- Call `setSampleFile(...)`

Source hooks:

- `plugins/AgentControl/AgentControl.cpp`
- `src/core/SampleClip.cpp`
- `src/tracks/SampleTrack.cpp`


## 2. Commands that are straightforward next

These map cleanly onto existing LMMS APIs and should be implemented next.

### `new project`

LMMS action:

- `Engine::getSong()->createNewProject()`

Source:

- `src/gui/MainWindow.cpp`


### `open project`

LMMS action:

- `Song::loadProject(...)`

Notes:

- Current UI path uses a dialog. Agent version should accept a path.

Source:

- `src/gui/MainWindow.cpp`


### `save project`
### `save project as <path>`

LMMS action:

- `Song::guiSaveProject()`
- `Song::guiSaveProjectAs(...)`

Source:

- `src/gui/MainWindow.cpp`


### `show song editor`
### `show pattern editor`
### `show piano roll`
### `show automation editor`
### `show mixer`
### `show controller rack`
### `show project notes`
### `show microtuner`

LMMS action:

- Existing main-window slots already exist for these windows.

Source:

- `src/gui/MainWindow.cpp`

Mapped slots:

- `toggleSongEditorWin()`
- `togglePatternEditorWin()`
- `togglePianoRollWin()`
- `toggleAutomationEditorWin()`
- `toggleMixerWin()`
- `toggleControllerRack()`
- `toggleProjectNotesWin()`
- `toggleMicrotunerWin()`


### `show tool <name>`

LMMS action:

- Tool plugins are loaded into `MainWindow::m_tools`
- `showTool(QAction*)` displays the selected tool view

Source:

- `src/gui/MainWindow.cpp`
- `src/core/ToolPlugin.cpp`

Examples:

- `show tool agent control`
- `show tool tap tempo`
- `show tool ladspa browser`


### `import midi <file>`
### `import hydrogen <file>`

LMMS action:

- `ImportFilter::import(file, Engine::getSong())`

Notes:

- LMMS already has import plugins for MIDI and Hydrogen.

Source:

- `src/core/ImportFilter.cpp`
- `plugins/MidiImport/MidiImport.cpp`
- `plugins/HydrogenImport/HydrogenImport.cpp`
- `src/gui/MainWindow.cpp`


### `new sample track`
### `new instrument track`
### `new automation track`

LMMS action:

- `Track::create(Track::Type::Sample, song)`
- `Track::create(Track::Type::Instrument, song)`
- `Track::create(Track::Type::Automation, song)`

Source:

- `src/core/Track.cpp`


### `load instrument <plugin>`
### `set instrument <plugin>`

LMMS action:

- Create or target an `InstrumentTrack`
- Call `InstrumentTrack::loadInstrument(pluginName, ...)`

Source:

- `src/tracks/InstrumentTrack.cpp`
- `include/InstrumentTrack.h`

Good first targets:

- `kicker`
- `tripleoscillator`
- `slicert`
- `sf2player`
- `patman`


### `open slicer`
### `send <sample> to slicer`

LMMS action:

- Existing file-browser code already creates an instrument track,
  loads `slicert`, and then calls `instrument()->loadFile(...)`

Source:

- `src/gui/FileBrowser.cpp`


### `load sample into current instrument`
### `load preset file into current instrument`

LMMS action:

- `instrument()->loadFile(...)`
- `replaceInstrument(DataFile(...))`

Source:

- `src/gui/instrument/InstrumentTrackWindow.cpp`


### `add effect <effect>`
### `remove effect <effect>`

LMMS action:

- Instantiate an `Effect`
- Append it to `EffectChain`

Source:

- `src/core/EffectChain.cpp`
- `src/gui/EffectRackView.cpp`
- `src/gui/modals/EffectSelectDialog.cpp`

Good first targets:

- `amplifier`
- `eq`
- `delay`
- `compressor`
- `stereoenhancer`


## 3. Commands that need one level more work

These are feasible, but need targeting rules or new helper APIs in the agent.

### `open plugin <name>`

Meaning is ambiguous in LMMS:

- open a tool plugin window
- create an instrument track with that plugin
- focus an existing instrument window that already uses that plugin
- add an effect plugin to a selected effect chain

Recommended split:

- `show tool <name>`
- `new instrument <name>`
- `focus instrument <track name>`
- `add effect <name> to <track>`

Relevant source:

- `src/gui/MainWindow.cpp`
- `src/tracks/InstrumentTrack.cpp`
- `src/core/EffectChain.cpp`


### `import audio from <full path>`

Current agent only imports from Downloads.

Needed:

- accept arbitrary absolute path
- validate extension and existence

Relevant source:

- `plugins/AgentControl/AgentControl.cpp`
- `src/core/SampleClip.cpp`


### `focus track <name>`
### `focus instrument window <track>`

Needed:

- track lookup by name
- bring the correct `InstrumentTrackWindow` or `SampleTrackWindow` to front

Relevant source:

- `src/gui/tracks/InstrumentTrackView.cpp`
- `src/gui/instrument/InstrumentTrackWindow.cpp`
- `src/gui/SampleTrackWindow.cpp`


### `play`
### `pause`
### `stop`

LMMS has playback control paths, but the clean agent entry point should target
the active editor or the song explicitly.

Relevant source:

- `src/gui/MainWindow.cpp`
- editor playback paths used by key handling


### `rename track <old> to <new>`

Needed:

- track lookup by `Track::name()`
- call `setName(...)`

Relevant source:

- `src/core/Track.cpp`
- `src/tracks/InstrumentTrack.cpp`
- `src/tracks/SampleTrack.cpp`


### `mute track <name>`
### `solo track <name>`

Needed:

- track lookup
- update mute or solo model

Relevant source:

- `src/core/Track.cpp`
- `include/Track.h`


## 4. Commands that need deeper LMMS-specific logic

These are possible, but not just one API call.

### `add 808 drum pattern to my song`

There are at least two valid implementations:

- current shortcut: sample-track clips on the song timeline
- richer version: instrument track or BB/pattern-based drum programming

For a real beat agent, the better target is beat/bassline or pattern-track
authoring, not only sample clips.

Relevant source/doc:

- `doc/wiki/LMMS-Architecture.md`
- `src/tracks/PatternTrack.cpp`
- `src/core/Track.cpp`


### `add hi hats`
### `add snare on 2 and 4`
### `humanize drums`

Needed:

- a pattern representation
- step or note placement rules
- clip selection and target track rules

This is where the command model should become intent-based instead of
simple keyword matching.


### `open splicer`

This is not an LMMS internal command unless you mean the external Splice app.
That should be treated as an OS command, not an LMMS command.

Recommended split:

- LMMS agent handles LMMS internals
- optional desktop helper handles macOS app launching


### `do anything in LMMS`

LMMS has a strong internal API for:

- project lifecycle
- tracks
- instruments
- effects
- imports
- tool windows

It does not expose a single generic command bus for all GUI actions. To reach
"do anything" you need:

- a command grammar
- object targeting (`current track`, `selected track`, `track named X`)
- safe mutation helpers on the GUI thread
- more explicit editor/window control APIs


## 5. Recommended command grammar

Use commands in these families so the agent stays deterministic.

### Project

- `new project`
- `open project <path>`
- `save project`
- `save project as <path>`
- `import midi <path>`
- `import hydrogen <path>`


### Windows

- `show song editor`
- `show pattern editor`
- `show piano roll`
- `show automation editor`
- `show mixer`
- `show controller rack`
- `show project notes`
- `show microtuner`
- `show tool <name>`


### Tracks

- `new instrument track`
- `new sample track`
- `new automation track`
- `rename track <name>`
- `mute track <name>`
- `solo track <name>`


### Instruments

- `new instrument <plugin>`
- `set instrument <plugin> on <track>`
- `load file <path> into instrument <track>`
- `open slicer`
- `send <sample> to slicer`


### Effects

- `add effect <plugin> to <track>`
- `remove effect <plugin> from <track>`


### Clips and patterns

- `import audio <path>`
- `add 808`
- `add kick`
- `add snare pattern`
- `add hi hats`


## 6. Recommended implementation order

1. Stabilize the text command bus around explicit verbs and arguments.
2. Add window commands via `MainWindow` slots.
3. Add track lookup helpers by name and type.
4. Add instrument commands through `InstrumentTrack::loadInstrument(...)`.
5. Add effect commands through `EffectChain`.
6. Add richer beat/pattern authoring once track targeting is stable.
7. Add voice on top of the same command bus, not as a separate control path.


## 7. Practical next batch to implement

These are the best next commands because the source already supports them
cleanly:

- `new project`
- `show mixer`
- `show piano roll`
- `show song editor`
- `new instrument track`
- `new sample track`
- `open slicer`
- `new instrument kicker`
- `new instrument tripleoscillator`
- `add effect amplifier to <track>`
- `import midi <path>`
- `import hydrogen <path>`
- `import audio <full path>`
