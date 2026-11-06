const WATCHLIST = {
  RELIANCE: { market:"india", ticker:"RELIANCE.NS", name:"Reliance Industries" },
  TCS: { market:"india", ticker:"TCS.NS", name:"Tata Consultancy Services" },
  TATASTEEL: { market:"india", ticker:"TATASTEEL.NS", name:"Tata Steel" },
  TATAMOTORS: { market:"india", ticker:"TATAMOTORS.NS", name:"Tata Motors" },
  BTCUSDT: { market:"crypto", ticker:"BTCUSDT", name:"Bitcoin" },
  ETHUSDT: { market:"crypto", ticker:"ETHUSDT", name:"Ethereum" }
};
const TIMEFRAMES = {
  "5m": { yahoo:"5m", binance:"5m", range:"5d" },
  "15m": { yahoo:"15m", binance:"15m", range:"1mo" },
  "1H": { yahoo:"60m", binance:"1h", range:"3mo" },
  "1D": { yahoo:"1d", binance:"1d", range:"5y" }
};
const send = (res, status, body) => res.status(status).json(body);
async function fetchYahoo(ticker, tf) {
  const cfg = TIMEFRAMES[tf];
  const url = new URL("https://query1.finance.yahoo.com/v8/finance/chart/" + encodeURIComponent(ticker));
  url.search = new URLSearchParams({ range:cfg.range, interval:cfg.yahoo });
  const response = await fetch(url, { headers:{ "user-agent":"Mozilla/5.0 AURA-AI/1.0" } });
  if (!response.ok) throw new Error("Yahoo Finance HTTP " + response.status);
  const payload = await response.json(), result = payload?.chart?.result?.[0];
  if (!result) throw new Error(payload?.chart?.error?.description || "Yahoo Finance returned no candles");
  const q = result.indicators.quote[0];
  return (result.timestamp || []).map((t,i)=>({
    time:t, open:q.open[i], high:q.high[i], low:q.low[i], close:q.close[i], volume:q.volume[i] || 0
  })).filter(c=>[c.open,c.high,c.low,c.close].every(Number.isFinite));
}
async function fetchBinance(ticker, tf) {
  const url = new URL("https://api.binance.com/api/v3/klines");
  url.search = new URLSearchParams({ symbol:ticker, interval:TIMEFRAMES[tf].binance, limit:"500" });
  const response = await fetch(url);
  if (!response.ok) throw new Error("Binance API HTTP " + response.status);
  const rows = await response.json();
  return rows.map(k=>({ time:Math.floor(k[0]/1000), open:+k[1], high:+k[2], low:+k[3], close:+k[4], volume:+k[5] }));
}
export default async function handler(req,res) {
  if (req.method !== "GET") return send(res,405,{error:"Method not allowed"});
  const symbol = String(req.query.symbol || "BTCUSDT").toUpperCase();
  const timeframe = String(req.query.tf || "5m");
  const item = WATCHLIST[symbol];
  if (!item || !TIMEFRAMES[timeframe]) return send(res,400,{error:"Unsupported symbol or timeframe",supported_symbols:Object.keys(WATCHLIST),supported_timeframes:Object.keys(TIMEFRAMES)});
  try {
    const candles = item.market === "crypto" ? await fetchBinance(item.ticker,timeframe) : await fetchYahoo(item.ticker,timeframe);
    if (!candles.length) throw new Error("Provider returned an empty candle series");
    const latest = candles[candles.length-1];
    res.setHeader("Cache-Control","s-maxage=20, stale-while-revalidate=40");
    return send(res,200,{symbol,timeframe,market:item.market,name:item.name,source:item.market==="crypto"?"Binance public market data":"Yahoo Finance chart endpoint (unofficial, best-effort)",updated_at:new Date().toISOString(),last_candle_time:latest.time,count:candles.length,candles});
  } catch(error) {
    return send(res,502,{error:error.message,symbol,timeframe,source:item.market==="crypto"?"Binance":"Yahoo Finance",hint:"Provider may be temporarily unavailable or rate-limited. Retry shortly."});
  }
}