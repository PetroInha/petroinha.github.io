---
layout: page
title: EnergyInsight
permalink: /EnergyInsight/
---

<style>
.eng-hero{background:linear-gradient(135deg,#002F6C,#005BAC);color:white;padding:34px 32px 28px;border-radius:18px;margin-bottom:26px;box-shadow:0 14px 40px rgba(0,0,0,0.16);position:relative;overflow:hidden;}
.eng-hero::before{content:"";position:absolute;top:-60px;right:-60px;width:220px;height:220px;background:rgba(255,255,255,0.05);border-radius:50%;}
.eng-hero h2{margin:0 0 8px;font-size:22px;font-weight:800;position:relative;z-index:1;}
.eng-hero p{margin:0;font-size:14px;opacity:0.88;line-height:1.7;position:relative;z-index:1;max-width:640px;}

.eng-tags{display:flex;flex-wrap:wrap;gap:8px;margin-top:16px;position:relative;z-index:1;}
.eng-tag{background:rgba(255,255,255,0.13);border:1px solid rgba(255,255,255,0.22);border-radius:20px;padding:4px 12px;font-size:11.5px;font-weight:600;}

.eng-frame-wrap{border:1px solid #e3e9f2;border-radius:14px;overflow:hidden;box-shadow:0 8px 26px rgba(0,0,0,0.07);background:#fff;}
.eng-frame-wrap iframe{display:block;width:100%;height:2100px;border:0;}

.eng-bar{display:flex;flex-wrap:wrap;gap:10px;align-items:center;justify-content:space-between;margin:14px 0 30px;font-size:12.5px;color:#77839a;}
.eng-bar a{color:#005BAC;font-weight:600;text-decoration:none;}
.eng-bar a:hover{text-decoration:underline;}

.eng-how{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:14px;margin:26px 0 10px;}
.eng-step{background:#f7f9fc;border:1px solid #e8eef6;border-left:3px solid #005BAC;border-radius:0 10px 10px 0;padding:15px 17px;}
.eng-step b{display:block;color:#005BAC;font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:.6px;margin-bottom:6px;}
.eng-step span{font-size:13px;line-height:1.65;color:#42505f;}

.eng-note{margin-top:24px;padding:14px 16px;background:#fff8e6;border-left:3px solid #d9a300;border-radius:0 8px 8px 0;font-size:13px;line-height:1.75;color:#6b5400;}

@media(max-width:900px){
  .eng-hero{padding:26px 20px;}
  .eng-frame-wrap iframe{height:1600px;}
}
</style>

<div class="eng-hero">
  <h2>Energy Market Monitor</h2>
  <p>A daily snapshot of the prices and macro drivers our CO₂ storage, hydrogen and unconventional-resource work depends on — crude and gas benchmarks alongside the dollar, rates, volatility and carbon — with a random-forest P10/P50/P90 outlook for the week ahead.</p>
  <div class="eng-tags">
    <span class="eng-tag">WTI · Brent · Dubai</span>
    <span class="eng-tag">Henry Hub</span>
    <span class="eng-tag">DXY · UST10Y · OVX</span>
    <span class="eng-tag">EIA fundamentals</span>
    <span class="eng-tag">Random Forest P10/P50/P90</span>
  </div>
</div>

<div class="eng-frame-wrap">
  <iframe src="{{ '/_images/energy_stats.html' | relative_url }}"
          title="CURE Energy Market Monitor"
          loading="lazy"></iframe>
</div>

<div class="eng-bar">
  <span>Interactive — hover for values, drag to zoom, double-click to reset.</span>
  <a href="{{ '/_images/energy_stats.html' | relative_url }}" target="_blank">Open full screen ↗</a>
</div>

### How this dashboard is built

<div class="eng-how">
  <div class="eng-step">
    <b>1 · Collect</b>
    <span>Daily bars from Yahoo Finance for tradable contracts; rates, the trade-weighted dollar and EIA fundamentals from the St. Louis Fed's FRED. Each source is fetched independently, so one outage degrades the dashboard instead of breaking it.</span>
  </div>
  <div class="eng-step">
    <b>2 · Align</b>
    <span>Everything is resampled onto a business-day grid. Weekly and monthly statistics are forward-filled — the last published print genuinely is the market's best information until the next release.</span>
  </div>
  <div class="eng-step">
    <b>3 · Engineer</b>
    <span>Per indicator: 1/3/5/10-day changes normalised by 60-day realised volatility, plus a 60-day level z-score. Differences rather than log returns, so yields and real rates stay defined when they go negative.</span>
  </div>
  <div class="eng-step">
    <b>4 · Fit</b>
    <span>A 500-tree random forest maps today's full cross-market state onto the log price change five trading days ahead. It trains on four years of history — not the one month plotted, which is far too little to fit a forest on.</span>
  </div>
  <div class="eng-step">
    <b>5 · Quantify</b>
    <span>A five-fold walk-forward split produces out-of-sample residuals. P10/P50/P90 are percentiles of the point forecast plus that empirical residual distribution — wider and more honest than the spread of the trees alone.</span>
  </div>
  <div class="eng-step">
    <b>6 · Publish</b>
    <span>Rendered to an interactive Plotly page with crude and gas given the top two rows, then committed and pushed. Re-run <code>_script/gather_energy_stats.py</code> to refresh.</span>
  </div>
</div>

<div class="eng-note">
  <b>Read the bands as uncertainty, not as a view.</b> The P10/P50/P90 range describes how wrong this one model has historically been over a one-week horizon. It assumes next week resembles the training period, and it will be wrong precisely when that assumption breaks — which is usually when it matters. Nothing here is investment advice. Full source list, per-indicator coverage and caveats are printed at the bottom of the dashboard itself.
</div>

**References** — Yahoo Finance · [FRED, Federal Reserve Bank of St. Louis](https://fred.stlouisfed.org/) · [U.S. Energy Information Administration](https://www.eia.gov/) · [Baker Hughes Rig Count](https://rigcount.bakerhughes.com/) · Breiman, L. (2001). Random Forests. *Machine Learning*, 45(1), 5–32.
