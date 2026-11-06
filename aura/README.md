# AURA AI — automated market data engine

AURA is being added as an isolated app inside the existing `oms733411-commits/voice-cloner` repository. Existing voice-cloner pages and APIs are not modified.

## Current data adapters
- Crypto: Binance public REST klines. No API key is needed for public market data.
- Indian equities: Yahoo Finance chart endpoint as a best-effort free source. This is unofficial, may be delayed/rate-limited, and is not an exchange-guaranteed feed.
- Watchlist: RELIANCE, TCS, TATASTEEL, TATAMOTORS, BTCUSDT, ETHUSDT.
- Timeframes exposed: 5m, 15m, 1H, 1D. 4H/1W aggregation and additional symbols are planned.

## Deploy on Cloudflare (free tier, subject to current quotas)
1. Install Wrangler and log in: `npx wrangler login`.
2. From this folder create the database: `npx wrangler d1 create aura-market-db`.
3. Copy the returned database_id into `wrangler.toml`.
4. Initialize schema: `npx wrangler d1 execute aura-market-db --file=./schema.sql`.
5. Deploy: `npx wrangler deploy`.
6. Open the Worker URL. The dashboard is served at the root; API health is at `/api/health`.

The five-minute Cron Trigger collects the configured 5m watchlist into D1. The API can fetch on demand and uses cached candles as a fallback. A D1 binding is required for persistence and scheduled collection.

## Local preview
From this directory: `npx wrangler dev`. Configure D1 locally using Wrangler's local D1 workflow.

## Important limitations
- This is a data-pipeline foundation, not a guaranteed real-time exchange terminal.
- Yahoo Finance is an unofficial best-effort source for Indian equities. If it rate-limits or changes, the dashboard reports the error instead of inventing candles.
- Binance public market data is used for crypto; exchange availability and regional access can vary.
- Strategy scores are rule-based evidence scores, not win probabilities. The current dashboard's AI panel is explicitly a transparent heuristic placeholder, not a trained ML model.
- Validate source licensing/terms before redistributing market data or using it commercially.
- No broker credentials, API secrets, or paid data services are required by this initial build.