# AgentControl Integration

Canonical LMMS integration boundary for the agent stack.

Implementation lives in the LMMS plugin source:

- `/Users/saksham/grp/docs/lmmsagent/lmms/plugins/AgentControl/AgentControl.h`
- `/Users/saksham/grp/docs/lmmsagent/lmms/plugins/AgentControl/AgentControl.cpp`

Transport:

- TCP localhost `127.0.0.1:7777`
- newline-delimited JSON request/response

Request:

```json
{
  "tool": "load_sample",
  "args": {
    "track": "Agent 808",
    "sample_path": "/path/to/sample.wav"
  }
}
```

Response envelope:

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
