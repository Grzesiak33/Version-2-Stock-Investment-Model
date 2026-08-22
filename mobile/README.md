# AI Stocks Made Simple — Mobile v3.0

Version 3 separates the consumer mobile experience from the Python investment engine.

## Architecture

- `mobile/` — React Native + Expo consumer application for Android/iOS (and web preview).
- Existing Python project — ranking/model engine and Streamlit admin/prototype dashboard.
- Next API layer — exposes rankings, current prices and simulation math to the mobile app.

## Preview on a phone

1. Install Node.js on the development computer.
2. Install the Expo Go app on the Android/iPhone used for previewing.
3. In a terminal: `cd mobile`
4. Run `npm install`
5. Run `npx expo start`
6. Scan the displayed QR code with the phone and open it in Expo Go.

## Hosting

React Native itself is not hosted by Streamlit. Streamlit can remain the free Python/admin dashboard. During development, Expo Go provides the easiest phone preview. A web build can later be hosted separately on a static host. The Python API can be deployed independently on a free/low-cost service subject to that provider's current limits.

## v3.0 UI included

- Neon beginner-first hero
- Mobile stock selection cards
- Deposit quick picks and custom amount
- Weekly/payday/monthly cadence
- End-date projection
- Contribution and fractional-share simulation
- Beginner education cards

## Next integration milestone

Replace the temporary in-app stock sample array with API calls to the existing Python Top-20 ranking data and live-price service. The model remains Python; React Native is the presentation layer.
