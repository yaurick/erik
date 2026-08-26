#!/usr/bin/env python3
"""Render original vs corrected OLCI payloads into an HTML preview."""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path

from fifteen_below import notification_body, render_json

ROOT = Path(__file__).resolve().parents[1]
PAYLOADS = ROOT / "payloads"
FIXTURES = ROOT / "fixtures"

CASES = [
    ("direct_ala_nqz.json", "Direct ALA–NQZ", "One relevant non-cancelled flight."),
    ("connecting_ala_ist_lhr.json", "Connecting ALA–IST–LHR", "Journey O&D is Almaty–London, not Almaty–Istanbul."),
    ("return_trip.json", "Return trip, outbound check-in open", "Inbound journey must not appear."),
    ("cancelled_relevant.json", "Cancelled relevant flight (X)", "Flight number and city pair omitted."),
    ("two_relevant_flights.json", "Two relevant flights + special surname", "Space-separated flight numbers; URL-encoded last name."),
]


def _load_template(name: str) -> str:
    return (PAYLOADS / name).read_text(encoding="utf-8")


def _load_booking(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def _card(title: str, body: str, kind: str) -> str:
    return f"""
      <article class="phone {kind}">
        <p class="app">Air Astana</p>
        <h3>{html.escape(title)}</h3>
        <p class="body">{html.escape(body)}</p>
      </article>
    """


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    original = _load_template("original.json")
    corrected = _load_template("corrected.json")
    static_booking = _load_booking("direct_ala_nqz.json")
    static_body = notification_body(
        render_json(original, static_booking, literal_encode=True)
    )
    static_title = render_json(original, static_booking, literal_encode=True)[
        "notification"
    ]["title"]
    merged_direct = render_json(corrected, static_booking)
    rows = [
        f"""
            <section>
              <h2>UAT: dynamic parameters sent as static text</h2>
              <p class="note">Wrapping the whole body in <code>[encode as='json-string']</code> JSON-escapes tags instead of merging them. FCM/Infobip then deliver that literal string.</p>
              <div class="pair">
                {_card(static_title, static_body, "before")}
                {_card(merged_direct["notification"]["title"], merged_direct["notification"]["body"], "after")}
              </div>
            </section>
            """
    ]
    for filename, label, note in CASES:
        booking = _load_booking(filename)
        orig_body = notification_body(render_json(original, booking))
        new_body = notification_body(render_json(corrected, booking))
        orig_title = render_json(original, booking)["notification"]["title"]
        new_title = render_json(corrected, booking)["notification"]["title"]
        rows.append(
            f"""
            <section>
              <h2>{html.escape(label)}</h2>
              <p class="note">{html.escape(note)} Fixture: <code>{html.escape(filename)}</code></p>
              <div class="pair">
                {_card(orig_title, orig_body, "before")}
                {_card(new_title, new_body, "after")}
              </div>
            </section>
            """
        )

    page = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>OLCI journey-logic push — before / after</title>
  <style>
    :root {{ font-family: "Helvetica Neue", Helvetica, Arial, sans-serif; color: #111; }}
    body {{ margin: 24px; background: #f4f4f1; }}
    h1 {{ font-size: 22px; }}
    h2 {{ font-size: 16px; margin-bottom: 4px; }}
    .note {{ color: #555; margin-top: 0; font-size: 13px; }}
    .pair {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }}
    .phone {{ background: #fff; border-radius: 16px; padding: 16px 18px; box-shadow: 0 8px 24px rgba(0,0,0,.08); }}
    .phone:before {{ display: block; font-size: 11px; letter-spacing: .08em; text-transform: uppercase; margin-bottom: 8px; color: #666; }}
    .before:before {{ content: "Original template"; color: #9b1c1c; }}
    .after:before {{ content: "Corrected journey logic"; color: #0f6b3f; }}
    .app {{ font-size: 12px; color: #666; margin: 0 0 4px; }}
    h3 {{ font-size: 15px; margin: 0 0 6px; }}
    .body {{ white-space: pre-wrap; font-size: 14px; line-height: 1.35; margin: 0; }}
    section {{ margin: 28px 0; }}
    code {{ font-size: 12px; }}
  </style>
</head>
<body>
  <h1>Online check-in is now open — journey logic</h1>
  <p>Rendered FCM <code>notification.title</code> / <code>notification.body</code> from the 15 Below template against PNR fixtures.</p>
  {''.join(rows)}
</body>
</html>
"""
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(page, encoding="utf-8")
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
