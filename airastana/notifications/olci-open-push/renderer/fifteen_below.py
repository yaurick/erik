"""Minimal 15 Below-style template engine for OLCI push payloads.

Supports the constructs used in Air Astana FCM/APNS templates:

- ``<ENABLE_JOURNEY_LOGIC> ... </ENABLE_JOURNEY_LOGIC>``
- ``[for-each flight]`` / ``[for-each journey]``
- ``[if path=value and path<>value]``
- ``[encode as='json-string'|url]``
- Tokens ``<NAME>`` and ``<NAME format=city_state|url>``

Journey objects are derived from flights that share ``journey_id``.
With journey logic enabled, a journey is relevant when any of its
flights is relevant, and cancelled (``schedule_change=X``) only when
every flight on that journey is cancelled.
"""

from __future__ import annotations

import json
import re
from typing import Any
from urllib.parse import quote

TRUE_VALUES = {"true", "True", True, "TRUE"}
TOKEN_RE = re.compile(r"<([A-Z0-9_]+)(?:\s+format=([a-z0-9_]+))?>")
OPEN_TAG_RE = re.compile(
    r"\[(for-each|if|encode)\s+([^\]]+)\]",
    re.IGNORECASE,
)


def load_booking(data: dict[str, Any], enable_journey_logic: bool = True) -> dict[str, Any]:
    flights = [dict(f) for f in data.get("flights", [])]
    journeys = _build_journeys(flights, lift_relevance=enable_journey_logic)
    triggering = next((f for f in flights if _is_true(f.get("relevant_flight"))), None)
    if triggering is None and flights:
        triggering = flights[0]
    return {
        "pnr": data.get("pnr", ""),
        "pax_lastname": data.get("pax_lastname", ""),
        "flights": flights,
        "journeys": journeys,
        "flight": triggering,
        "journey": next((j for j in journeys if _is_true(j.get("relevant_flight"))), None),
        "enable_journey_logic": enable_journey_logic,
    }


def _build_journeys(flights: list[dict[str, Any]], lift_relevance: bool = True) -> list[dict[str, Any]]:
    order: list[str] = []
    grouped: dict[str, list[dict[str, Any]]] = {}
    for flight in flights:
        jid = str(flight.get("journey_id") or "J1")
        if jid not in grouped:
            order.append(jid)
            grouped[jid] = []
        grouped[jid].append(flight)

    journeys: list[dict[str, Any]] = []
    for jid in order:
        segs = grouped[jid]
        first, last = segs[0], segs[-1]
        relevant = (
            any(_is_true(s.get("relevant_flight")) for s in segs) if lift_relevance else False
        )
        all_cancelled = all(_is_cancelled(s.get("schedule_change")) for s in segs)
        journeys.append(
            {
                "journey_id": jid,
                "flights": segs,
                "dept_city": first.get("dept_city", ""),
                "dept_country": first.get("dept_country", ""),
                "arrv_city": last.get("arrv_city", ""),
                "arrv_country": last.get("arrv_country", ""),
                "relevant_flight": relevant,
                "schedule_change": "X" if all_cancelled else "",
            }
        )
    return journeys


def _is_true(value: Any) -> bool:
    return value in TRUE_VALUES or value is True


def _is_cancelled(value: Any) -> bool:
    return str(value or "") == "X"


def strip_journey_wrapper(template: str) -> tuple[str, bool]:
    text = template.strip()
    enabled = False
    if text.startswith("<ENABLE_JOURNEY_LOGIC>"):
        enabled = True
        text = text[len("<ENABLE_JOURNEY_LOGIC>") :]
        if text.rstrip().endswith("</ENABLE_JOURNEY_LOGIC>"):
            text = text.rstrip()[: -len("</ENABLE_JOURNEY_LOGIC>")]
        text = text.strip()
    return text, enabled


def render(
    template: str,
    booking_data: dict[str, Any],
    *,
    literal_encode: bool = False,
) -> str:
    """Render a 15 Below push template.

    ``literal_encode=True`` matches the production bug: ``[encode as='json-string']``
    JSON-escapes its inner text *without* running for-each / if / tokens, so the
    device receives static template source.
    """
    payload, enabled = strip_journey_wrapper(template)
    context = load_booking(booking_data, enable_journey_logic=enabled)
    context["literal_encode"] = literal_encode
    return _render_fragment(payload, context)


def render_json(
    template: str,
    booking_data: dict[str, Any],
    *,
    literal_encode: bool = False,
) -> dict[str, Any]:
    rendered = render(template, booking_data, literal_encode=literal_encode)
    return json.loads(rendered)


UNMERGED_RE = re.compile(
    r"\[for-each |\[if |\[encode |\[/for-each\]|\[/if\]|\[/encode\]"
    r"|<CARRIER_CODE>|<FLIGHT_NUM>|<JOURNEY_[A-Z_]+"
    r"|<PNR>|<PAX_LASTNAME>|%7B%7B|\{\{"
)


def unmerged_markers(text: str) -> list[str]:
    return UNMERGED_RE.findall(text)


