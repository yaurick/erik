# OLCI open push — journey logic

15 Below FCM/APNS template for *Online check-in is now open*. Dynamic fields merge **before** the push is handed to FCM/Infobip; they are not static copy.

**Paste this:** [`payloads/corrected.json`](payloads/corrected.json)

Do not paste it into Firebase Console or Infobip as finished text — those channels will send the tags unchanged. Why the original showed static data: [DYNAMIC_PARAMETERS.md](DYNAMIC_PARAMETERS.md).

## After merge (KC854 ALA–NQZ, PNR ABC123, KASSYM)

> **Online check-in is now open**  
> Check in online for your KC854 Almaty, Kazakhstan - Astana, Kazakhstan flight now and save time at the airport.  
> Open your booking: `https://app-ds-website-uat-we.azurewebsites.net/global-en/mmb/booking-details?surname=KASSYM&pnrNumber=ABC123#/6`

`data` (FCM requires strings) and APNS custom keys: `type=OLCI_OPEN`, `pnr=ABC123`, `surname=KASSYM`, plus `flightNumbers`, `journey`, `deepLink`.

## Defects in the submitted payload

| Defect | What the passenger sees |
| --- | --- |
| Whole body wrapped in `[encode as='json-string']` | `[for-each]`, `<CARRIER_CODE>`, `<FLIGHT_NUM>` ship as static text |
| `surname=%7B%7BPAX_LASTNAME%7D%7D` | Every device opens MMB with literal `{{PAX_LASTNAME}}` |
| `[for-each journey][if flight.relevant_flight=…]` | Return PNR prints outbound **and** inbound city pairs |
| No FCM `data` / APNS custom keys | NSE (`mutable-content`) has nothing to substitute |

## Verify

```bash
cd airastana/notifications/olci-open-push/renderer
python3 -m unittest test_olci_journey_logic.py -v
python3 generate_preview.py --out ../preview.html
```
