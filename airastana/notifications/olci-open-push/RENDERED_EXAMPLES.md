# Rendered copy

## UAT today — parameters stay static

`[encode as='json-string']` around the whole body ships the tags unchanged:

```
Check in online for your [for-each flight][if flight.relevant_flight=True and flight.schedule_change<>X]<CARRIER_CODE><FLIGHT_NUM>[/if][/for-each] ...
Open your booking: ...surname=%7B%7BPAX_LASTNAME%7D%7D&pnrNumber=%7B%7BPNR%7D%7D#/6
```

## After merge — corrected (direct KC854)

See `payloads/merged_example_direct.json` for the JSON FCM must receive.

```
Check in online for your KC854 Almaty, Kazakhstan - Astana, Kazakhstan flight now and save time at the airport.
Open your booking: https://app-ds-website-uat-we.azurewebsites.net/global-en/mmb/booking-details?surname=KASSYM&pnrNumber=ABC123#/6
```

`data.pnr=ABC123` `data.surname=KASSYM` `data.flightNumbers=KC854`

## Connecting ALA–IST–LHR (only KC923 relevant)

```
Check in online for your KC923 Almaty, Kazakhstan - London, United Kingdom flight now and save time at the airport.
```

## Return trip, outbound check-in open

Original also leaked the inbound city pair. Corrected:

```
Check in online for your KC854 Almaty, Kazakhstan - Astana, Kazakhstan flight now and save time at the airport.
Open your booking: https://app-ds-website-uat-we.azurewebsites.net/global-en/mmb/booking-details?surname=NUR-SULTAN&pnrNumber=RTN789#/6
```