def _render_fragment(text: str, context: dict[str, Any]) -> str:
    out: list[str] = []
    i = 0
    while i < len(text):
        if text.startswith("[for-each ", i) or text.startswith("[if ", i) or text.startswith("[encode ", i):
            kind, arg, inner, end = _read_block(text, i)
            if kind == "for-each":
                out.append(_render_for_each(arg.strip(), inner, context))
            elif kind == "if":
                if _eval_expr(arg.strip(), context):
                    out.append(_render_fragment(inner, context))
            elif kind == "encode":
                inner_text = (
                    inner
                    if context.get("literal_encode")
                    else _render_fragment(inner, context)
                )
                out.append(_apply_encode(arg.strip(), inner_text))
            i = end
            continue

        token_match = TOKEN_RE.match(text, i)
        if token_match:
            out.append(_resolve_token(token_match.group(1), token_match.group(2), context))
            i = token_match.end()
            continue

        out.append(text[i])
        i += 1
    return "".join(out)


def _read_block(text: str, start: int) -> tuple[str, str, str, int]:
    open_match = OPEN_TAG_RE.match(text, start)
    if not open_match:
        raise ValueError(f"Invalid block at {start}: {text[start:start + 40]!r}")
    kind = open_match.group(1).lower()
    arg = open_match.group(2)
    close = f"[/{kind}]"
    open_prefix = f"[{kind}"
    depth = 1
    i = open_match.end()
    inner_start = i
    while i < len(text):
        if text.startswith(close, i):
            depth -= 1
            if depth == 0:
                return kind, arg, text[inner_start:i], i + len(close)
            i += len(close)
            continue
        if text.startswith(open_prefix, i) and (i + len(open_prefix) < len(text)) and text[i + len(open_prefix)] in " \t":
            depth += 1
            nxt = text.find("]", i)
            i = nxt + 1 if nxt != -1 else i + 1
            continue
        i += 1
    raise ValueError(f"Unclosed [{kind}] block")


def _render_for_each(name: str, inner: str, context: dict[str, Any]) -> str:
    collection = context.get(f"{name}s")
    if not isinstance(collection, list):
        collection = context.get(name)
    if not isinstance(collection, list):
        collection = []
    chunks: list[str] = []
    for item in collection:
        child = dict(context)
        child[name] = item
        # 15 Below keeps the triggering flight in scope inside journey loops.
        # Only a [for-each flight] iteration replaces `flight`.
        if name == "flight":
            child["flight"] = item
        chunks.append(_render_fragment(inner, child))
    return "".join(chunks)


def _eval_expr(expr: str, context: dict[str, Any]) -> bool:
    parts = [p.strip() for p in re.split(r"\s+and\s+", expr, flags=re.IGNORECASE)]
    return all(_eval_clause(p, context) for p in parts if p)


def _eval_clause(clause: str, context: dict[str, Any]) -> bool:
    if "<>" in clause:
        path, expected = clause.split("<>", 1)
        actual = _resolve_path(path.strip(), context)
        return str(actual or "") != expected.strip()
    if "=" in clause:
        path, expected = clause.split("=", 1)
        actual = _resolve_path(path.strip(), context)
        expected = expected.strip()
        if expected in {"True", "true", "FALSE", "False", "false"}:
            want = expected.lower() == "true"
            return _is_true(actual) is want
        return str(actual) == expected
    raise ValueError(f"Unsupported condition: {clause!r}")


def _resolve_path(path: str, context: dict[str, Any]) -> Any:
    cur: Any = context
    for part in path.split("."):
        if cur is None:
            return None
        if isinstance(cur, dict):
            cur = cur.get(part)
        else:
            cur = getattr(cur, part, None)
    return cur


def _resolve_token(name: str, fmt: str | None, context: dict[str, Any]) -> str:
    key = name.lower()
    if key == "pnr":
        value = str(context.get("pnr", ""))
        return _format_value(value, fmt)
    if key == "pax_lastname":
        return _format_value(str(context.get("pax_lastname", "")), fmt)

    source: dict[str, Any] | None
    field = key
    if key.startswith("journey_"):
        source = context.get("journey")
        field = key[len("journey_") :]
    else:
        source = context.get("flight")

    if not source:
        return ""

    raw = source.get(field, "")
    if fmt == "city_state":
        country_key = field.replace("city", "country")
        city = str(raw or "")
        country = str(source.get(country_key, "") or "")
        return f"{city}, {country}" if country else city
    return _format_value(str(raw or ""), fmt)


def _format_value(value: str, fmt: str | None) -> str:
    if fmt == "url":
        return quote(value, safe="")
    return value


def _apply_encode(arg: str, value: str) -> str:
    match = re.search(r"as=['\"]([^'\"]+)['\"]", arg, re.IGNORECASE)
    encoding = (match.group(1) if match else arg).lower()
    if encoding in {"json-string", "json"}:
        value = value.replace("\\n", "\n").replace("\\t", "\t")
        return json.dumps(value, ensure_ascii=False)[1:-1]
    if encoding == "url":
        return quote(value, safe="")
    raise ValueError(f"Unsupported encode type: {arg!r}")


def notification_body(payload: dict[str, Any]) -> str:
    return payload["notification"]["body"]
