const WATCHLIST = {
  "RELIANCE": { market: "india", yahoo: "RELIANCE.NS", name: "Reliance Industries" },
  "TCS": { market: "india", yahoo: "TCS.NS", name: "Tata Consultancy Services" },
  "TATASTEEL": { market: "india", yahoo: "TATASTEEL.NS", name: "Tata Steel" },
  "TATAMOTORS": { market: "india", yahoo: "TATAMOTORS.NS", name: "Tata Motors" },
  "BTCUSDT": { market: "crypto", binance: "BTCUSDT", name: "Bitcoin" },
  "ETHUSDT": { market: "crypto", binance: "ETHUSDT", name: "Ethereum" }
};
const TF = { "5m": "5m", "15m": "15m", "1H": "60m", "1D": "1d" };
const json = (data, status = 200) => new Response(JSON.stringify(data), {
  status, headers: { "content-type": "application/json; charset=utf-8", "access-control-allow-origin": "*", "cache-control": "no-store" }
});
function normalizeYahoo(payload) {
  const r = payload?.chart?.result?.[0];
  if (!r) throw new Error(payload?.chart?.error?.description || "Yahoo Finance returned no data");
  const q = r.indicators.quote[0], adj = r.indicators.adjclose?.[0]?.adjclose || [];
  return (r.timestamp || []).map((t, i) => ({
    time: t, open: q.open[i], high: q.high[i], low: q.low[i], close: q.close[i],
    volume: q.volume[i] || 0
  })).filter(x => [x.open,x.high,x.low,x.close].every(Number.isFinite));
}
async function fetchCandles(symbol, timeframe) {
  const item = WATCHLIST[symbol], interval = TF[timeframe];
  if (!item || !interval) throw new Error("Unsupported symbol or timeframe");
  if (item.market === "crypto") {
    const url = new URL("https://api.binance.com/api/v3/klines");
    url.search = new URLSearchParams({ symbol: item.binance, interval: interval === "60m" ? "1h" : interval, limit: "500" });
    const res = await fetch(url, { headers: { "user-agent": "AURA-Market-Engine/1.0" } });
    if (!res.ok) throw new Error("Binance API HTTP " + res.status);
    const rows = await res.json();
    return rows.map(k => ({ time: Math.floor(k[0]/1000), open:+k[1], high:+k[2], low:+k[3], close:+k[4], volume:+k[5] }));
  }
  const range = interval === "5m" ? "5d" : interval === "15m" ? "1mo" : interval === "60m" ? "3mo" : "5y";
  const url = new URL("https://query1.finance.yahoo.com/v8/finance/chart/" + item.yahoo);
  url.search = new URLSearchParams({ range, interval });
  const res = await fetch(url, { headers: { "user-agent": "Mozilla/5.0 AURA/1.0" } });
  if (!res.ok) throw new Error("Yahoo Finance HTTP " + res.status);
  return normalizeYahoo(await res.json());
}
async function saveCandles(db, symbol, timeframe, rows, source) {
  if (!db || !rows.length) return;
  const stmts = rows.map(c => db.prepare(
    "INSERT INTO candles(symbol,timeframe,time,open,high,low,close,volume,source,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?) ON CONFLICT(symbol,timeframe,time) DO UPDATE SET open=excluded.open,high=excluded.high,low=excluded.low,close=excluded.close,volume=excluded.volume,source=excluded.source,updated_at=excluded.updated_at"
  ).bind(symbol,timeframe,c.time,c.open,c.high,c.low,c.close,c.volume,source,Math.floor(Date.now()/1000)));
  for (let i=0;i<stmts.length;i+=80) await db.batch(stmts.slice(i,i+80));
}
async function readCandles(db, symbol, timeframe, limit=500) {
  if (!db) return [];
  const r = await db.prepare("SELECT time,open,high,low,close,volume FROM candles WHERE symbol=? AND timeframe=? ORDER BY time DESC LIMIT ?")
    .bind(symbol,timeframe,limit).all();
  return (r.results || []).reverse();
}
async function handle(request, env) {
  const url = new URL(request.url);
  if (request.method === "OPTIONS") return new Response(null, { headers: { "access-control-allow-origin":"*", "access-control-allow-methods":"GET,OPTIONS", "access-control-allow-headers":"content-type" } });
  if (url.pathname === "/api/health") return json({ app:"AURA AI", status:"online", storage:!!env.DB, providers:["Binance public API","Yahoo Finance chart (best-effort)"], watchlist:Object.keys(WATCHLIST), server_time:new Date().toISOString() });
  if (url.pathname === "/api/watchlist") return json(Object.entries(WATCHLIST).map(([symbol,v])=>({symbol,...v})));
  if (url.pathname === "/api/candles") {
    const symbol = (url.searchParams.get("symbol") || "BTCUSDT").toUpperCase();
    const timeframe = url.searchParams.get("tf") || "5m";
    if (!WATCHLIST[symbol] || !TF[timeframe]) return json({error:"Unsupported symbol/timeframe"},400);
    try {
      let candles = await readCandles(env.DB, symbol, timeframe, 500);
      let source = WATCHLIST[symbol].market === "crypto" ? "Binance public API" : "Yahoo Finance (best-effort)";
      if (candles.length < 30 || Date.now()/1000 - candles[candles.length-1].time > (timeframe==="1D"?86400:timeframe==="1H"?7200:1800)) {
        candles = await fetchCandles(symbol,timeframe);
        await saveCandles(env.DB,symbol,timeframe,candles,source);
      }
      return json({symbol,timeframe,source,updated_at:new Date().toISOString(),count:candles.length,candles});
    } catch (e) {
      if (candles?.length) return json({symbol,timeframe,source:"D1 cached fallback",warning:e.message,count:candles.length,candles});
      return json({error:e.message,source:WATCHLIST[symbol].market==="crypto"?"Binance":"Yahoo Finance"},502);
    }
  }
  if (env.ASSETS) return env.ASSETS.fetch(request);
  return json({error:"Not found"},404);
}
async function collect(env) {
  if (!env.DB) return;
  const jobs = Object.entries(WATCHLIST).map(async ([symbol,item]) => {
    try {
      const rows = await fetchCandles(symbol,"5m");
      await saveCandles(env.DB,symbol,"5m",rows,item.market==="crypto"?"Binance public API":"Yahoo Finance (best-effort)");
    } catch (e) { console.log("Collector error",symbol,e.message); }
  });
  await Promise.allSettled(jobs);
}
export default {
  fetch: handle,
  scheduled: async (_event, env, ctx) => { ctx.waitUntil(collect(env)); }
};