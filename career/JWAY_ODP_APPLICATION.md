# JWay ODP apply form — field-by-field (live form)

Form: https://jway-group.breezy.hr/p/48b74222e7b8-part-time-business-analyst-optimizely-data-platform-odp/apply  
Resume to upload: `career/Yerik_Kassym_ODP_CDP_Resume.pdf`

The form is **one page**. Do **not** use Indeed/LinkedIn quick-apply — upload the CDP PDF so they see the tailored CV.  
Check the privacy box last, then Submit.

---

## 1. Upload Resume * (file)

**Enter:** `Yerik_Kassym_ODP_CDP_Resume.pdf`  
Not the generic Sr BA PDF. This one leads with CDP / Emarsys / customer-data layer.

---

## 2. Full Name *

**Enter:** `Yerik Kassym`

---

## 3. Email Address *

**Enter:** `yerik.kassym@gmail.com`  
Use Gmail, not the Air Astana work email.

---

## 4. Phone Number *

**Enter:** your personal mobile with country code, e.g. `+7 …`  
WhatsApp-reachable is best. Required; not on the CV.

---

## 5. Desired Salary * (USD + amount + frequency)

Default is **US Dollar ($) + Yearly**. You must change the frequency.

| Control | Set to |
|---|---|
| Currency | US Dollar ($) — leave it |
| Frequency dropdown | **Hourly** (options: Yearly, Monthly, Biweekly, Weekly, Daily, **Hourly**) |
| Amount | **55** |

That is **$55/hour**. For 15–20 hrs/week ≈ **$3.6k–$4.8k/month**.

**Do not** leave it on Yearly and type `55` — that reads as $55/year.  
**Do not** type a ₸ monthly salary.  
If the dropdown will not switch, type **57200** and leave Yearly ($55 × 20 hrs × 52).

---

## 6. Cover Letter (optional)

Still fill it. Keep it short because questions 7–11 repeat the same story.

Paste:

```
I am applying for the part-time ODP Business Analyst contract (15–20 hrs/week).

I am a Senior BA (4+ years) working on CDP and customer-data integrations at Air Astana: previously Emarsys, currently driving a CDP as the consolidated customer-data layer, plus messaging channels (Infobip, SendGrid, 15 Below) and REST/SOAP APIs.

I have not used Optimizely ODP yet. I do the same work this role needs — CDP requirements, data-flow / schema mapping, technical specs, and pre-go-live testing — and I ramp on new platforms from API and configuration docs.

Available 15–20 hrs/week from 18 Aug 2026. Timezone Asia/Almaty (UTC+5). Live calls and focused work only after 17:30 Almaty (≈ 13:30 London / 08:30 US Eastern); delivery is evenings, weekends, and async.

Rate: USD $55/hour.

Yerik Kassym · yerik.kassym@gmail.com · linkedin.com/in/kassymyerik
```

---

## 7. BA / CDP experience * (textarea)

**Question:** *Tell us about your experience as a Business Analyst. Have you worked on Customer Data Platform (CDP), Marketing Analytics, CRM, or customer data integration projects? Please describe your role.*

Paste:

```
I have 4+ years as a Business Analyst (Senior BA since 2024) at Air Astana, owning requirements from BRD through technical specs, schemas, API documentation, and pre-business testing.

Yes — CDP and customer-data integration is my current work. I previously supported Emarsys, then moved to driving a CDP as the consolidated customer-data layer: mapping how CRM/CX, loyalty, and operational systems feed customer profiles into one platform. I write integration requirements, data-flow maps, and acceptance checks so marketing/CX and engineering share the same picture of the customer record.

I also own messaging/notification channels used for lifecycle communications (email, WhatsApp, SMS-style notifications via Infobip, SendGrid, and 15 Below), which sits next to marketing analytics use cases: events, templates, triggers, and downstream activation.

My role is the BA/integration owner — not the campaign operator: requirements, data contracts, APIs, and go-live validation.
```

---

## 8. Which CDPs / MarTech? * (radio — pick one)

Options: Optimizely Data Platform (ODP) · Salesforce CDP · Segment · Tealium · ActionIQ · Adobe Experience Platform · **Others**

