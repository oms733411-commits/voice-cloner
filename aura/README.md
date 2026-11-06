# AURA AI — Vercel deployment

AURA is an isolated dashboard inside `oms733411-commits/voice-cloner`. Existing Voice Cloner files are not modified.

## Deploy on Vercel
1. Open https://vercel.com/new and import `oms733411-commits/voice-cloner`.
2. Set **Root Directory** to `aura`.
3. Framework preset: **Other**. Leave Build Command and Output Directory empty.
4. Deploy. Open the deployment URL; health endpoint: `/api/health`.

## Automated data fetching
The dashboard requests candles from `/api/candles` when a symbol/timeframe is selected and refreshes the active chart periodically. Vercel's CDN caches responses briefly to reduce provider calls.

- Crypto: Binance public REST market-data API, no API key for public klines.
- Indian stocks: Yahoo Finance chart endpoint, unofficial best-effort data. It can be delayed, rate-limited or changed without notice.
- Symbols: RELIANCE, TCS, TATASTEEL, TATAMOTORS, BTCUSDT, ETHUSDT.
- Timeframes: 5m, 15m, 1H, 1D.

## Important free-plan limitation
This Vercel deployment does not run a permanent background collector or persist candles to a database. Dashboard requests fetch current historical candle windows on demand; CDN caching reduces repeated requests. Vercel Hobby Cron Jobs are limited to once per day, so they cannot replace a five-minute collector. For persistent history and frequent scheduled ingestion, connect a database and an external scheduler or use a provider with an appropriate free streaming plan.

## Accuracy and safety
- Provider timestamps are Unix seconds; candle values are validated before returning.
- If a provider fails, API returns an error; the dashboard hides signals rather than inventing data.
- Technical scores are evidence scores, not win probabilities.
- This is a prototype, not investment advice. Verify market data, exchange terms, and licensing before relying on or redistributing it.
- No API keys or paid credentials are required by this initial implementation.