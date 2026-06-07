---
layout: page
title: Lectures
permalink: /Lectures/
---

<style>
/* ── Global ── */
.data-flow{height:2px;background:linear-gradient(90deg,transparent,#005BAC,transparent);background-size:200% 100%;animation:dataFlow 4s linear infinite;margin:36px 0;}
@keyframes dataFlow{0%{background-position:200% 0;}100%{background-position:-200% 0;}}

/* ── Hero ── */
.lec-hero{background:linear-gradient(135deg,#002F6C,#005BAC);color:white;padding:40px 38px 34px;border-radius:18px;margin-bottom:40px;box-shadow:0 14px 40px rgba(0,0,0,0.16);position:relative;overflow:hidden;}
.lec-hero::before{content:"";position:absolute;top:-60px;right:-60px;width:220px;height:220px;background:rgba(255,255,255,0.05);border-radius:50%;}
.lec-hero h2{margin:0 0 8px;font-size:22px;font-weight:800;position:relative;z-index:1;}
.lec-hero p{margin:0;font-size:14px;opacity:0.88;line-height:1.7;max-width:740px;position:relative;z-index:1;}
.lec-hero-chips{display:flex;flex-wrap:wrap;gap:10px;margin-top:18px;position:relative;z-index:1;}
.lec-hero-chip{background:rgba(255,255,255,0.15);border:1px solid rgba(255,255,255,0.25);padding:5px 14px;border-radius:999px;font-size:12px;font-weight:600;}

/* ── Section title ── */
.lec-section-title{font-size:17px;font-weight:800;color:#005BAC;margin:42px 0 20px;padding-bottom:8px;border-bottom:2px solid #e4edf8;}

/* ── Faculty course columns ── */
.faculty-grid{display:grid;grid-template-columns:1fr 1fr;gap:28px;margin-bottom:8px;}
.faculty-col{}
.faculty-header{display:flex;align-items:center;gap:12px;margin-bottom:16px;padding:14px 18px;background:white;border-radius:14px;box-shadow:0 6px 18px rgba(0,0,0,0.08);border-left:5px solid #005BAC;}
.faculty-avatar{width:46px;height:46px;border-radius:50%;object-fit:cover;object-position:top;flex-shrink:0;}
.faculty-hname{font-size:15px;font-weight:800;color:#005BAC;margin:0 0 1px;}
.faculty-hrole{font-size:11.5px;color:#888;}

.fac-card{background:white;border-radius:12px;padding:14px 16px;box-shadow:0 4px 14px rgba(0,0,0,0.07);margin-bottom:12px;border-left:3px solid #c5d8f0;transition:border-color .2s,box-shadow .2s;}
.fac-card:hover{border-left-color:#005BAC;box-shadow:0 8px 24px rgba(0,0,0,0.11);}
.fac-code{font-size:11px;font-weight:700;color:#aaa;letter-spacing:0.5px;margin-bottom:3px;}
.fac-name-ko{font-size:14px;font-weight:800;color:#111;margin:0 0 1px;}
.fac-name-en{font-size:12px;color:#666;margin:0 0 6px;}
.fac-desc{font-size:12.5px;color:#555;line-height:1.6;margin:0 0 8px;}
.fac-chips{display:flex;flex-wrap:wrap;gap:5px;}
.fac-chip{background:#e8f0fb;color:#005BAC;font-size:10.5px;font-weight:600;padding:2px 9px;border-radius:999px;}

/* ── Curriculum grid ── */
.curr-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:22px;margin-bottom:8px;}
.curr-col{background:white;border-radius:16px;box-shadow:0 6px 18px rgba(0,0,0,0.08);overflow:hidden;}
.curr-col-header{padding:12px 18px;font-size:13px;font-weight:800;color:white;}
.curr-col-body{padding:14px 16px;}
.curr-row{padding:9px 0;border-bottom:1px solid #f0f4fa;font-size:13px;}
.curr-row:last-child{border-bottom:none;}
.curr-code{font-size:10.5px;font-weight:700;color:#aaa;display:block;margin-bottom:1px;}
.curr-ko{font-weight:700;color:#111;display:block;line-height:1.3;}
.curr-en{color:#777;font-size:12px;display:block;margin-bottom:3px;}
.curr-desc-sm{font-size:11.5px;color:#888;line-height:1.5;}
.cure-tag{display:inline-block;background:#e8f0fb;color:#005BAC;font-size:9.5px;font-weight:700;padding:1px 7px;border-radius:999px;margin-left:5px;vertical-align:middle;}

/* ── Grad cards ── */
.grad-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:18px;margin-bottom:8px;}
.grad-card{background:white;border-radius:14px;padding:18px 20px;box-shadow:0 6px 18px rgba(0,0,0,0.08);border-top:4px solid #005BAC;transition:transform .2s,box-shadow .2s;}
.grad-card:hover{transform:translateY(-3px);box-shadow:0 14px 32px rgba(0,0,0,0.12);}
.grad-card.jo{border-top-color:#1565c0;}
.grad-card.shin{border-top-color:#00695c;}
.grad-card.both{border-top:4px solid transparent;border-image:linear-gradient(90deg,#00695c,#1565c0) 1;}
.grad-ko{font-size:14.5px;font-weight:800;color:#111;margin:0 0 2px;}
.grad-en{font-size:12px;color:#777;margin:0 0 8px;}
.grad-desc{font-size:13px;color:#555;line-height:1.65;margin:0 0 10px;}
.grad-chips{display:flex;flex-wrap:wrap;gap:5px;}
.grad-chip{background:#f0f4fa;color:#005BAC;font-size:11px;font-weight:600;padding:3px 9px;border-radius:999px;}
.grad-by{font-size:11px;color:#aaa;margin-top:8px;}

/* ── Pathway ── */
.pathway{background:linear-gradient(135deg,rgba(0,91,172,0.05),rgba(0,91,172,0.02));border:1px dashed rgba(0,91,172,0.30);border-radius:16px;padding:20px 24px;}
.pathway h4{margin:0 0 14px;color:#005BAC;font-size:15px;}
.pathway-rows{display:flex;flex-direction:column;gap:8px;}
.pathway-row{display:flex;align-items:baseline;gap:8px;font-size:13px;flex-wrap:wrap;}
.pw-from{font-weight:700;color:#005BAC;white-space:nowrap;}
.pw-arr{color:#aaa;}
.pw-to{color:#444;}

@media(max-width:900px){
  .faculty-grid{grid-template-columns:1fr;}
  .curr-grid{grid-template-columns:1fr;}
}
@media(max-width:700px){
  .lec-hero{padding:26px 20px;}
}
</style>


<!-- ════════════════ HERO ════════════════ -->
<div class="lec-hero">
<h2>CURE Lab — Courses &amp; Curriculum</h2>
<p>The Department of Energy Resources Engineering at Inha University offers a rigorous curriculum bridging subsurface geoscience, carbon capture &amp; storage, AI-powered data analysis, and sustainable energy systems — from foundational sciences to capstone research projects.</p>
<div class="lec-hero-chips">
  <span class="lec-hero-chip">🎓 Undergraduate + Graduate</span>
  <span class="lec-hero-chip">🔬 CCS · AI · Digital Rock · Hydrogen</span>
  <span class="lec-hero-chip">📍 Dept. of Energy Resources Engineering, Inha Univ.</span>
</div>
</div>


<!-- ════════════════ CURE FACULTY COURSES ════════════════ -->
<div class="lec-section-title">Courses by CURE Faculty</div>

<div class="faculty-grid">

<!-- Prof. Shin -->
<div class="faculty-col">
  <div class="faculty-header">
    <img class="faculty-avatar" src="https://raw.githubusercontent.com/PetroInha/petroinha.github.io/main/_images/hd_shin.JPG" alt="Prof. Shin">
    <div>
      <div class="faculty-hname">Prof. Hyundon Shin</div>
      <div class="faculty-hrole">Reservoir Engineering · CCS · Oil Sands · Hydrogen</div>
    </div>
  </div>

  <div class="fac-card">
    <div class="fac-code">ENR3315</div>
    <div class="fac-name-ko">지오에너지공학개론</div>
    <div class="fac-name-en">Introduction to Geo-Energy Engineering</div>
    <div class="fac-desc">Petroleum engineering fundamentals — reservoir types, fluid properties, drive mechanisms, and basic well performance. Entry point to subsurface energy systems.</div>
    <div class="fac-chips"><span class="fac-chip">Reservoir</span><span class="fac-chip">Petroleum Engineering</span><span class="fac-chip">Fluid Flow</span></div>
  </div>

  <div class="fac-card">
    <div class="fac-code">ENR3313</div>
    <div class="fac-name-ko">시추 및 지층평가공학</div>
    <div class="fac-name-en">Drilling and Subsurface Evaluation Engineering</div>
    <div class="fac-desc">Drilling mechanics, well design, formation evaluation using wireline logs, and Python-based data processing for subsurface characterization.</div>
    <div class="fac-chips"><span class="fac-chip">Drilling</span><span class="fac-chip">Well Logs</span><span class="fac-chip">Python</span></div>
  </div>

  <div class="fac-card">
    <div class="fac-code">ENR3207</div>
    <div class="fac-name-ko">이산화탄소 포집 및 저장 기술</div>
    <div class="fac-name-en">CO₂ Capture and Storage Technology</div>
    <div class="fac-desc">Principles and technologies for geological carbon sequestration — site selection, injection design, trapping mechanisms, and risk assessment for CCS projects.</div>
    <div class="fac-chips"><span class="fac-chip">CCS</span><span class="fac-chip">CO₂ Injection</span><span class="fac-chip">Storage Security</span></div>
  </div>

  <div class="fac-card">
    <div class="fac-code">ENR4319</div>
    <div class="fac-name-ko">지오에너지 생산 및 설비</div>
    <div class="fac-name-en">Geo-Energy Production and Facility</div>
    <div class="fac-desc">Petroleum production engineering, well completion methods, artificial lift, surface facility design, and production optimization strategies.</div>
    <div class="fac-chips"><span class="fac-chip">Production Engineering</span><span class="fac-chip">Well Completion</span><span class="fac-chip">Facilities</span></div>
  </div>
</div>

<!-- Prof. Jo -->
<div class="faculty-col">
  <div class="faculty-header">
    <img class="faculty-avatar" src="https://raw.githubusercontent.com/PetroInha/petroinha.github.io/main/_images/hj_photo.jfif" alt="Prof. Jo">
    <div>
      <div class="faculty-hname">Prof. Honggeun Jo</div>
      <div class="faculty-hrole">Subsurface AI · Geostatistics · Digital Rock · CCS Modeling</div>
    </div>
  </div>

  <div class="fac-card">
    <div class="fac-code">ENR3103</div>
    <div class="fac-name-ko">지구통계학</div>
    <div class="fac-name-en">Geostatistics</div>
    <div class="fac-desc">Statistical methods for spatial data analysis and resource assessment — variogram modeling, kriging, sequential Gaussian simulation, and geological uncertainty quantification.</div>
    <div class="fac-chips"><span class="fac-chip">Kriging</span><span class="fac-chip">Spatial Statistics</span><span class="fac-chip">Uncertainty</span></div>
  </div>

  <div class="fac-card">
    <div class="fac-code">ENR3314</div>
    <div class="fac-name-ko">CO₂ 지중저장 모니터링</div>
    <div class="fac-name-en">CO₂ Subsurface Storage Monitoring</div>
    <div class="fac-desc">Monitoring and verification technologies for geological carbon storage — 4D seismic, InSAR surface deformation, well-based sensors, and data integration workflows.</div>
    <div class="fac-chips"><span class="fac-chip">4D Seismic</span><span class="fac-chip">InSAR</span><span class="fac-chip">CCS Monitoring</span></div>
  </div>

  <div class="fac-card">
    <div class="fac-code">ENR3312</div>
    <div class="fac-name-ko">에너지 빅데이터</div>
    <div class="fac-name-en">Energy Big Data</div>
    <div class="fac-desc">Data science workflows applied to energy systems — data wrangling, dimensionality reduction, supervised and unsupervised learning for geoscience and energy applications.</div>
    <div class="fac-chips"><span class="fac-chip">Machine Learning</span><span class="fac-chip">Data Science</span><span class="fac-chip">Geoscience</span></div>
  </div>

  <div class="fac-card">
    <div class="fac-code">ENR4320</div>
    <div class="fac-name-ko">에너지자원과 인공지능</div>
    <div class="fac-name-en">Energy Resources and Artificial Intelligence</div>
    <div class="fac-desc">Deep learning and generative AI methods for subsurface modeling — CNNs for seismic interpretation, GAN-based geological model generation, and AI-driven uncertainty quantification.</div>
    <div class="fac-chips"><span class="fac-chip">Deep Learning</span><span class="fac-chip">Generative AI</span><span class="fac-chip">Subsurface Modeling</span></div>
  </div>
</div>

</div><!-- end faculty-grid -->


<div class="data-flow"></div>


<!-- ════════════════ UNDERGRAD CURRICULUM ════════════════ -->
<div class="lec-section-title">Undergraduate Curriculum Overview</div>

<div class="curr-grid">

<!-- Foundation (1–2학년) -->
<div class="curr-col">
  <div class="curr-col-header" style="background:linear-gradient(90deg,#455a64,#607d8b);">1–2학년 &nbsp;·&nbsp; Foundation</div>
  <div class="curr-col-body">

    <div class="curr-row">
      <span class="curr-code">ENR1101</span>
      <span class="curr-ko">에너지자원과 미래</span>
      <span class="curr-en">Energy Resources and Future</span>
      <span class="curr-desc-sm">Geology, exploration, assessment, and economics of global energy resources. Broad introduction to the field.</span>
    </div>

    <div class="curr-row">
      <span class="curr-code">ENR1902</span>
      <span class="curr-ko">컴퓨터프로그래밍</span>
      <span class="curr-en">Computer Programming</span>
      <span class="curr-desc-sm">Python programming and computational problem-solving for engineering applications.</span>
    </div>

    <div class="curr-row">
      <span class="curr-code">ENR2113</span>
      <span class="curr-ko">에너지자원지질</span>
      <span class="curr-en">Energy Resources Geology</span>
      <span class="curr-desc-sm">Geological fundamentals — stratigraphy, structural geology, and rock classification applied to subsurface resource development.</span>
    </div>

    <div class="curr-row">
      <span class="curr-code">ENR2102</span>
      <span class="curr-ko">유체역학</span>
      <span class="curr-en">Fluid Mechanics</span>
      <span class="curr-desc-sm">Fluid behavior in underground and surface contexts; Darcy's law, flow equations, and well deliverability.</span>
    </div>

    <div class="curr-row">
      <span class="curr-code">ENR2105</span>
      <span class="curr-ko">에너지자원수치해석</span>
      <span class="curr-en">Numerical Analysis for Energy Resources</span>
      <span class="curr-desc-sm">Mathematical methods and their computational implementation for solving engineering problems.</span>
    </div>

    <div class="curr-row">
      <span class="curr-code">ENR2107</span>
      <span class="curr-ko">에너지열역학</span>
      <span class="curr-en">Energy Thermodynamics</span>
      <span class="curr-desc-sm">Thermodynamic principles governing heat transfer, phase behavior, and energy conversion in reservoir and surface systems.</span>
    </div>

    <div class="curr-row">
      <span class="curr-code">ENR2108</span>
      <span class="curr-ko">신재생에너지개론</span>
      <span class="curr-en">Introduction to Renewable Energy</span>
      <span class="curr-desc-sm">Overview of solar, wind, hydro, geothermal, and biomass energy — principles, potential, and challenges.</span>
    </div>

    <div class="curr-row">
      <span class="curr-code">ENR2104</span>
      <span class="curr-ko">에너지자원경제</span>
      <span class="curr-en">Energy Resources Economics</span>
      <span class="curr-desc-sm">Economic analysis of resource development projects, market dynamics, and investment decision frameworks.</span>
    </div>

  </div>
</div>

<!-- Core (3학년) -->
<div class="curr-col">
  <div class="curr-col-header" style="background:linear-gradient(90deg,#1565c0,#1976d2);">3학년 &nbsp;·&nbsp; Core Engineering</div>
  <div class="curr-col-body">

    <div class="curr-row">
      <span class="curr-code">ENR3102</span>
      <span class="curr-ko">지구물리탐사</span>
      <span class="curr-en">Geophysical Exploration</span>
      <span class="curr-desc-sm">Seismic, gravity, magnetic, and electrical methods for subsurface characterization and resource exploration.</span>
    </div>

    <div class="curr-row">
      <span class="curr-code">ENR3103</span>
      <span class="curr-ko">지구통계학 <span class="cure-tag">Jo</span></span>
      <span class="curr-en">Geostatistics</span>
      <span class="curr-desc-sm">Variogram analysis, kriging interpolation, stochastic simulation, and spatial uncertainty quantification.</span>
    </div>

    <div class="curr-row">
      <span class="curr-code">ENR3207</span>
      <span class="curr-ko">이산화탄소 포집 및 저장 기술 <span class="cure-tag">Shin</span></span>
      <span class="curr-en">CO₂ Capture and Storage Technology</span>
      <span class="curr-desc-sm">Geological sequestration of CO₂ — capture technologies, storage formation selection, injectivity, and long-term containment.</span>
    </div>

    <div class="curr-row">
      <span class="curr-code">ENR3312</span>
      <span class="curr-ko">에너지 빅데이터 <span class="cure-tag">Jo</span></span>
      <span class="curr-en">Energy Big Data</span>
      <span class="curr-desc-sm">Machine learning and data analytics for energy and geoscience datasets — feature engineering, regression, and classification.</span>
    </div>

    <div class="curr-row">
      <span class="curr-code">ENR3313</span>
      <span class="curr-ko">시추 및 지층평가공학 <span class="cure-tag">Shin</span></span>
      <span class="curr-en">Drilling and Subsurface Evaluation</span>
      <span class="curr-desc-sm">Rotary drilling mechanics, well design, formation evaluation from logs, and Python-based data interpretation.</span>
    </div>

    <div class="curr-row">
      <span class="curr-code">ENR3314</span>
      <span class="curr-ko">CO₂ 지중저장 모니터링 <span class="cure-tag">Jo</span></span>
      <span class="curr-en">CO₂ Subsurface Storage Monitoring</span>
      <span class="curr-desc-sm">Monitoring verification and accounting (MVA) for CCS — seismic, InSAR, geochemical, and wellbore monitoring techniques.</span>
    </div>

    <div class="curr-row">
      <span class="curr-code">ENR3315</span>
      <span class="curr-ko">지오에너지공학개론 <span class="cure-tag">Shin</span></span>
      <span class="curr-en">Introduction to Geo-Energy Engineering</span>
      <span class="curr-desc-sm">Petroleum reservoir fundamentals — fluid properties, drive mechanisms, material balance, and reservoir performance analysis.</span>
    </div>

    <div class="curr-row">
      <span class="curr-code">ENR3202</span>
      <span class="curr-ko">암석역학 및 실험</span>
      <span class="curr-en">Rock Mechanics and Laboratory</span>
      <span class="curr-desc-sm">Mechanical and thermal properties of rocks — laboratory testing, stress analysis, and geomechanical applications.</span>
    </div>

  </div>
</div>

<!-- Advanced (4학년) -->
<div class="curr-col">
  <div class="curr-col-header" style="background:linear-gradient(90deg,#00695c,#00897b);">4학년 &nbsp;·&nbsp; Advanced &amp; Capstone</div>
  <div class="curr-col-body">

    <div class="curr-row">
      <span class="curr-code">ENR4211</span>
      <span class="curr-ko">수소에너지 저장과 안전</span>
      <span class="curr-en">Hydrogen Energy Storage and Safety</span>
      <span class="curr-desc-sm">Underground and surface hydrogen storage systems, compression and liquefaction, safety protocols, and geological H₂ storage concepts.</span>
    </div>

    <div class="curr-row">
      <span class="curr-code">ENR4214</span>
      <span class="curr-ko">수소에너지공학개론</span>
      <span class="curr-en">Introduction to Hydrogen Energy Engineering</span>
      <span class="curr-desc-sm">Hydrogen production pathways (green, blue, grey), fuel cells, and the role of hydrogen in the energy transition.</span>
    </div>

    <div class="curr-row">
      <span class="curr-code">ENR4319</span>
      <span class="curr-ko">지오에너지 생산 및 설비 <span class="cure-tag">Shin</span></span>
      <span class="curr-en">Geo-Energy Production and Facility</span>
      <span class="curr-desc-sm">Production engineering fundamentals — well deliverability, artificial lift, surface processing, and production system optimization.</span>
    </div>

    <div class="curr-row">
      <span class="curr-code">ENR4320</span>
      <span class="curr-ko">에너지자원과 인공지능 <span class="cure-tag">Jo</span></span>
      <span class="curr-en">Energy Resources and Artificial Intelligence</span>
      <span class="curr-desc-sm">Deep learning, CNNs, GANs, and generative models applied to seismic interpretation, geological modeling, and production prediction.</span>
    </div>

    <div class="curr-row">
      <span class="curr-code">ENR4113</span>
      <span class="curr-ko">에너지전환 및 정책</span>
      <span class="curr-en">Energy Transition and Policy</span>
      <span class="curr-desc-sm">Economic and policy frameworks for the global energy transition — carbon markets, net-zero targets, and national energy strategies.</span>
    </div>

    <div class="curr-row">
      <span class="curr-code">ENR4106</span>
      <span class="curr-ko">풍력에너지개론</span>
      <span class="curr-en">Introduction to Wind Energy</span>
      <span class="curr-desc-sm">Wind energy systems — turbine aerodynamics, site assessment, grid integration, and offshore wind project development.</span>
    </div>

    <div class="curr-row">
      <span class="curr-code">ENR4105</span>
      <span class="curr-ko">순환경제</span>
      <span class="curr-en">Circular Economy</span>
      <span class="curr-desc-sm">Circular resource utilization systems, waste-to-resource frameworks, and lifecycle thinking for critical materials.</span>
    </div>

    <div class="curr-row">
      <span class="curr-code">ENR4324</span>
      <span class="curr-ko">에너지자원공학 설계 및 평가</span>
      <span class="curr-en">Energy Resources Engineering Capstone Design</span>
      <span class="curr-desc-sm">Integrative capstone project spanning exploration through resource utilization — team-based design, analysis, and presentation.</span>
    </div>

  </div>
</div>

</div><!-- end curr-grid -->


<div class="data-flow"></div>


<!-- ════════════════ GRADUATE COURSES ════════════════ -->
<div class="lec-section-title">Graduate Research Courses</div>

<div class="grad-grid">

<div class="grad-card jo">
  <div class="grad-ko">추계학적 지구통계 모델링</div>
  <div class="grad-en">Stochastic Geostatistical Modeling</div>
  <div class="grad-desc">Advanced geostatistical simulation methods — multi-point statistics, object-based modeling, and training image-based approaches for 3D subsurface model generation.</div>
  <div class="grad-chips"><span class="grad-chip">MPS</span><span class="grad-chip">SinGAN</span><span class="grad-chip">Model Uncertainty</span></div>
  <div class="grad-by">Prof. Jo</div>
</div>

<div class="grad-card jo">
  <div class="grad-ko">지오에너지 머신러닝</div>
  <div class="grad-en">Geo-Energy Machine Learning</div>
  <div class="grad-desc">Supervised and unsupervised learning, deep neural networks, and physics-informed ML for reservoir characterization, production forecasting, and subsurface data analysis.</div>
  <div class="grad-chips"><span class="grad-chip">Neural Networks</span><span class="grad-chip">History Matching</span><span class="grad-chip">PINN</span></div>
  <div class="grad-by">Prof. Jo</div>
</div>

<div class="grad-card jo">
  <div class="grad-ko">디지털 트윈과 저류층 시뮬레이션</div>
  <div class="grad-en">Digital Twin and Reservoir Simulation</div>
  <div class="grad-desc">Building digital twin frameworks for subsurface systems — coupled fluid flow and geomechanical simulation, data assimilation (ES-MDA), and real-time reservoir management.</div>
  <div class="grad-chips"><span class="grad-chip">ES-MDA</span><span class="grad-chip">Reservoir Sim</span><span class="grad-chip">Digital Twin</span></div>
  <div class="grad-by">Prof. Jo</div>
</div>

<div class="grad-card shin">
  <div class="grad-ko">탄소감축 및 기후변화 대응기술</div>
  <div class="grad-en">Carbon Reduction and Climate Change Response Technology</div>
  <div class="grad-desc">Advanced CCS technologies, CCUS system design, carbon capture process engineering, and integrated energy-climate policy frameworks for net-zero pathways.</div>
  <div class="grad-chips"><span class="grad-chip">CCUS</span><span class="grad-chip">Net-Zero</span><span class="grad-chip">CO₂ Storage</span></div>
  <div class="grad-by">Prof. Shin</div>
</div>

<div class="grad-card shin">
  <div class="grad-ko">가스공학특론</div>
  <div class="grad-en">Advanced Gas Engineering</div>
  <div class="grad-desc">Advanced treatment of natural gas reservoir performance — unconventional gas (shale, tight), gas condensate systems, EGR, and underground gas storage design.</div>
  <div class="grad-chips"><span class="grad-chip">Shale Gas</span><span class="grad-chip">EGR</span><span class="grad-chip">UGS</span></div>
  <div class="grad-by">Prof. Shin</div>
</div>

<div class="grad-card">
  <div class="grad-ko">기후환경과 에너지기술</div>
  <div class="grad-en">Climate Environment and Energy Technology</div>
  <div class="grad-desc">Interactions between energy systems and the climate — emissions accounting, environmental impact assessment, and engineering solutions for sustainable energy development.</div>
  <div class="grad-chips"><span class="grad-chip">Climate Policy</span><span class="grad-chip">Emissions</span><span class="grad-chip">Sustainability</span></div>
</div>

<div class="grad-card">
  <div class="grad-ko">에너지산업과 신재생에너지</div>
  <div class="grad-en">Energy Industry and Renewable Energy</div>
  <div class="grad-desc">Industry structure and investment landscape of global renewable energy — project finance, grid integration, and the evolving role of fossil fuels in a transition economy.</div>
  <div class="grad-chips"><span class="grad-chip">Renewables</span><span class="grad-chip">Energy Markets</span><span class="grad-chip">Project Finance</span></div>
</div>

<div class="grad-card">
  <div class="grad-ko">신재생에너지 산업 및 기술 동향</div>
  <div class="grad-en">Renewable Energy Industry and Technology Trends</div>
  <div class="grad-desc">Emerging technologies and market trends in solar PV, offshore wind, green hydrogen, and battery storage — with case studies on leading global projects.</div>
  <div class="grad-chips"><span class="grad-chip">Solar PV</span><span class="grad-chip">Offshore Wind</span><span class="grad-chip">Green H₂</span></div>
</div>

<div class="grad-card">
  <div class="grad-ko">인류의 그림자, 에너지 바로 알기</div>
  <div class="grad-en">Understanding Energy and Humanity</div>
  <div class="grad-desc">A cross-disciplinary seminar exploring the history, geopolitics, and social dimensions of energy — from fossil fuel civilization to the future of sustainable energy access.</div>
  <div class="grad-chips"><span class="grad-chip">Energy History</span><span class="grad-chip">Geopolitics</span><span class="grad-chip">Society</span></div>
</div>

</div>


<div class="data-flow"></div>


<!-- ════════════════ CURRICULUM PATHWAY ════════════════ -->
<div class="lec-section-title">Recommended Learning Path</div>

<div class="pathway">
<h4>Foundation → Specialization → Research</h4>
<div class="pathway-rows">
  <div class="pathway-row"><span class="pw-from">컴퓨터프로그래밍</span><span class="pw-arr">→</span><span class="pw-to">에너지빅데이터 → 에너지자원과인공지능 → (Grad) 지오에너지 머신러닝</span></div>
  <div class="pathway-row"><span class="pw-from">에너지자원지질</span><span class="pw-arr">→</span><span class="pw-to">지구물리탐사 → 지오에너지공학개론 → 지오에너지생산및설비</span></div>
  <div class="pathway-row"><span class="pw-from">지구통계학</span><span class="pw-arr">→</span><span class="pw-to">에너지빅데이터 → CO₂지중저장모니터링 → (Grad) 추계학적 지구통계 모델링 · 디지털 트윈</span></div>
  <div class="pathway-row"><span class="pw-from">이산화탄소포집및저장기술</span><span class="pw-arr">→</span><span class="pw-to">CO₂지중저장모니터링 → (Grad) 탄소감축 및 기후변화 대응기술</span></div>
  <div class="pathway-row"><span class="pw-from">시추및지층평가공학</span><span class="pw-arr">→</span><span class="pw-to">지오에너지생산및설비 → 수소에너지저장과안전 → (Grad) 가스공학특론</span></div>
</div>
</div>
