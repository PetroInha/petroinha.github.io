---
layout: post
title: "Open Porous Media Short Course with Prof. Carl Fredrik Berg (NTNU)"
date: 2026-06-16 18:00:00 +0900
categories: jekyll update
---

<style>
.post-hero{background:linear-gradient(135deg,#002F6C,#005BAC,#1565C0,#003E82);background-size:300% 300%;animation:gradShift 14s ease infinite;color:white;padding:52px 40px;border-radius:18px;margin-bottom:36px;box-shadow:0 20px 48px rgba(0,0,0,0.20);position:relative;overflow:hidden;}
.post-hero::before{content:"";position:absolute;top:-50px;right:-50px;width:200px;height:200px;background:rgba(255,255,255,0.06);border-radius:50%;}
@keyframes gradShift{0%{background-position:0% 50%;}50%{background-position:100% 50%;}100%{background-position:0% 50%;}}
.post-hero h2{margin:0 0 10px 0;font-size:28px;font-weight:800;position:relative;z-index:1;}
.post-hero p{margin:0;font-size:15px;line-height:1.7;opacity:0.92;max-width:800px;position:relative;z-index:1;}
.post-chips{display:flex;flex-wrap:wrap;gap:12px;margin-top:22px;position:relative;z-index:1;}
.post-chip{background:rgba(255,255,255,0.18);border:1px solid rgba(255,255,255,0.25);padding:7px 16px;border-radius:999px;font-size:13px;font-weight:600;}
.data-flow{height:2px;background:linear-gradient(90deg,transparent,#005BAC,transparent);background-size:200% 100%;animation:dataFlow 4s linear infinite;margin:32px 0;}
@keyframes dataFlow{0%{background-position:200% 0;}100%{background-position:-200% 0;}}
.photo-featured{border-radius:16px;overflow:hidden;box-shadow:0 16px 40px rgba(0,0,0,0.18);margin:28px 0;}
.photo-featured img{width:100%;display:block;transition:transform .4s ease;}
.photo-featured:hover img{transform:scale(1.02);}
.photo-caption{background:#f7f9fc;padding:14px 20px;font-size:13px;color:#555;font-style:italic;border-top:1px solid #e4eaf2;}
.sec-head{display:flex;align-items:center;gap:12px;margin:36px 0 18px 0;}
.sec-num{flex:0 0 auto;width:34px;height:34px;border-radius:9px;background:#005BAC;color:white;display:flex;align-items:center;justify-content:center;font-size:14px;font-weight:800;}
.sec-head h3{margin:0;font-size:20px;font-weight:800;color:#111;}
.expert{background:white;border-radius:16px;box-shadow:0 10px 30px rgba(0,0,0,0.10);padding:28px 30px;margin:24px 0;border-left:6px solid #005BAC;}
.expert-name{font-size:20px;font-weight:800;color:#111;margin:0 0 4px 0;}
.expert-aff{font-size:13.5px;color:#005BAC;font-weight:600;margin:0 0 16px 0;}
.expert p{font-size:14px;line-height:1.8;color:#333;margin:0 0 12px 0;}
.expert p:last-child{margin-bottom:0;}
.expert-tags{display:flex;flex-wrap:wrap;gap:8px;margin-top:16px;}
.expert-tag{background:#eef4fc;color:#005BAC;font-size:12px;font-weight:600;padding:5px 12px;border-radius:999px;}
.stack{display:grid;grid-template-columns:repeat(auto-fit,minmax(215px,1fr));gap:18px;margin:26px 0;}
.stack-card{background:white;border-radius:14px;box-shadow:0 8px 24px rgba(0,0,0,0.09);padding:22px;border-top:4px solid #005BAC;}
.stack-card .mono{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:13px;font-weight:700;color:#005BAC;display:block;margin-bottom:8px;}
.stack-role{font-size:14px;font-weight:700;color:#111;margin:0 0 8px 0;}
.stack-desc{font-size:13px;color:#555;line-height:1.7;margin:0;}
.agenda{background:white;border-radius:14px;box-shadow:0 8px 26px rgba(0,0,0,0.09);overflow:hidden;margin:24px 0;border-top:5px solid #005BAC;}
.agenda-head{background:#002F6C;color:white;padding:14px 22px;font-size:14px;font-weight:700;letter-spacing:0.3px;}
.agenda-row{display:grid;grid-template-columns:120px 1fr;gap:16px;padding:15px 22px;border-bottom:1px solid #eef2f7;align-items:baseline;}
.agenda-row:last-child{border-bottom:none;}
.agenda-time{font-size:13px;font-weight:700;color:#005BAC;}
.agenda-what{font-size:14px;color:#333;line-height:1.65;}
.agenda-note{display:block;font-size:12.5px;color:#777;margin-top:4px;}
.trap-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:16px;margin:26px 0;}
.trap{background:#f7f9fc;border:1px solid #e4eaf2;border-radius:12px;padding:20px;}
.trap-when{display:inline-block;background:#005BAC;color:white;font-size:10.5px;font-weight:700;letter-spacing:0.6px;text-transform:uppercase;padding:3px 9px;border-radius:5px;margin-bottom:10px;}
.trap-name{font-size:14.5px;font-weight:700;color:#111;margin:0 0 7px 0;}
.trap-desc{font-size:13px;color:#555;line-height:1.7;margin:0;}
.case-grid{display:grid;grid-template-columns:1fr 1fr;gap:22px;margin:26px 0;}
.case{background:white;border-radius:16px;box-shadow:0 10px 28px rgba(0,0,0,0.10);overflow:hidden;border-top:5px solid #005BAC;}
.case.oil{border-top-color:#1b5e20;}
.case-body{padding:24px;}
.case-kicker{font-size:11px;font-weight:700;letter-spacing:0.9px;text-transform:uppercase;color:#005BAC;margin:0 0 6px 0;}
.case.oil .case-kicker{color:#1b5e20;}
.case-name{font-size:19px;font-weight:800;color:#111;margin:0 0 12px 0;}
.case-body p{font-size:13.5px;color:#444;line-height:1.75;margin:0 0 10px 0;}
.case-body p:last-child{margin-bottom:0;}
.callout{background:linear-gradient(135deg,#f4f9ff,#eaf2fc);border-left:5px solid #005BAC;border-radius:12px;padding:22px 26px;margin:26px 0;}
.callout h4{margin:0 0 10px 0;font-size:16px;font-weight:800;color:#002F6C;}
.callout p{margin:0 0 10px 0;font-size:14px;line-height:1.75;color:#333;}
.callout p:last-child{margin-bottom:0;}
.links{background:#f7f9fc;border:1px solid #e4eaf2;border-radius:12px;padding:22px 26px;margin:26px 0;}
.links h4{margin:0 0 12px 0;font-size:14px;font-weight:800;color:#111;text-transform:uppercase;letter-spacing:0.7px;}
.links ul{margin:0;padding-left:18px;}
.links li{font-size:13.5px;line-height:1.9;color:#444;}
.links a{color:#005BAC;font-weight:600;}
.closing{background:linear-gradient(135deg,#002F6C,#005BAC);color:white;border-radius:16px;padding:34px 32px;margin:34px 0 8px 0;text-align:center;}
.closing p{margin:0 auto;font-size:15px;line-height:1.8;opacity:0.95;max-width:720px;}
@media(max-width:700px){
  .post-hero{padding:36px 22px;}.post-hero h2{font-size:22px;}
  .case-grid{grid-template-columns:1fr;}
  .agenda-row{grid-template-columns:1fr;gap:3px;}
}
@media(prefers-reduced-motion:reduce){
  .post-hero,.data-flow{animation:none;}
  .photo-featured img{transition:none;}
}
</style>


<div class="post-hero">
<h2>Open Porous Media Short Course with Prof. Carl Fredrik Berg 🇳🇴</h2>
<p>
Three days of hands-on training on the Open Porous Media (OPM) open-source reservoir
simulator — from the basics of building a simulation deck, through the physics that
governs CO₂ in the subsurface, to running and visualizing real field-scale models of
Sleipner and Norne.
</p>
<div class="post-chips">
  <span class="post-chip">📅 June 16–18, 2026</span>
  <span class="post-chip">📍 Seoul</span>
  <span class="post-chip">🇳🇴 NTNU × Inha University</span>
  <span class="post-chip">💻 Hands-on CCS Simulation</span>
</div>
</div>

<div class="photo-featured">
  <img src="https://raw.githubusercontent.com/PetroInha/petroinha.github.io/main/_images/20260616-18_CCS_%EB%B6%84%EC%95%BC_%ED%95%B4%EC%99%B8%EC%A0%84%EB%AC%B8%EA%B0%80_%EC%B4%88%EC%B2%AD_%EB%8B%A8%EA%B8%B0%EA%B5%90%EC%9C%A1.jpg" alt="Participants of the Open Porous Media short course with Prof. Carl Fredrik Berg, June 2026">
  <div class="photo-caption">Prof. Carl Fredrik Berg with course participants — the opening lecture on the Sleipner and Norne field cases, June 16, 2026</div>
</div>

<div class="data-flow"></div>

CURE Lab hosted a three-day intensive short course led by **Prof. Carl Fredrik Berg** of
NTNU (Norwegian University of Science and Technology), held as part of a program bringing
invited overseas experts in CCS to Korea for focused technical training.

The subject was **Open Porous Media (OPM)** — the open-source reservoir simulation stack
that has quietly become one of the standard tools for CO₂ storage modeling. For a lab
whose research runs on subsurface flow simulation, having the software explained by
someone who works on it in the country that has been injecting CO₂ offshore since 1996 is
about as direct a transfer of expertise as it gets.

<div class="sec-head">
  <div class="sec-num">01</div>
  <h3>The instructor</h3>
</div>

<div class="expert">
<p class="expert-name">Prof. Carl Fredrik Berg</p>
<p class="expert-aff">Department of Geosciences, NTNU · Trondheim, Norway</p>
<p>
Prof. Berg works at the point where pore-scale physics meets field-scale engineering. His
research covers digital rock modeling of flow in porous media, the upscaling of transport
properties from pore images to simulation grids, wettability characterization, and the
optimization of reservoir simulation models — including well placement and uncertainty
quantification. He is affiliated with <strong>PoreLab</strong>, the Norwegian Centre of
Excellence dedicated to the physics of porous media.
</p>
<p>
That combination is unusual and it is exactly why the course worked. Upscaling is the
recurring problem of CO₂ storage simulation: the physics that controls how much CO₂ stays
put happens at the scale of millimetres and metres, while the models that regulators and
operators actually run have grid cells hundreds of metres wide. Someone who has worked at
both ends can explain not just which keyword to type, but what the simulator is
approximating away when you do.
</p>
<p>
At NTNU he teaches courses including <em>Geomechanics and Flow in Porous Media</em> and
<em>Numerical Methods in Reservoir Simulation</em>, and he maintains an openly available
reservoir simulation textbook — a teaching background that showed in how the three days
were paced.
</p>
<div class="expert-tags">
  <span class="expert-tag">Digital Rock Physics</span>
  <span class="expert-tag">Upscaling</span>
  <span class="expert-tag">Reservoir Simulation</span>
  <span class="expert-tag">Wettability</span>
  <span class="expert-tag">CO₂ Storage</span>
  <span class="expert-tag">PoreLab</span>
</div>
</div>

<div class="sec-head">
  <div class="sec-num">02</div>
  <h3>What is Open Porous Media?</h3>
</div>

OPM is a community initiative for open, reproducible simulation of porous media
processes, developed largely out of Norway with contributions from SINTEF, NORCE, Equinor
and the university groups around them. Its flagship, **OPM Flow**, is a fully-implicit
three-phase black-oil reservoir simulator released under a free license.

The practical significance is easy to miss if you have only ever used commercial
software. OPM Flow reads the same industry-standard input decks as the commercial
simulators, has been validated against them on real field cases, and is used
operationally on producing assets — so it is not a teaching toy. But because it is open
source, you can read the discretization, instrument the solver, and publish a paper that
someone else can reproduce exactly. For a research lab, that last property is worth a
great deal.

<div class="stack">
  <div class="stack-card">
    <span class="mono">opm-common</span>
    <p class="stack-role">Input &amp; deck handling</p>
    <p class="stack-desc">Parses the simulation deck — grid, rock and fluid properties, wells, schedule — in the standard industry format, so existing models transfer without rewriting.</p>
  </div>
  <div class="stack-card">
    <span class="mono">OPM Flow</span>
    <p class="stack-role">The simulator</p>
    <p class="stack-desc">Fully-implicit black-oil solver with extensions for CO₂ storage, thermal, polymer and solvent. Parallelized for multi-million-cell field models.</p>
  </div>
  <div class="stack-card">
    <span class="mono">ResInsight</span>
    <p class="stack-role">3D visualization &amp; post-processing</p>
    <p class="stack-desc">Open-source viewer for grids, properties, faults and wells, with flow diagnostics and a Python interface for scripted analysis.</p>
  </div>
</div>

<div class="data-flow"></div>

<div class="sec-head">
  <div class="sec-num">03</div>
  <h3>The three days</h3>
</div>

<div class="agenda">
  <div class="agenda-head">June 16–18, 2026 · Short course program</div>
  <div class="agenda-row">
    <div class="agenda-time">Day 1</div>
    <div class="agenda-what">Getting started with OPM
      <span class="agenda-note">Installing and running OPM Flow, the anatomy of a simulation deck, grid and property input, wells and schedule, reading the output. Introduction to the Sleipner and Norne field cases.</span>
    </div>
  </div>
  <div class="agenda-row">
    <div class="agenda-time">Day 2</div>
    <div class="agenda-what">The physics of CO₂ in the subsurface
      <span class="agenda-note">CO₂–brine phase behaviour, the trapping mechanisms and their timescales, relative permeability and hysteresis, and how each of these is represented — or approximated — inside the simulator.</span>
    </div>
  </div>
  <div class="agenda-row">
    <div class="agenda-time">Day 3</div>
    <div class="agenda-what">Field-scale models and visualization
      <span class="agenda-note">Running full field models, interpreting the simulation outcome, and building 3D visualizations and diagnostic plots that communicate what the model is actually saying.</span>
    </div>
  </div>
</div>

<div class="sec-head">
  <div class="sec-num">04</div>
  <h3>The physics: what actually holds CO₂ down</h3>
</div>

A CO₂ storage forecast is only as trustworthy as its treatment of trapping. Injected CO₂
is buoyant — it wants to rise — and the security of a storage site comes from a sequence
of mechanisms that immobilize it progressively over very different timescales.

<div class="trap-grid">
  <div class="trap">
    <span class="trap-when">Immediate</span>
    <p class="trap-name">Structural trapping</p>
    <p class="trap-desc">A low-permeability caprock physically blocks the buoyant plume. Dominant from day one, but it is the mechanism most sensitive to seal integrity and fault behaviour.</p>
  </div>
  <div class="trap">
    <span class="trap-when">Years – decades</span>
    <p class="trap-name">Residual (capillary) trapping</p>
    <p class="trap-desc">As brine imbibes back behind the migrating plume, CO₂ is snapped off into disconnected, immobile blobs. Capturing this requires relative permeability hysteresis — get the hysteresis model wrong and the forecast is wrong.</p>
  </div>
  <div class="trap">
    <span class="trap-when">Decades – centuries</span>
    <p class="trap-name">Solubility trapping</p>
    <p class="trap-desc">CO₂ dissolves into the formation brine. Crucially, CO₂-saturated brine is <em>denser</em> than the brine below it, so the interface is gravitationally unstable and sinks in convective fingers — which greatly accelerates dissolution.</p>
  </div>
  <div class="trap">
    <span class="trap-when">Centuries +</span>
    <p class="trap-name">Mineral trapping</p>
    <p class="trap-desc">Dissolved CO₂ reacts with formation minerals to precipitate solid carbonate — the most permanent outcome, and the slowest. Full geochemistry generally sits outside the flow simulator itself.</p>
  </div>
</div>

OPM Flow handles CO₂ storage through a dedicated **CO₂STORE** mode, in which the
CO₂–brine phase behaviour is not read from user-supplied tables but computed internally
from pressure, temperature and salinity as the simulation runs. That matters for storage
work, where conditions vary widely across a regional model and hand-tabulated PVT quietly
stops being valid.

<div class="callout">
<h4>⚠️ The upscaling problem, made concrete</h4>
<p>
The convective fingers that drive solubility trapping are on the order of metres wide. A
field-scale grid cell is on the order of a hundred metres. So a full-field simulation
cannot resolve the very mechanism that determines long-term storage capacity — refine the
grid enough to capture it and the model becomes unrunnable.
</p>
<p>
This is why sub-grid models for convective mixing are an active research topic, and why
CO₂ storage benchmarks such as the SPE Comparative Solution Projects exist at all: to find
out whether independent groups modeling the same site actually agree. It is also precisely
the territory Prof. Berg's upscaling research sits in, and it made for the most useful
discussion of the course.
</p>
</div>

<div class="data-flow"></div>

<div class="sec-head">
  <div class="sec-num">05</div>
  <h3>Two real fields: Sleipner and Norne</h3>
</div>

Rather than synthetic examples, the course worked with two open benchmark datasets from
the Norwegian continental shelf — both real fields, both with published models, both with
decades of measured data to argue with.

<div class="case-grid">
  <div class="case">
    <div class="case-body">
      <p class="case-kicker">CO₂ Storage · North Sea</p>
      <p class="case-name">Sleipner</p>
      <p>
        The world's first commercial-scale CO₂ storage operation. Since 1996, roughly a
        million tonnes of CO₂ per year have been separated from produced gas and injected
        into the Utsira Formation, a high-permeability saline aquifer offshore Norway.
      </p>
      <p>
        What makes Sleipner uniquely valuable is the monitoring record: a series of
        time-lapse seismic surveys has imaged the plume spreading beneath the caprock year
        after year. The public benchmark model, released in 2020, was built from that 4D
        seismic mapping — so a simulation can be checked against what the subsurface
        actually did, not just against another simulation.
      </p>
    </div>
  </div>
  <div class="case oil">
    <div class="case-body">
      <p class="case-kicker">Full Field Benchmark · Norwegian Sea</p>
      <p class="case-name">Norne</p>
      <p>
        An Equinor-operated subsea oil field, producing since 1997 under water injection.
        Its operator and partners released an unusually complete dataset for research and
        education: the full simulation model, production history, PVT measurements,
        geological description, well logs, and four seismic surveys.
      </p>
      <p>
        Norne is the standard stress test for a reservoir simulator. The grid is faulted
        corner-point geometry with heterogeneous, anisotropic permeability, dissolved gas,
        transmissibility multipliers and pressure-dependent porosity — all the awkward
        features that a clean textbook case leaves out.
      </p>
    </div>
  </div>
</div>

<div class="sec-head">
  <div class="sec-num">06</div>
  <h3>Making the results legible</h3>
</div>

The final part of the course dealt with something easy to treat as an afterthought and
expensive to get wrong: turning a simulation into something a person can interpret. A
field-scale run produces gigabytes of cell-by-cell state across hundreds of time steps,
and the engineering question — *where did the CO₂ go, and is it staying there?* — is not
answerable by reading numbers.

Using **ResInsight**, the open-source 3D post-processor developed alongside OPM,
participants worked through visualizing plume migration in the grid, sectioning models
against faults and wells, and building the diagnostic plots that make a saturation field
into an argument. Its Python interface also means these views can be scripted and
regenerated — which matters when a study involves not one model but an ensemble of
realizations.

<div class="links">
<h4>Resources</h4>
<ul>
  <li><a href="https://opm-project.org/" target="_blank" rel="noopener">The Open Porous Media Initiative</a> — documentation, tutorials and open datasets</li>
  <li><a href="https://resinsight.org/" target="_blank" rel="noopener">ResInsight</a> — 3D viewer and post-processor for reservoir models</li>
  <li><a href="https://co2datashare.org/dataset/sleipner-2019-benchmark-model" target="_blank" rel="noopener">Sleipner 2019 Benchmark Model</a> — open reference dataset on CO2DataShare</li>
  <li><a href="https://www.ntnu.edu/employees/carl.f.berg" target="_blank" rel="noopener">Prof. Carl Fredrik Berg</a> — NTNU profile and publications</li>
  <li><a href="https://porelab.no/" target="_blank" rel="noopener">PoreLab</a> — Norwegian Centre of Excellence for the physics of porous media</li>
</ul>
</div>

<div class="closing">
<p>
Our thanks to Prof. Carl Fredrik Berg for three generous days, and for teaching the
simulator and its limitations with equal care. CURE members leave with an open,
reproducible CCS simulation workflow they can build research on — and a standing
connection to NTNU. 🇳🇴 🤝 🇰🇷
</p>
</div>
