# Why the OLCI push showed static copy

FCM, APNS, and Infobip **do not merge** `<PNR>`, `{{PNR}}`, or `[for-each]` themselves. If the merge engine never runs (or the tags are locked inside a literal encode), the device displays the template as static data.

## What you were seeing

| Symptom | Cause |
| --- | --- |
| Body contains `[for-each flight]`, `<CARRIER_CODE>`, `<FLIGHT_NUM>` | Tags were wrapped in `[encode as='json-string']…[/encode]`. That encode is a **literal JSON-escape** of its inner text. Inner `for-each` / `if` / tokens are not evaluated, so they ship as static characters. |
| Deep link is `surname=%7B%7BPAX_LASTNAME%7D%7D&pnrNumber=%7B%7BPNR%7D%7D` | `%7B%7B` is already percent-encoded `{{`. 15 Below never sees `<PAX_LASTNAME>` or `{{PAX_LASTNAME}}`, so every passenger gets the same URL. |
| NSE / app cannot rewrite the alert | `mutable-content` and `content-available` were set, but there was **no FCM `data` map and no APNS custom keys**. The extension only receives the static `aps.alert` strings. |
| Infobip custom payload empty | Infobip delivers personalisation either by merging placeholders **before** send, or via `customPayload` / FCM `data` (all values must be **strings**). Neither was present. |

## Rule

1. Merge in **15 Below** (this JSON is a 15 Below template, not an FCM console paste).
2. Keep `[for-each]`, `[if]`, and `<TOKENS>` **outside** `[encode as='json-string']`.
3. Encode **only** values that need it — last name in the query string: `[encode as='url']<PAX_LASTNAME>[/encode]`.
4. After merge, FCM `data.*` values must all be strings (FCM rejects objects).
5. Put the same merged strings on APNS **next to** `aps` (not inside `aps`) so the Notification Service Extension can read `pnr`, `surname`, `deepLink`.

## Do not paste this file into Firebase Console or Infobip as finished copy

Those UIs will send the tags unchanged. Save it as the **15 Below push JSON template** with journey logic enabled. The payload that leaves 15 Below toward FCM/Infobip must already contain `KC854`, `KASSYM`, `ABC123`, etc.

## After merge (direct KC854, PNR ABC123)

`notification.body` / `data.body` / `aps.alert.body`:

```
Check in online for your KC854 Almaty, Kazakhstan - Astana, Kazakhstan flight now and save time at the airport.
Open your booking: https://app-ds-website-uat-we.azurewebsites.net/global-en/mmb/booking-details?surname=KASSYM&pnrNumber=ABC123#/6
```

`data` (strings only):

```
type=OLCI_OPEN
pnr=ABC123
surname=KASSYM
flightNumbers=KC854
journey=Almaty, Kazakhstan - Astana, Kazakhstan
deepLink=https://app-ds-website-uat-we.azurewebsites.net/global-en/mmb/booking-details?surname=KASSYM&pnrNumber=ABC123#/6
```
