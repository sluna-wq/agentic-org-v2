#!/usr/bin/env python3
"""
Convert claude --output-format stream-json to readable markdown.
Usage: claude ... --output-format stream-json | python3 scripts/jsonl_to_md.py LABEL
"""
import sys
import json
from datetime import datetime, timezone

label = sys.argv[1] if len(sys.argv) > 1 else "session"
now   = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

print(f"# Session: {label}")
print(f"Generated: {now}\n\n---\n")


def clip(s, n=600):
    s = str(s)
    return s if len(s) <= n else s[:n] + f"\n… [{len(s) - n} chars]"


for raw in sys.stdin:
    raw = raw.strip()
    if not raw:
        continue
    try:
        e = json.loads(raw)
    except json.JSONDecodeError:
        sys.stderr.write(f"[non-json] {raw}\n")
        continue

    t = e.get("type", "")

    if t == "system":
        model = e.get("model", "")
        mode  = e.get("permissionMode", "")
        tools = [x["name"] for x in e.get("tools", []) if "name" in x]
        print(f"**Model:** `{model}` | **Mode:** `{mode}`")
        if tools:
            print(f"**Tools:** {', '.join(tools)}")
        print()

    elif t == "assistant":
        for blk in e.get("message", {}).get("content", []):
            bt = blk.get("type", "")
            if bt == "text":
                text = blk.get("text", "").strip()
                if text:
                    print(f"**Assistant:**\n\n{text}\n")
            elif bt == "tool_use":
                name = blk.get("name", "")
                inp  = blk.get("input", {})
                print(f"**→ `{name}`**")
                for k, v in inp.items():
                    s = json.dumps(v) if not isinstance(v, str) else v
                    print(f"  - **{k}:** `{clip(s)}`")
                print()

    elif t == "user":
        for blk in e.get("message", {}).get("content", []):
            if blk.get("type") != "tool_result":
                continue
            raw_content = blk.get("content", "")
            if isinstance(raw_content, list):
                text = "\n".join(
                    i.get("text", "") for i in raw_content if i.get("type") == "text"
                )
            else:
                text = str(raw_content)
            if text.strip():
                print(f"**← Result:**\n```\n{clip(text, 2000)}\n```\n")

    elif t == "result":
        result   = e.get("result", "")
        turns    = e.get("num_turns", "?")
        duration = e.get("duration_ms", 0) / 1000
        is_error = e.get("is_error", False)
        status   = "ERROR" if is_error else "success"
        print(f"---\n\n## Final Output\n\n{result}\n")
        print(f"---\n\n**Turns:** {turns} | **Duration:** {duration:.1f}s | **Status:** {status}\n")
