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
.eng-frame-wrap iframe{display:block;width:100%;height:1736px;border:0;}

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
  .eng-frame-wrap iframe{height:1736px;}
}
</style>

<div class="eng-hero">
  <h2>Energy Market Monitor</h2>
  <p>Three months of the prices and macro drivers our CO₂ storage, hydrogen and unconventional-resource work depends on — crude and gas benchmarks alongside the dollar, the Treasury and TIPS curves, volatility and carbon — with a gradient-boosted P10/P50/P90 outlook for the week ahead pinned to the top of the chart, and every past call scored against what actually printed.</p>
  <div class="eng-tags">
    <span class="eng-tag">WTI · Brent</span>
    <span class="eng-tag">Henry Hub</span>
    <span class="eng-tag">OVX · RBOB</span>
    <span class="eng-tag">UST &amp; TIPS curves</span>
    <span class="eng-tag">DXY · Broad TW USD</span>
    <span class="eng-tag">LightGBM P10/P50/P90</span>
    <span class="eng-tag">Direction F1 scorecard</span>
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
  <span><b>All panels share one time axis</b> — drag to pan, scroll to zoom, double-click to reset, and every other chart follows. Opens on the last three months plus the forecast week; pan left for more history.</span>
  <a href="{{ '/_images/energy_stats.html' | relative_url }}" target="_blank">Open full screen ↗</a>
</div>

### Track record — the stars

Every run logs its full forecast before anything is drawn. Once a predicted day's close prints, that run's **next-day P50** appears as a star on the candle it was predicting — hover for the predicted and actual moves, the price error, and whether that star is a live call or a backtested one.

The colour scores the **direction**, not the price. Read each call as a daily long/short: go long if the model says tomorrow closes above today, short if below.

- <b style="color:#b38600">★ gold</b> — the direction was right. The trade made money.
- <b style="color:#123a6b">★ navy</b> — the direction was wrong. The trade lost.

Next to each P10/P50/P90 line at the top of the chart is that contract's **direction F1**, with the hit rate, the number of scored calls, and the mean absolute price error. F1 is used rather than raw accuracy on purpose: "up" is the positive class, so a model that simply calls up every day can post a flattering hit rate in a rising market while F1 exposes it. Roughly 0.5 is a coin flip.

The <b style="color:#c0392b">red band</b> marks the backtested window, and the bold red number in the middle of it is what a **daily long/short** would have been worth over that stretch: go long one unit when the model calls up, short one unit when it calls down, hold a day, compound. **100% is break-even** — 110% means the stake grew a tenth, 90% means it lost one. It is frictionless, with no spread, financing or slippage, so read it as a ceiling on what the signal is worth rather than an achievable return.

**Where the stars come from.** The chart is seeded with a **walk-forward backtest** over the preceding 30 trading days. For each of those days the panel is truncated to that date before the model is fitted, validated and simulated, so it never sees the bar it is predicting — there is no lookahead in the training. But those rows were still generated after the fact, so they are tagged `backtest` and are not the same thing as a call made in advance. Every subsequent run appends genuine live predictions on top, which are tagged `live` and can never be overwritten by a later replay. Over time the record becomes predominantly live.


### How the one-week forecast is produced

The model is a **LightGBM** gradient-boosted tree ensemble. It never predicts a week directly: it learns a **single one-day step** — given the contract's last **14 trading days** of volatility-scaled returns plus the current state of every other indicator on this page, what is tomorrow's log price change? — and is then applied **recursively**: predict tomorrow, append that price to the history, re-derive the 14-day window from the extended series, and predict again, five times over to reach a week.

Hyperparameters are found by randomised search over a **forward-chaining, gapped** time-series split: every validation fold sits strictly later than the data it was trained on, with a 14-day gap between them so a validation row's trailing window cannot overlap rows the model has already seen. The search is scored on **directional accuracy** rather than R², because daily-return R² hovers near zero and barely separates candidates, while direction is what the scorecard measures. The winning settings are cached with the date they were found and reused for a week before the search runs again, so the model tracks a drifting market without paying for a search on every run.

Uncertainty is generated the same way. At each step a residual is drawn at random from the model's own walk-forward out-of-sample errors, and **2,000 independent paths** are simulated. The P10/P50/P90 fan on the crude and gas panels is the 10th/50th/90th percentile of those paths at each day, so the band widens with horizon because the errors genuinely compound — not because a widening was imposed on it.

Two limits are worth stating plainly. The other indicators are **held fixed** through the rollout: the dollar, the curve and volatility are not themselves forecast, so the fan answers "where does this contract drift if the rest of the market stands still", not "what will happen". And because each step feeds on its own output, any bias in the one-day model accumulates rather than cancels.

<div class="eng-note">
  <b>Read the bands as uncertainty, not as a view.</b> The P10/P50/P90 range describes how wrong this one model has historically been. It assumes next week resembles the training period, and it will be wrong precisely when that assumption breaks — which is usually when it matters.
  <br><br>
  <b>Series caveats.</b> EUA carbon is proxied by the KRBN ETF, not the ICE EUA futures settlement. FRED publishes TIPS yields from 5 years out — there is no 2-year real rate — so the short leg of the real-yield panel is 5Y, labelled as such in the panel's colour key.
  <br><br>
  <b>No warranty and no responsibility.</b> This page is produced automatically from third-party data for internal research interest only. It is <b>not</b> investment, trading, financial or commercial advice, and it is not a recommendation to buy, sell or hold anything. The underlying data may be delayed, revised, incomplete or simply wrong, and the model output is a statistical extrapolation that carries no guarantee of accuracy. CURE, Inha University and the authors accept <b>no liability whatsoever</b> for any loss or damage arising from any use of, or reliance on, this page or its forecasts. Use it at your own risk, and verify anything that matters against the primary sources below.
</div>

**References** — Yahoo Finance · [FRED, Federal Reserve Bank of St. Louis](https://fred.stlouisfed.org/) · [U.S. Energy Information Administration](https://www.eia.gov/) · Ke, G., et al. (2017). LightGBM: A Highly Efficient Gradient Boosting Decision Tree. *NeurIPS 30*.
