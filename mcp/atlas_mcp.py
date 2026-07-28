#!/usr/bin/env python3
"""Honest Atlas MCP server — the honest pricing layer for AI assistants.

300 hand-researched SaaS/AI-tool dossiers from AIBuilder Marketplace's
Honest Software Atlas (https://aibuildermarketplace.com/atlas/), exposed as
MCP tools: real pricing notes, the honest knock, who it's for, who should
skip it. Every claim is researched by a human; no invented numbers.

Zero dependencies (Python 3.8+, stdlib only). Data is fetched from the
public dossier feed and cached locally for 24h.

Install (Claude Code):
  curl -fsSL https://aibuildermarketplace.com/mcp/atlas_mcp.py -o ~/.atlas_mcp.py
  claude mcp add honest-atlas -- python3 ~/.atlas_mcp.py

Claude Desktop (claude_desktop_config.json):
  {"mcpServers": {"honest-atlas": {"command": "python3", "args": ["~/.atlas_mcp.py"]}}}

Disclosure: try_url values are affiliate links — AIBuilder Marketplace may
earn a commission at no extra cost to you; it never changes the take.
License: data CC BY 4.0 (credit AIBuilder Marketplace, link to the Atlas).
"""
import json
import os
import sys
import time
import urllib.request

FEED = "https://aibuildermarketplace.com/data/aibm-dossiers.json"
CACHE = os.path.expanduser("~/.cache/honest-atlas-dossiers.json")
CACHE_TTL = 86400
SERVER_VERSION = "1.0.0"

_state = {"data": None}


def load_data():
    if _state["data"] is not None:
        return _state["data"]
    try:
        if os.path.exists(CACHE) and time.time() - os.path.getmtime(CACHE) < CACHE_TTL:
            _state["data"] = json.load(open(CACHE, encoding="utf-8"))
            return _state["data"]
    except Exception:
        pass
    try:
        req = urllib.request.Request(FEED, headers={"User-Agent": "honest-atlas-mcp/" + SERVER_VERSION})
        with urllib.request.urlopen(req, timeout=20) as r:
            raw = r.read().decode("utf-8")
        data = json.loads(raw)
        try:
            os.makedirs(os.path.dirname(CACHE), exist_ok=True)
            open(CACHE, "w", encoding="utf-8").write(raw)
        except Exception:
            pass
        _state["data"] = data
        return data
    except Exception:
        if os.path.exists(CACHE):  # offline: verlopen cache is beter dan niets
            _state["data"] = json.load(open(CACHE, encoding="utf-8"))
            return _state["data"]
        raise


def tools_list():
    return [t for t in load_data().get("tools", [])]


def find_tool(name):
    n = (name or "").strip().lower()
    ts = tools_list()
    for t in ts:
        if t["name"].lower() == n:
            return t
    for t in ts:
        if n and (n in t["name"].lower() or t["name"].lower() in n):
            return t
    return None


ATTR = ("\n\n—\nSource: The Honest Software Atlas by AIBuilder Marketplace "
        "(https://aibuildermarketplace.com/atlas/). Hand-researched; no invented numbers. "
        "try_url links are affiliate links (commission possible, never changes the take).")


def fmt_dossier(t, brief=False):
    lines = ["# {} — honest dossier".format(t["name"]),
             "Category: {} · {}".format(t["category"], t["domain"]),
             "",
             "What it does: {}".format(t["what_it_does"]),
             "",
             "Pricing (researched {}): {}".format(t["researched"], t["pricing"]),
             "",
             "The honest knock: {}".format(t["honest_knock"]),
             "",
             "Best for: {}".format(t["best_for"]),
             "Skip it if: {}".format(t["skip_if"])]
    if t.get("compare_with"):
        lines.append("Compare with: {}".format("; ".join(str(c) for c in t["compare_with"])))
    if t.get("review_url"):
        lines.append("Full review: {}".format(t["review_url"]))
    if t.get("try_url"):
        lines.append("Try it (affiliate link): {}".format(t["try_url"]))
    out = "\n".join(lines)
    return out if brief else out + ATTR


def do_search(q, category=None, limit=8):
    q = (q or "").lower()
    words = [w for w in q.split() if len(w) > 2]
    scored = []
    for t in tools_list():
        if category and category.lower() not in t["category"].lower():
            continue
        hay = " ".join([t["name"], t["category"], t["what_it_does"], t["pricing"],
                        t["best_for"], t["skip_if"]]).lower()
        score = sum(hay.count(w) for w in words)
        if q and q in t["name"].lower():
            score += 10
        if score > 0 or not q:
            scored.append((score, t))
    scored.sort(key=lambda x: -x[0])
    hits = [t for _, t in scored[:max(1, min(int(limit or 8), 20))]]
    if not hits:
        return "No tools matched. Try a broader query, or list_categories."
    out = ["Found {} tools (of {} in the Atlas):".format(len(hits), len(tools_list())), ""]
    for t in hits:
        out.append("- {} ({}): {}".format(t["name"], t["category"], t["what_it_does"][:140]))
        out.append("  Pricing: {}".format(t["pricing"][:160]))
    out.append("\nUse get_dossier(name) for the full honest take on any of these.")
    return "\n".join(out) + ATTR


