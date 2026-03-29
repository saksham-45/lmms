# LMMS Agent

Local LMMS agent stack built around typed `AgentControl` tools.

## Structure

- `integrations/lmms/AgentControl/`: integration contract and schema.
- `plugins/AgentControl/`: typed LMMS tool server implementation.
- `shared/`: deterministic discovery, planner, orchestrator, and project memory.
- `lmms-text-agent/`: text frontend over shared planner/orchestrator.
- `lmms-voice-agent/`: voice frontend using `whisper.cpp` transcript + same planner/orchestrator.
- `scripts/`: build/install/run helpers.
- `evals/`: fixed evaluation task taxonomy.
- `docs/MANUAL_TASK_MAP.md`: compatibility-aware transfer from LMMS 0.4.12 manual.
- `docs/MANUAL_FEATURE_COVERAGE.md`: full feature-family map from manual to agent capabilities.
- `docs/MANUAL_TOC_EXTRACTED.md`: extracted TOC index used for manual coverage.

## Core Tool Contract

All tool responses follow:

```json
{
  "ok": true,
  "result": {},
  "state_delta": {},
  "warnings": [],
  "error_code": null,
  "error_message": null
}
```

## Build + Install

```bash
./lmmsagent/scripts/build_agentcontrol.sh
./lmmsagent/scripts/install_agentcontrol.sh
```

## Run Text Agent

```bash
./lmmsagent/scripts/run_text_agent.sh --interactive
# or single command
./lmmsagent/scripts/run_text_agent.sh "set tempo to 124"
# guided mode (confirm each step)
./lmmsagent/scripts/run_text_agent.sh --guided "compose from score sheet"
# manual capability map
./lmmsagent/scripts/run_text_agent.sh "manual map"
./lmmsagent/scripts/run_text_agent.sh "manual map automation"
```

## Run Voice Agent

```bash
./lmmsagent/scripts/run_voice_agent.sh --audio /path/to/input.wav --whisper-model /path/to/ggml-model.bin
# or bypass ASR
./lmmsagent/scripts/run_voice_agent.sh --transcript "load instrument triple oscillator"
```

## Notes

- Planner output is always structured (`plan`, `clarify`, or `reject`).
- Clarification is triggered for low confidence, subjective prompts, and risky operations.
- Project memory is append-only journal + preference cache under `~/.lmmsagent/memory/`.
- Beginner prompts are mapped to manual-driven playbooks with explicit compatibility cautions.
