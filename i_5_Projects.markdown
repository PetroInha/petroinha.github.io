---
layout: page
title: Projects
permalink: /Projects/
---

<style>
.proj-hero{background:linear-gradient(135deg,#002F6C,#005BAC);color:white;padding:38px 36px 32px;border-radius:18px;margin-bottom:40px;box-shadow:0 14px 40px rgba(0,0,0,0.16);position:relative;overflow:hidden;}
.proj-hero::before{content:"";position:absolute;top:-50px;right:-50px;width:200px;height:200px;background:rgba(255,255,255,0.05);border-radius:50%;}
.proj-hero h2{margin:0 0 8px;font-size:22px;font-weight:800;position:relative;z-index:1;}
.proj-hero p{margin:0;font-size:14px;opacity:0.88;line-height:1.65;position:relative;z-index:1;max-width:760px;}
.proj-hero-stats{display:flex;flex-wrap:wrap;gap:24px;margin-top:20px;position:relative;z-index:1;}
.proj-hero-stat .num{font-size:28px;font-weight:800;line-height:1;}
.proj-hero-stat .lbl{font-size:11px;opacity:0.7;text-transform:uppercase;letter-spacing:0.5px;}

.section-title{font-size:18px;font-weight:800;color:#005BAC;margin:40px 0 22px;padding-bottom:8px;border-bottom:2px solid #e4edf8;}

.proj-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(370px,1fr));gap:26px;margin-bottom:40px;}

.proj-card{background:white;border-radius:18px;box-shadow:0 8px 28px rgba(0,0,0,0.09);overflow:hidden;display:flex;flex-direction:column;transition:transform .25s ease,box-shadow .25s ease;}
.proj-card:hover{transform:translateY(-4px);box-shadow:0 18px 44px rgba(0,0,0,0.14);}
.proj-card-accent{height:5px;}
.proj-card-body{padding:24px 26px;flex:1;display:flex;flex-direction:column;gap:14px;}

.proj-meta{font-size:12px;color:#888;font-weight:600;display:flex;flex-wrap:wrap;gap:6px;align-items:center;}
.proj-meta-badge{background:#f0f4fa;color:#555;padding:3px 10px;border-radius:999px;font-size:11px;}
.proj-meta-badge.status-active{background:#e6f4ea;color:#2e7d32;}
.proj-meta-badge.status-past{background:#f3f3f3;color:#888;}

.proj-title{font-size:16px;font-weight:800;color:#111;line-height:1.4;margin:0;}
.proj-desc{font-size:13.5px;color:#444;line-height:1.7;margin:0;}

.proj-topics-label{font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:0.8px;color:#005BAC;margin-bottom:6px;}
.proj-topics{display:flex;flex-wrap:wrap;gap:7px;}
.proj-topic{background:#e8f0fb;color:#005BAC;font-size:11.5px;font-weight:600;padding:4px 11px;border-radius:999px;}

.proj-methods{margin:0;padding:0 0 0 16px;font-size:13px;color:#444;line-height:1.8;}
.proj-methods li{margin-bottom:2px;}

.past-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:20px;margin-bottom:40px;}
.past-card{background:#f8f9fc;border-radius:14px;padding:22px 24px;border-left:4px solid #b0c4de;}
.past-card h4{margin:0 0 6px;font-size:15px;font-weight:700;color:#333;}
.past-card .past-meta{font-size:12px;color:#888;margin-bottom:10px;}
.past-card p{font-size:13px;color:#555;line-height:1.65;margin:0 0 10px;}

.focus-bar{display:flex;flex-wrap:wrap;gap:12px;margin-top:10px;}
.focus-chip{background:#e8f0fb;color:#005BAC;padding:9px 18px;border-radius:999px;font-size:13.5px;font-weight:700;transition:all .2s ease;cursor:default;}
.focus-chip:hover{background:#005BAC;color:white;transform:translateY(-2px);}

.data-flow{height:2px;background:linear-gradient(90deg,transparent,#005BAC,transparent);background-size:200% 100%;animation:dataFlow 4s linear infinite;margin:32px 0;}
@keyframes dataFlow{0%{background-position:200% 0;}100%{background-position:-200% 0;}}

@media(max-width:700px){
  .proj-grid,.past-grid{grid-template-columns:1fr;}
  .proj-hero{padding:26px 20px;}
}
</style>


<div class="proj-hero">
<h2>CURE Lab — Research Portfolio</h2>
<p>We lead interdisciplinary national R&amp;D programs bridging nano-scale rock physics to field-scale deployment — advancing geological carbon storage, AI-driven subsurface modeling, unconventional energy systems, and digital geoscience platforms.</p>
<div class="proj-hero-stats">
  <div class="proj-hero-stat"><div class="num">6</div><div class="lbl">Active Projects</div></div>
  <div class="proj-hero-stat"><div class="num">4</div><div class="lbl">Funding Agencies</div></div>
  <div class="proj-hero-stat"><div class="num">2028–30</div><div class="lbl">Horizon</div></div>
</div>
</div>


<div class="section-title">Ongoing Projects</div>

<div class="proj-grid">

<!-- ===== 1. Low-Carbon Oil Sands ===== -->
<div class="proj-card">
  <div class="proj-card-accent" style="background:linear-gradient(90deg,#bf360c,#e64a19);"></div>
  <div class="proj-card-body">
    <div class="proj-meta">
      <span class="proj-meta-badge status-active">Active</span>
      <span class="proj-meta-badge">2022 – 2028</span>
      <span class="proj-meta-badge">Ministry of Land, Infrastructure &amp; Transport</span>
    </div>
    <p class="proj-title">Low-Carbon High-Yield Unconventional Oil Recovery</p>
    <p class="proj-desc">
      Develops next-generation thermal recovery technologies for oil sands with substantially reduced carbon footprint.
      Focuses on hybrid steam-solvent injection processes, intelligent operation control, and geomechanically coupled
      reservoir simulation to maximize oil production while minimizing steam-to-oil ratio and greenhouse gas emissions.
    </p>
    <div>
      <div class="proj-topics-label">Key Topics</div>
      <div class="proj-topics">
        <span class="proj-topic">ES-SAGD</span>
        <span class="proj-topic">Steam &amp; Gas Push (SAGP)</span>
        <span class="proj-topic">eMSAGP</span>
        <span class="proj-topic">Shale Barrier Modeling</span>
        <span class="proj-topic">NCG Injection</span>
        <span class="proj-topic">Geomechanical Coupling</span>
        <span class="proj-topic">Well Pair Optimization</span>
        <span class="proj-topic">ML Performance Prediction</span>
        <span class="proj-topic">SAGD Preheating</span>
        <span class="proj-topic">Emission Reduction</span>
        <span class="proj-topic">Economic Evaluation</span>
      </div>
    </div>
    <div>
      <div class="proj-topics-label">Research Approaches</div>
      <ul class="proj-methods">
        <li>Hybrid ES-SAGD and solvent-steam co-injection process simulation</li>
        <li>Thermo-geomechanical coupled reservoir simulation (SAGD + geomechanics)</li>
        <li>Machine learning models for SAGD performance prediction from well log data</li>
        <li>Non-condensable gas (NCG) injection timing and rate optimization</li>
        <li>Well pair spacing, toe-up preheating, and operating strategy optimization</li>
        <li>Economic viability analysis of eco-friendly oil sands development</li>
      </ul>
    </div>
  </div>
</div>

<!-- ===== 2. Cross-Border CCS Network ===== -->
<div class="proj-card">
  <div class="proj-card-accent" style="background:linear-gradient(90deg,#005BAC,#1a6dcc);"></div>
  <div class="proj-card-body">
    <div class="proj-meta">
      <span class="proj-meta-badge status-active">Active</span>
      <span class="proj-meta-badge">2025 – 2029</span>
      <span class="proj-meta-badge">Ministry of Trade, Industry &amp; Energy</span>
    </div>
    <p class="proj-title">Cross-Border CCS Network Optimization</p>
    <p class="proj-desc">
      Designs an integrated CO₂ capture–transport–storage network linking Korea's major industrial emission sources
      to offshore and overseas geological storage sites. Develops multi-objective optimization frameworks for
      hub-and-spoke CO₂ logistics, incorporating economic, safety, and regulatory constraints for a
      commercially viable CCS supply chain.
    </p>
    <div>
      <div class="proj-topics-label">Key Topics</div>
      <div class="proj-topics">
        <span class="proj-topic">CO₂ Transport Network</span>
        <span class="proj-topic">Hub-and-Spoke Design</span>
        <span class="proj-topic">Ship-based CO₂ Transport</span>
        <span class="proj-topic">Pipeline Optimization</span>
        <span class="proj-topic">Multi-objective Optimization</span>
        <span class="proj-topic">CCS Supply Chain</span>
        <span class="proj-topic">Blue Hydrogen Linkage</span>
        <span class="proj-topic">Cross-border Storage</span>
        <span class="proj-topic">Risk Assessment</span>
        <span class="proj-topic">Policy Scenario Analysis</span>
      </div>
    </div>
    <div>
      <div class="proj-topics-label">Research Approaches</div>
      <ul class="proj-methods">
        <li>CO₂ source mapping and industrial cluster analysis for hub site selection</li>
        <li>Economic comparison of ship-based vs. pipeline CO₂ transport scenarios</li>
        <li>Integration with blue hydrogen supply chains (Korea–Canada, Korea–Australia)</li>
        <li>Network topology optimization using mixed-integer programming</li>
        <li>Risk, safety, and environmental impact assessment of CO₂ infrastructure</li>
        <li>Policy and regulatory scenario modeling for cross-border CCS frameworks</li>
      </ul>
    </div>
  </div>
</div>

<!-- ===== 3. Nano-Scale Offshore CCS ===== -->
<div class="proj-card">
  <div class="proj-card-accent" style="background:linear-gradient(90deg,#00695c,#00897b);"></div>
  <div class="proj-card-body">
    <div class="proj-meta">
      <span class="proj-meta-badge status-active">Active</span>
      <span class="proj-meta-badge">2025 – 2029</span>
      <span class="proj-meta-badge">Ministry of Trade, Industry &amp; Energy</span>
    </div>
    <p class="proj-title">Nano-Scale Offshore CCS Integrity</p>
    <p class="proj-desc">
      Investigates CO₂ containment security and caprock seal integrity for offshore geological storage in Korea's
      East Sea, spanning nano-scale pore structure through field-scale deformation response.
      Combines generative AI for digital rock augmentation, coupled thermo-hydro-mechanical (THM) simulation,
      and satellite InSAR geodetic monitoring to deliver a multi-scale integrity assessment framework.
    </p>
    <div>
      <div class="proj-topics-label">Key Topics</div>
      <div class="proj-topics">
        <span class="proj-topic">Caprock Seal Integrity</span>
        <span class="proj-topic">Nano Digital Rock Physics</span>
        <span class="proj-topic">SEM / CT Imaging</span>
        <span class="proj-topic">Generative AI Augmentation</span>
        <span class="proj-topic">THM Coupled Simulation</span>
        <span class="proj-topic">InSAR Surface Deformation</span>
        <span class="proj-topic">Well Leakage Risk</span>
        <span class="proj-topic">CO₂–Brine–Rock Geochemistry</span>
        <span class="proj-topic">Offshore East Sea Storage</span>
        <span class="proj-topic">Multi-scale Upscaling</span>
      </div>
    </div>
    <div>
      <div class="proj-topics-label">Research Approaches</div>
      <ul class="proj-methods">
        <li>SEM/micro-CT pore imaging, segmentation, and pore network extraction of caprock samples</li>
        <li>SinGAN/GAN-based digital rock data augmentation for uncertainty assessment</li>
        <li>THM coupled geomechanical simulation of CO₂ injection and caprock response</li>
        <li>InSAR surface deformation inversion to characterize CO₂ storage reservoirs</li>
        <li>ML-assisted assessment of CO₂ leakage risk through legacy wells and fractures</li>
        <li>Geochemical modeling of CO₂–brine–mineral interactions and trapping mechanisms</li>
      </ul>
    </div>
  </div>
</div>

<!-- ===== 4. Digital Rock + AI Platform ===== -->
<div class="proj-card">
  <div class="proj-card-accent" style="background:linear-gradient(90deg,#4a148c,#7b1fa2);"></div>
  <div class="proj-card-body">
    <div class="proj-meta">
      <span class="proj-meta-badge status-active">Active</span>
      <span class="proj-meta-badge">2025 – 2030</span>
      <span class="proj-meta-badge">Ministry of Education</span>
    </div>
    <p class="proj-title">Digital Rock Physics + AI Platform</p>
    <p class="proj-desc">
      Builds an integrated digital rock physics (DRP) platform that couples pore-scale multi-physics simulation
      with AI-driven property estimation and uncertainty quantification. Targets automated characterization of
      reservoir and caprock petrophysical properties — permeability, relative permeability, capillary pressure,
      and elastic moduli — from 3D CT/SEM images, with full uncertainty propagation from pore to field scale.
    </p>
    <div>
      <div class="proj-topics-label">Key Topics</div>
      <div class="proj-topics">
        <span class="proj-topic">Pore-Network Modeling</span>
        <span class="proj-topic">Lattice Boltzmann Method</span>
        <span class="proj-topic">3D CT Image Processing</span>
        <span class="proj-topic">Relative Permeability</span>
        <span class="proj-topic">Capillary Pressure</span>
        <span class="proj-topic">Deep Learning Upscaling</span>
        <span class="proj-topic">Uncertainty Quantification</span>
        <span class="proj-topic">GAN Rock Synthesis</span>
        <span class="proj-topic">Multi-physics Coupling</span>
        <span class="proj-topic">Digital Core Analysis</span>
      </div>
    </div>
    <div>
      <div class="proj-topics-label">Research Approaches</div>
      <ul class="proj-methods">
        <li>3D CT/SEM image segmentation and pore network extraction for rock microstructure analysis</li>
        <li>Lattice Boltzmann method (LBM) for pore-scale single- and multi-phase flow simulation</li>
        <li>Deep learning (CNN, PoreFlow-Net) for rapid permeability and porosity prediction</li>
        <li>GAN-based synthetic rock sample generation for data augmentation</li>
        <li>Multi-scale upscaling from pore-scale physics to core- and reservoir-scale properties</li>
        <li>Uncertainty propagation framework for petrophysical property estimation</li>
      </ul>
    </div>
  </div>
</div>

<!-- ===== 5. GenAI for Geological Media ===== -->
<div class="proj-card">
  <div class="proj-card-accent" style="background:linear-gradient(90deg,#1b5e20,#2e7d32);"></div>
  <div class="proj-card-body">
    <div class="proj-meta">
      <span class="proj-meta-badge status-active">Active</span>
      <span class="proj-meta-badge">2025 – 2026</span>
      <span class="proj-meta-badge">Ministry of Science &amp; ICT</span>
    </div>
    <p class="proj-title">Generative AI for Geological Media Modeling</p>
    <p class="proj-desc">
      Develops generative AI workflows for realistic geological model synthesis, augmentation, and data conditioning.
      Focuses on single-image and process-based generative approaches that reproduce complex geological
      heterogeneity — fluvial channels, turbidite lobes, deltaic systems — while honoring sparse well log
      and seismic observations for robust subsurface uncertainty assessment.
    </p>
    <div>
      <div class="proj-topics-label">Key Topics</div>
      <div class="proj-topics">
        <span class="proj-topic">SinGAN</span>
        <span class="proj-topic">Process-based Modeling</span>
        <span class="proj-topic">Training Image Generation</span>
        <span class="proj-topic">Well Data Conditioning</span>
        <span class="proj-topic">Multi-point Statistics</span>
        <span class="proj-topic">Geological Uncertainty</span>
        <span class="proj-topic">Ensemble Modeling</span>
        <span class="proj-topic">GAN Acceptance Criteria</span>
        <span class="proj-topic">Fluvial / Turbidite Facies</span>
      </div>
    </div>
    <div>
      <div class="proj-topics-label">Research Approaches</div>
      <ul class="proj-methods">
        <li>SinGAN-based geological model augmentation from a single training image</li>
        <li>Conditioning generative models to sparse well log and dynamic production data</li>
        <li>Minimum acceptance criteria for quality evaluation of generative geological models</li>
        <li>Integration of SinGAN with ES-MDA for history matching of CO₂ storage reservoirs</li>
        <li>Probabilistic geological scenario generation for subsurface uncertainty quantification</li>
      </ul>
    </div>
  </div>
</div>

<!-- ===== 6. GenAI Reservoir Modeling (KOGAS) ===== -->
<div class="proj-card">
  <div class="proj-card-accent" style="background:linear-gradient(90deg,#006064,#00838f);"></div>
  <div class="proj-card-body">
    <div class="proj-meta">
      <span class="proj-meta-badge status-active">Active</span>
      <span class="proj-meta-badge">2025 – 2028</span>
      <span class="proj-meta-badge">Korea Gas Corporation (KOGAS)</span>
    </div>
    <p class="proj-title">Generative AI Reservoir Modeling for Gas Storage &amp; CCS</p>
    <p class="proj-desc">
      Develops foundation model-based frameworks for 3D reservoir model generation and dynamic data assimilation,
      targeting underground natural gas storage and CO₂ geological storage applications.
      Integrates multi-source subsurface data (well logs, 3D seismic, production history, InSAR) into
      geologically consistent ensemble reservoir models for robust production forecasting and uncertainty quantification.
    </p>
    <div>
      <div class="proj-topics-label">Key Topics</div>
      <div class="proj-topics">
        <span class="proj-topic">Foundation Model</span>
        <span class="proj-topic">3D Geostatistical Simulation</span>
        <span class="proj-topic">ES-MDA</span>
        <span class="proj-topic">History Matching</span>
        <span class="proj-topic">Seismic Data Conditioning</span>
        <span class="proj-topic">Dynamic Data Assimilation</span>
        <span class="proj-topic">Production Forecasting</span>
        <span class="proj-topic">CO₂ Plume Prediction</span>
        <span class="proj-topic">Uncertainty Quantification</span>
        <span class="proj-topic">Underground Gas Storage</span>
      </div>
    </div>
    <div>
      <div class="proj-topics-label">Research Approaches</div>
      <ul class="proj-methods">
        <li>Foundation AI model for multi-conditional 3D subsurface model generation</li>
        <li>Ensemble Smoother with Multiple Data Assimilation (ES-MDA) for history matching</li>
        <li>SinGAN/GAN-based geological prior model generation and conditioning</li>
        <li>Integration of well, 3D seismic, BHP, and InSAR deformation data</li>
        <li>CO₂ plume migration prediction and storage performance uncertainty quantification</li>
        <li>Transfer learning for adapting pre-trained models to new reservoir settings</li>
      </ul>
    </div>
  </div>
</div>

</div><!-- end proj-grid -->


<div class="data-flow"></div>


<div class="section-title" style="color:#888;">Completed Projects</div>

<div class="past-grid">

<div class="past-card">
  <h4>CO₂ Storage Efficiency Enhancement</h4>
  <div class="past-meta">2023 – 2025 &nbsp;|&nbsp; Ministry of Trade, Industry &amp; Energy</div>
  <p>Developed methods to enhance CO₂ injectivity and storage efficiency in saline aquifers and tight formations.
     Investigated EGR (Enhanced Gas Recovery) coupled with CCS in the Duvernay Shale, Canada, and
     optimized multi-well injection scheduling for the Pohang Basin, South Korea.</p>
  <div class="proj-topics" style="margin-top:8px;">
    <span class="proj-topic">CO₂ Injectivity</span>
    <span class="proj-topic">EGR-CCS</span>
    <span class="proj-topic">Injection Scheduling</span>
    <span class="proj-topic">Proxy Model Optimization</span>
    <span class="proj-topic">Storage Efficiency Factor</span>
  </div>
</div>

<div class="past-card">
  <h4>Commercial Carbon Storage Exploration</h4>
  <div class="past-meta">2023 – 2025 &nbsp;|&nbsp; Ministry of Trade, Industry &amp; Energy</div>
  <p>Conducted 3D seismic acquisition, interpretation, and geostatistical modeling to evaluate West Sea (Yellow Sea)
     offshore storage sites for commercial-scale CO₂ geological storage. Developed probabilistic volumetric
     storage capacity estimates and site ranking frameworks.</p>
  <div class="proj-topics" style="margin-top:8px;">
    <span class="proj-topic">3D Seismic Interpretation</span>
    <span class="proj-topic">Geostatistical Ensemble Modeling</span>
    <span class="proj-topic">Storage Capacity Estimation</span>
    <span class="proj-topic">West Sea Site Characterization</span>
    <span class="proj-topic">Structural Trap Evaluation</span>
  </div>
</div>

</div>


<div class="data-flow"></div>


<div class="section-title">Strategic Focus Areas</div>

<div class="focus-bar">
  <div class="focus-chip">AI-Powered Subsurface Modeling</div>
  <div class="focus-chip">Nano → Field Scale Integration</div>
  <div class="focus-chip">Geological Carbon Storage</div>
  <div class="focus-chip">Unconventional Energy Systems</div>
  <div class="focus-chip">Digital Rock Physics</div>
  <div class="focus-chip">Generative AI for Geoscience</div>
  <div class="focus-chip">CCS Commercialization</div>
  <div class="focus-chip">Uncertainty Quantification</div>
</div>