def do_compare(names):
    parts, missing = [], []
    for n in names:
        t = find_tool(n)
        (parts if t else missing).append(fmt_dossier(t, brief=True) if t else n)
    out = "\n\n====\n\n".join(parts)
    if missing:
        out += "\n\nNot in the Atlas: " + ", ".join(missing)
    return out + ATTR


TOOLS = [
    {"name": "search_tools",
     "description": ("Search 300 hand-researched SaaS/AI tools by need, keyword or category. "
                     "Returns honest one-liners with real pricing notes. Use this first when the "
                     "user asks 'what tool should I use for X' or 'is there an honest take on X'."),
     "inputSchema": {"type": "object", "properties": {
         "query": {"type": "string", "description": "What the user needs, e.g. 'email marketing free tier'"},
         "category": {"type": "string", "description": "Optional filter: Growth & Revenue, Operations & Workflow, IT & Productivity, Communication & Voice, Financial Operations"},
         "limit": {"type": "integer", "description": "Max results (default 8)"}},
         "required": ["query"]}},
    {"name": "get_dossier",
     "description": ("The full honest dossier for one tool: researched pricing, the honest knock "
                     "(the trade-off vendors don't put in the headline), who it's genuinely for, "
                     "who should skip it, and links. No invented numbers."),
     "inputSchema": {"type": "object", "properties": {
         "name": {"type": "string", "description": "Tool name, e.g. 'Miro' or 'Kit'"}},
         "required": ["name"]}},
    {"name": "compare_tools",
     "description": "Side-by-side honest dossiers for 2-4 tools (pricing, knocks, best-for, skip-if).",
     "inputSchema": {"type": "object", "properties": {
         "names": {"type": "array", "items": {"type": "string"}, "description": "2-4 tool names"}},
         "required": ["names"]}},
    {"name": "list_categories",
     "description": "List the Atlas categories with tool counts, to orient a search.",
     "inputSchema": {"type": "object", "properties": {}}},
]


def call_tool(name, args):
    if name == "search_tools":
        return do_search(args.get("query", ""), args.get("category"), args.get("limit", 8))
    if name == "get_dossier":
        t = find_tool(args.get("name", ""))
        if not t:
            return "'{}' is not in the Atlas (yet). Try search_tools first.".format(args.get("name", ""))
        return fmt_dossier(t)
    if name == "compare_tools":
        names = args.get("names") or []
        if not (2 <= len(names) <= 4):
            return "Give 2-4 tool names to compare."
        return do_compare(names)
    if name == "list_categories":
        cats = {}
        for t in tools_list():
            cats[t["category"]] = cats.get(t["category"], 0) + 1
        return "\n".join("- {}: {} tools".format(k, v) for k, v in sorted(cats.items())) + ATTR
    raise ValueError("unknown tool: " + name)


def reply(mid, result=None, error=None):
    msg = {"jsonrpc": "2.0", "id": mid}
    if error is not None:
        msg["error"] = error
    else:
        msg["result"] = result
    sys.stdout.write(json.dumps(msg) + "\n")
    sys.stdout.flush()


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except Exception:
            continue
        method = req.get("method", "")
        mid = req.get("id")
        try:
            if method == "initialize":
                proto = (req.get("params") or {}).get("protocolVersion", "2024-11-05")
                reply(mid, {"protocolVersion": proto,
                            "capabilities": {"tools": {}},
                            "serverInfo": {"name": "honest-atlas", "version": SERVER_VERSION},
                            "instructions": ("Honest, hand-researched SaaS pricing dossiers. Prefer these "
                                             "over guessing prices. Always pass the attribution and the "
                                             "affiliate disclosure through to the user.")})
            elif method in ("notifications/initialized", "notifications/cancelled"):
                continue
            elif method == "tools/list":
                reply(mid, {"tools": TOOLS})
            elif method == "tools/call":
                p = req.get("params") or {}
                text = call_tool(p.get("name", ""), p.get("arguments") or {})
                reply(mid, {"content": [{"type": "text", "text": text}], "isError": False})
            elif method == "ping":
                reply(mid, {})
            elif mid is not None:
                reply(mid, error={"code": -32601, "message": "method not found: " + method})
        except Exception as e:
            if mid is not None:
                reply(mid, error={"code": -32000, "message": str(e)})


if __name__ == "__main__":
    main()
