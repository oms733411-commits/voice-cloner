export default function handler(req,res) {
  res.setHeader("Cache-Control","no-store");
  res.status(200).json({
    app:"AURA AI",
    status:"online",
    deployment:"Vercel serverless",
    data_sources:{
      crypto:"Binance public REST API",
      indian_equities:"Yahoo Finance chart endpoint; unofficial and best-effort"
    },
    supported_symbols:["RELIANCE","TCS","TATASTEEL","TATAMOTORS","BTCUSDT","ETHUSDT"],
    supported_timeframes:["5m","15m","1H","1D"],
    collection_mode:"Fetch on dashboard request with short CDN cache; no persistent database configured",
    server_time:new Date().toISOString()
  });
}