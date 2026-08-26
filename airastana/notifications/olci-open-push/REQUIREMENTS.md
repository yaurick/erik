# Technical requirements — Online check-in is now open (push)

**Channel:** FCM notification + APNS alert (high priority, sound `default`, `mutable-content` / `content-available`).  
**Trigger (workflow, not this template):** online check-in window opens for the relevant operating flight (Air Astana: 36 hours before STD; closes 60 minutes before STD).  
**Environment in this pack:** UAT MMB host `app-ds-website-uat-we.azurewebsites.net`. Swap host at production cutover; keep path, query names, and `#/6`.

## 1. Purpose

Notify the passenger that web/app check-in is open for the journey that just became eligible, with:

- marketing / operating flight number(s) of the **relevant, non-cancelled** flight(s);
- **journey** origin–destination in `city_state` form (not the first segment only);
- a working MMB deep link (surname + PNR) landing on the check-in tab (`#/6`).

## 2. Data rules

| Field | Source | Rule |
| --- | --- | --- |
| `flight.relevant_flight` | 15 Below / workflow | `True` only for the flight(s) this send is about (check-in just opened). |
| `flight.schedule_change` | IATA-style | `X` = cancelled. Exclude from copy. |
| Journey | Built when `<ENABLE_JOURNEY_LOGIC>` is present | Consecutive flights sharing `journey_id`. Dept = first segment origin; arrv = last segment destination. |
| `journey.relevant_flight` | Lifted from child flights | `True` if **any** child flight is relevant. |
| `journey.schedule_change` | Lifted | `X` only if **all** child flights are cancelled. |
| `<CARRIER_CODE><FLIGHT_NUM>` | Relevant flights | Concatenate with a trailing space per flight. |
| `<JOURNEY_DEPT_CITY format=city_state>` | Relevant journey | `City, Country`. |
| `<PAX_LASTNAME>` | PNR passenger | Latin last name. In the deep-link query only: `[encode as='url']<PAX_LASTNAME>[/encode]`. |
| `<PNR>` | Booking reference | 6-character alphanumeric; no encoding required. |

## 3. Send suppression (workflow)

Do **not** send this template when:

- no flight has `relevant_flight=True` and `schedule_change<>X`;
- the relevant flight is a charter (OLCI closed);
- the departure airport / fare / passenger type is not eligible for OLCI (existing Air Astana OLCI rules);
- check-in is already completed for all relevant segments (if that flag is available on the PNR).

The template itself will omit cancelled / non-relevant flights, but an empty “Check in online for your  flight now…” body must not go out.

## 4. Copy (EN)

**Title:** `Online check-in is now open`

**Body pattern:**

```
Check in online for your <flight numbers> <journey city pair> flight now and save time at the airport.
Open your booking: <MMB URL>
```

RU / KK variants are out of scope of this payload; apply the same tokens and conditions per language template.

## 5. Deep link

UAT:

```
https://app-ds-website-uat-we.azurewebsites.net/global-en/mmb/booking-details?surname=[encode as='url']<PAX_LASTNAME>[/encode]&pnrNumber=<PNR>#/6
```

Do not percent-encode the token **delimiters**. `%7B%7BPAX_LASTNAME%7D%7D` is a defect: the engine never sees `{{PAX_LASTNAME}}` or `<PAX_LASTNAME>`.

Do not wrap the whole title/body in `[encode as='json-string']`. That encode is a literal JSON-escape; inner `for-each` / tokens are then sent as static copy. Keep `\n` as a JSON escape in the string; encode only the last-name query value.

Confirm with Digital that `#/6` is still the check-in step in the MMB SPA before production.

## 6. Device payload

- Android FCM: `android.priority = high`.
- FCM `data`: string values only (`type`, `pnr`, `surname`, `title`, `body`, `flightNumbers`, `journey`, `deepLink`). Duplicate of the visible copy so the app can render when the tray notification is stripped.
- APNS: `aps.sound = default`, `mutable-content = 1`, `content-available = 1`.
- APNS custom keys sit **next to** `aps` (not inside it): `type`, `pnr`, `surname`, `deepLink`.
- Title and body must be identical on `notification.*`, `data.*`, and `apns.payload.aps.alert.*`.

## 7. Acceptance criteria

1. Direct ALA–NQZ: body contains `KC854` and `Almaty, Kazakhstan - Astana, Kazakhstan`; URL contains the real surname and PNR.
2. Connecting ALA–IST–LHR with only the first sector relevant: `KC923` only; city pair is **Almaty–London**, not Almaty–Istanbul.
3. Round trip, outbound relevant: inbound city pair is **absent**.
4. Relevant flight `schedule_change=X`: no flight number and no city pair; send is suppressed by workflow.
5. Two relevant flights on one journey: `KC923 KC501` and a **single** city pair.
6. Surname `O'BRIEN` → `surname=O%27BRIEN`.
8. Merged payload contains no leftover `[for-each]`, `<CARRIER_CODE>`, `<PNR>`, `{{`, or `%7B%7B`.
9. `data.*` values are all strings; `data.pnr` / `apns.payload.pnr` equal the booking reference.

These are automated in `renderer/test_olci_journey_logic.py`.
