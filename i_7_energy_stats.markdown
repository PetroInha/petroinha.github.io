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
/* Fallback height only — the script below resizes the frame to its content. */
.eng-frame-wrap iframe{display:block;width:100%;height:1196px;border:0;}

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
  .eng-frame-wrap iframe{height:1196px;}
}
</style>

<div class="eng-hero">
  <h2>Energy Market Monitor</h2>
  <p>Three months of the prices and macro drivers our CO₂ storage, hydrogen and unconventional-resource work depends on — crude and gas benchmarks alongside the dollar, the Treasury and TIPS curves, volatility and carbon — with a random-forest P10/P50/P90 outlook for the week ahead pinned to the top of the chart.</p>
  <div class="eng-tags">
    <span class="eng-tag">WTI · Brent · Dubai</span>
    <span class="eng-tag">Henry Hub</span>
    <span class="eng-tag">OVX · RBOB</span>
    <span class="eng-tag">UST &amp; TIPS curves</span>
    <span class="eng-tag">DXY · Broad TW USD</span>
    <span class="eng-tag">Random Forest P10/P50/P90</span>
  </div>
</div>

<div class="eng-frame-wrap">
  <iframe id="eng-frame"
          src="{{ '/_images/energy_stats.html' | relative_url }}"
          title="CURE Energy Market Monitor"
          loading="lazy"></iframe>
</div>

<script>
// The frame sizes itself to its content two ways: the dashboard posts its
// height on load (see SIZE_JS in gather_energy_stats.py), and as a backstop we
// read it directly, which works because both are served from this origin. The
// CSS height is written by the generator to match the figure exactly, so the
// first paint is already correct and neither path causes a visible jump.
(function () {
  var f = document.getElementById('eng-frame');
  if (!f) return;

  function apply(h) {
    if (h > 400) f.style.height = h + 'px';
  }

  window.addEventListener('message', function (ev) {
    if (ev.data && typeof ev.data.cureEnergyHeight === 'number') {
      apply(ev.data.cureEnergyHeight);
    }
  });

  function fit() {
    try {
      var d = f.contentDocument || f.contentWindow.document;
      apply(Math.max(d.body.scrollHeight, d.documentElement.scrollHeight));
    } catch (e) { /* keep whatever height we already have */ }
  }

  f.addEventListener('load', function () {
    fit();
    // Plotly lays out asynchronously; re-measure once it has settled.
    setTimeout(fit, 400);
    setTimeout(fit, 1500);
  });
  window.addEventListener('resize', fit);
})();
</script>

<div class="eng-bar">
  <span><b>All panels share one time axis</b> — drag to pan, scroll to zoom, double-click to reset, and every other chart follows.</span>
  <a href="{{ '/_images/energy_stats.html' | relative_url }}" target="_blank">Open full screen ↗</a>
</div>

### How this dashboard is built

<div class="eng-how">
  <div class="eng-step">
    <b>1 · Collect</b>
    <span>Three months of daily bars from Yahoo Finance for tradable contracts; the Treasury and TIPS curves and the trade-weighted dollar from the St. Louis Fed's FRED. Each source is fetched independently, so one outage degrades the dashboard instead of breaking it.</span>
  </div>
  <div class="eng-step">
    <b>2 · Align</b>
    <span>Everything is resampled onto a business-day grid. Lower-frequency series are forward-filled — the last published print genuinely is the market's best information until the next release.</span>
  </div>
  <div class="eng-step">
    <b>3 · Engineer</b>
    <span>The contract's own <b>last 14 trading days</b> of returns, volatility-scaled, plus momentum and level z-scores. For every other indicator: 1/3/5/10-day changes and a 60-day level z-score — differences rather than log returns, so yields and real rates stay defined when they go negative.</span>
  </div>
  <div class="eng-step">
    <b>4 · Fit</b>
    <span>A 500-tree random forest maps that 14-day window plus the cross-market state onto <b>tomorrow's</b> log price change — a single one-day step, not a five-day jump. It trains on four years of history; the three months plotted would be far too little.</span>
  </div>
  <div class="eng-step">
    <b>5 · Roll forward</b>
    <span>The one-day model is applied <b>recursively</b>: predict tomorrow, append that price, re-derive the 14-day window, predict again — five times. Each step adds a residual drawn from the model's own out-of-sample errors, and 2,000 such paths are simulated, so uncertainty compounds with horizon instead of being assumed.</span>
  </div>
  <div class="eng-step">
    <b>6 · Publish</b>
    <span>Crude and gas take the top row side by side; related indicators are grouped three panels to a row, sharing a second y-axis where their levels differ too much to plot together. Every x-axis is matched, so the panels pan and zoom as one. Re-run <code>_script/gather_energy_stats.py</code> to refresh.</span>
  </div>
</div>

### How the one-week forecast is produced

The model never predicts a week directly. It learns a **single one-day step** — given the contract's last **14 trading days** of volatility-scaled returns plus the current state of every other indicator on this page, what is tomorrow's log price change? — and is then applied **recursively**: predict tomorrow, append that price to the history, re-derive the 14-day window from the extended series, and predict again, five times over to reach a week.

Uncertainty is generated the same way. At each step a residual is drawn at random from the model's own walk-forward out-of-sample errors, and **2,000 independent paths** are simulated. The P10/P50/P90 fan on the crude and gas panels is the 10th/50th/90th percentile of those paths at each day, so the band widens with horizon because the errors genuinely compound — not because a widening was imposed on it.

Two limits are worth stating plainly. The other indicators are **held fixed** through the rollout: the dollar, the curve and volatility are not themselves forecast, so the fan answers "where does this contract drift if the rest of the market stands still", not "what will happen". And because each step feeds on its own output, any bias in the one-day model accumulates rather than cancels.

<div class="eng-note">
  <b>Read the bands as uncertainty, not as a view.</b> The P10/P50/P90 range describes how wrong this one model has historically been. It assumes next week resembles the training period, and it will be wrong precisely when that assumption breaks — which is usually when it matters.
  <br><br>
  <b>Series caveats.</b> Dubai crude has no free daily feed — no public source publishes it daily — so the daily Dubai line is <b>reconstructed</b> as Brent plus the interpolated monthly Dubai−Brent spread. Its day-to-day shape is Brent's; only its level is Dubai's. The true monthly prints are overlaid as open circles, and the reconstruction is excluded from the forecast model. EUA carbon is proxied by the KRBN ETF, not the ICE EUA futures settlement. FRED publishes TIPS yields from 5 years out — there is no 2-year real rate — so the short leg of the real-yield panel is 5Y, labelled as such in the panel's colour key.
  <br><br>
  <b>No warranty and no responsibility.</b> This page is produced automatically from third-party data for internal research interest only. It is <b>not</b> investment, trading, financial or commercial advice, and it is not a recommendation to buy, sell or hold anything. The underlying data may be delayed, revised, incomplete or simply wrong, and the model output is a statistical extrapolation that carries no guarantee of accuracy. CURE, Inha University and the authors accept <b>no liability whatsoever</b> for any loss or damage arising from any use of, or reliance on, this page or its forecasts. Use it at your own risk, and verify anything that matters against the primary sources below.
</div>

**References** — Yahoo Finance · [FRED, Federal Reserve Bank of St. Louis](https://fred.stlouisfed.org/) · [U.S. Energy Information Administration](https://www.eia.gov/) · Breiman, L. (2001). Random Forests. *Machine Learning*, 45(1), 5–32.