**Select: Others**

Do not pick ODP. You have not implemented it. Emarsys is not on the list, so Others is the honest answer. The text in questions 7 and 6 already names Emarsys + current CDP.

---

## 9. Requirements → technical specs * (textarea)

**Question:** *Describe a project where you gathered business requirements and translated them into technical specifications or data requirements. What was your contribution and the outcome?*

Paste:

```
Example: consolidating customer data into a CDP and wiring marketing/CX channels onto it.

Business wanted one customer-data layer instead of fragmented profiles across Emarsys, messaging providers, and operational systems. I ran BRD review with business/CX, then produced technical requirements: source systems, objects/fields to sync, API contracts (REST/SOAP), sequence/data-flow diagrams, and acceptance criteria.

I documented endpoints in Postman, listed gaps (missing IDs, duplicate profile rules, channel triggers), and ran pre-business tests before sign-off.

Outcome: engineering and vendors had implementation-ready specs; CDP became the feed for customer data, and channels (email, WhatsApp, notifications) had a clear data contract instead of ad-hoc mappings. I use the same pattern on the Zendesk → Q19 channel migration (current-state map, requirements, UAT checklist).
```

---

## 10. Data mapping / SQL / APIs / events * (textarea)

**Question:** *What is your experience with data mapping, customer data models, SQL, APIs, or event tracking? Please indicate your level of proficiency and provide examples.*

Paste (honest — do not upgrade SQL unless you actually write it daily):

```
Data mapping / customer data models — strong (daily). I map source-to-target customer and operational data into the CDP (profiles, identifiers, channel attributes), produce schemas/data dictionaries, and flag identity and completeness issues before build.

APIs — strong (daily). REST and SOAP: technical documentation, integration requirements, Postman collections, endpoint validation, auth/error cases.

Event / channel tracking — solid. Messaging and CX events (sends, inbound WhatsApp, notification triggers, help-center/chatbot channels). I specify what must be captured and passed, not a full analytics-engineer tracking plan.

SQL — working / not primary. I can read models and write basic SELECT/JOIN checks to validate a mapping. I do not position as a SQL analyst; validation is usually API payloads, Postman, and schema review.

Example: CDP feed from surrounding systems — field mapping + API contract + Postman checks + pre-business test, not a warehouse SQL build.
```

If you *do* write SQL often at work, replace the SQL paragraph with one real example (table/join you used). Do not invent it.

---

## 11. Availability & start date * (short text)

**Question:** *This is a part-time remote consulting engagement requiring approximately 15–20 hours per week for 3–6 months. Are you available for this commitment, and what is your earliest start date?*

Paste:

```
Yes. I can commit 15–20 hours/week for 3–6 months (extendable). Earliest start: 18 August 2026.

Timezone: Asia/Almaty (UTC+5). I am available only after 17:30 Almaty on weekdays (≈ 12:30 UTC / 13:30 London / 08:30 US Eastern), plus weekends. Delivery is async-first; I can join 2–3 short calls per week inside that window. I am not available before 17:30 Almaty or for a full overlapping US/EU workday.
```

---

## 12. Data Privacy Notice * (checkbox)

**Check the box.** Open “View Privacy Notice” if you want to skim it; it is required to submit.

---

## Availability cheat sheet (Almaty = UTC+5)

You said **after 17:30 Almaty only**. That maps to:

| Almaty | London (BST) | US Eastern (EDT) |
|---|---|---|
| 17:30 | 13:30 | 08:30 |
| 19:00 | 15:00 | 10:00 |
| 21:00 | 17:00 | 12:00 |
| 23:00 | 19:00 | 14:00 |

Best call window to offer: **17:30–20:00 Almaty** (US morning 08:30–11:00 / EU early afternoon).

---

## Submit

Click **Submit Application**. You should get a Breezy confirmation email at gmail.

If they reply, ask: *Are the 15–20 hours a hard cap, and can standups sit after 17:30 Almaty (08:30 US Eastern)?*  
If they need daily meetings before 17:30 Almaty, decline — that collides with Air Astana.
