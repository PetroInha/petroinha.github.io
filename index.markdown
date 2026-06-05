---
layout: home
---



<style>


/* ===== Top split layout ===== */

.hero-split{
display:grid;
grid-template-columns: 1.4fr 1fr;
gap:30px;
align-items:center;
margin-bottom:25px;
}

/* responsive */

@media (max-width:900px){
.hero-split{
grid-template-columns:1fr;
}
}

/* ===== iscue card ===== */

.iscue-card{
background:linear-gradient(135deg,#003E82,#005BAC,#0A6ED1);
background-size:200% 200%;
animation:gradShiftCard 12s ease infinite;
color:white;
border-radius:18px;
padding:24px;
box-shadow:0 16px 40px rgba(0,0,0,0.18);
transition:transform 0.25s ease, box-shadow 0.25s ease;
position:relative;
overflow:hidden;
}

.iscue-card::after{
content:"";
position:absolute;
bottom:-40px; right:-40px;
width:160px; height:160px;
background:rgba(255,255,255,0.05);
border-radius:50%;
pointer-events:none;
}

@keyframes gradShiftCard{
0%{background-position:0% 50%;}
50%{background-position:100% 50%;}
100%{background-position:0% 50%;}
}

.iscue-card:hover{
transform:translateY(-4px);
box-shadow:0 22px 48px rgba(0,0,0,0.22);
}

.iscue-card h3{
margin-top:8px;
margin-bottom:6px;
font-weight:700;
}

.iscue-success-badge{
display:inline-flex;
align-items:center;
gap:7px;
background:rgba(74,222,128,0.20);
border:1px solid rgba(74,222,128,0.45);
padding:5px 13px;
border-radius:999px;
font-size:12px;
font-weight:700;
letter-spacing:0.4px;
color:#d4f7e0;
}

.iscue-success-dot{
width:7px; height:7px;
background:#4ade80;
border-radius:50%;
box-shadow:0 0 6px #4ade80;
animation:blinkDot 2s ease infinite;
flex-shrink:0;
}

@keyframes blinkDot{
0%,100%{opacity:1;}
50%{opacity:0.25;}
}

.iscue-chip{
display:inline-block;
background:rgba(255,255,255,0.16);
border:1px solid rgba(255,255,255,0.22);
padding:5px 11px;
border-radius:999px;
font-size:12px;
margin-right:5px;
margin-top:6px;
}

.iscue-btn{
display:inline-block;
margin-top:14px;
padding:10px 16px;
border-radius:10px;
background:white;
color:#005BAC !important;
font-weight:700;
text-decoration:none;
font-size:14px;
transition:background .2s ease, transform .2s ease;
position:relative;
z-index:1;
}

.iscue-btn:hover{
background:#eef4ff;
transform:translateY(-2px);
}

/* ===== recent highlights ===== */

.highlights-grid{
display:grid;
grid-template-columns:1fr 1fr;
gap:16px;
margin-top:14px;
}

.hl-card{
border-radius:12px;
padding:16px;
background:rgba(0,91,172,0.05);
border:1px solid rgba(0,91,172,0.12);
transition:transform .2s ease, box-shadow .2s ease;
text-decoration:none !important;
color:inherit !important;
display:block;
}

.hl-card:hover{
transform:translateY(-3px);
box-shadow:0 10px 24px rgba(0,0,0,0.10);
background:rgba(0,91,172,0.09);
}

.hl-tag{
font-size:11px;
font-weight:700;
text-transform:uppercase;
letter-spacing:0.6px;
color:#005BAC;
margin-bottom:6px;
}

.hl-title{
font-size:14px;
font-weight:700;
line-height:1.4;
color:#111;
margin:0;
}

.hl-sub{
font-size:12px;
color:#666;
margin-top:4px;
}

@media(max-width:600px){
.highlights-grid{grid-template-columns:1fr;}
}

/* Scroll reveal (fade-up on scroll) */
.reveal{
  opacity:0;
  transform:translateY(18px);
  transition:opacity 700ms ease, transform 700ms ease;
  will-change:opacity, transform;
}
.reveal.is-visible{ opacity:1; transform:translateY(0); }
.reveal.delay-1{ transition-delay:80ms; }
.reveal.delay-2{ transition-delay:160ms; }
.reveal.delay-3{ transition-delay:240ms; }
.reveal.delay-4{ transition-delay:320ms; }

/* Section card */
.section-card{
  background: rgba(0,0,0,0.02);
  border: 1px solid rgba(0,0,0,0.06);
  border-radius: 18px;
  padding: 22px;
  position: relative;
}

/* Subtle float (“breathing”) animation */
@keyframes floaty {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-6px); }
}
.section-card.float { animation: floaty 6.5s ease-in-out infinite; }
.section-card.float:hover{ animation-play-state: paused; }

/* Research topic explorer */
.topic-explorer{
  display:grid;
  grid-template-columns:180px 1fr;
  gap:20px;
  margin-top:22px;
  align-items:start;
}

.topic-nav{
  display:flex;
  flex-direction:column;
  gap:10px;
}

.topic-nav-btn{
  padding:12px 16px;
  border-radius:12px;
  border:1.5px solid rgba(0,91,172,0.22);
  color:#005BAC;
  background:rgba(0,91,172,0.05);
  font-weight:700;
  font-size:14px;
  cursor:pointer;
  text-align:left;
  transition:all .2s ease;
  width:100%;
}

.topic-nav-btn:hover{
  background:rgba(0,91,172,0.12);
  border-color:#005BAC;
  transform:translateX(3px);
}

.topic-nav-btn.active{
  background:#005BAC;
  color:white;
  border-color:#005BAC;
  box-shadow:0 8px 20px rgba(0,91,172,0.28);
  transform:translateX(3px);
}

.topic-display{
  border-radius:16px;
  overflow:hidden;
  box-shadow:0 12px 36px rgba(0,0,0,0.14);
  background:white;
}

.topic-display img{
  width:100%;
  aspect-ratio:16/9;
  object-fit:cover;
  display:block;
  transition:opacity .3s ease;
}

.topic-display-desc{
  padding:18px 22px;
  background:#f7f9fc;
  border-top:1px solid #e4eaf2;
}

.topic-display-desc strong{
  display:block;
  font-size:15px;
  color:#005BAC;
  margin-bottom:6px;
}

.topic-display-desc p{
  font-size:14px;
  color:#444;
  line-height:1.65;
  margin:0;
}

@media(max-width:700px){
  .topic-explorer{grid-template-columns:1fr;}
  .topic-nav{flex-direction:row;flex-wrap:wrap;}
  .topic-nav-btn{width:auto;font-size:13px;padding:9px 13px;}
  .topic-nav-btn:hover,.topic-nav-btn.active{transform:none;}
}

/* Soft divider */
.hr-soft{
  border:none;
  height:1px;
  background:linear-gradient(90deg, rgba(0,91,172,0), rgba(0,91,172,0.55), rgba(0,91,172,0));
  margin: 26px 0;
}

/* CTA buttons */
.cta-row{
  display:flex;
  flex-wrap:wrap;
  gap:12px;
  margin-top:14px;
  align-items:center;
}
.cta-btn{
  display:inline-flex;
  align-items:center;
  justify-content:center;
  gap:10px;
  padding:12px 16px;
  border-radius:14px;
  border:1px solid rgba(0,91,172,0.25);
  background:#005BAC;
  color:#fff !important;
  font-weight:800;
  text-decoration:none !important;
  box-shadow:0 10px 20px rgba(0,91,172,0.25);
  transition:transform 200ms ease, box-shadow 200ms ease, filter 200ms ease;
}
.cta-btn:hover{
  transform:translateY(-2px);
  box-shadow:
    0 18px 36px rgba(0,91,172,0.35),
    0 0 0 6px rgba(0,91,172,0.12);
  filter:saturate(1.05);
}
.cta-btn.secondary{
  background:#fff;
  color:#005BAC !important;
  border:1.5px solid #005BAC;
  box-shadow:0 10px 20px rgba(0,0,0,0.08);
}
.cta-btn.secondary:hover{
  box-shadow:
    0 18px 36px rgba(0,0,0,0.12),
    0 0 0 6px rgba(0,91,172,0.10);
}
.cta-note{ font-size:13px; color:#555; }

/* Inline icons */
.cta-ico{
  width:18px; height:18px;
  display:inline-block;
  background:currentColor;
  -webkit-mask: var(--mask) no-repeat center / contain;
  mask: var(--mask) no-repeat center / contain;
}
.ico-mail{ --mask: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path fill="black" d="M20 4H4a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V6a2 2 0 0 0-2-2Zm0 4-8 5-8-5V6l8 5 8-5v2Z"/></svg>'); }
.ico-users{ --mask: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path fill="black" d="M16 11a4 4 0 1 0-4-4 4 4 0 0 0 4 4Zm-8 0a4 4 0 1 0-4-4 4 4 0 0 0 4 4Zm0 2c-3.33 0-6 1.34-6 3v2h12v-2c0-1.66-2.67-3-6-3Zm8 0c-.42 0-.82.03-1.2.08A4.9 4.9 0 0 1 18 16v2h6v-2c0-1.66-2.67-3-6-3Z"/></svg>'); }

/* Reduced motion */
@media (prefers-reduced-motion: reduce){
  .reveal{ opacity:1; transform:none; transition:none; }
  .section-card.float{ animation:none; }
  .cure-chip{ transition:none; }
  .cta-btn{ transition:none; }
}

/* ===== HERO SLIDER ===== */

.hero-slider{
position:relative;
width:100%;
height:260px;
overflow:hidden;
border-radius:14px;
box-shadow:0 10px 26px rgba(0,0,0,0.18);
margin-top:18px;
}

.hero-slide{
position:absolute;
width:100%;
height:100%;
opacity:0;
transition:opacity 1s ease;
}

.hero-slide img{
width:100%;
height:100%;
object-fit:cover;
}

.hero-slide.active{
opacity:1;
}

/* dots */

.slider-dots{
position:absolute;
bottom:10px;
left:50%;
transform:translateX(-50%);
display:flex;
gap:6px;
}

.slider-dot{
width:8px;
height:8px;
border-radius:50%;
background:rgba(255,255,255,0.6);
}

.slider-dot.active{
background:white;
}


</style>

<div class="hero-split reveal">

<!-- LEFT : current CURE intro -->
<div>

<h1><span style="color:#005BAC;"><strong>CURE@Inha</strong></span></h1>

<h3><span style="color:#005BAC;">Subsurface Intelligence for the Energy Transition</span></h3>

<p>
We fuse <strong>physics</strong>, <strong>data</strong>, and <strong>AI</strong> to build next-generation geoenergy systems—
from <strong>CO₂ storage</strong> to <strong>underground hydrogen storage</strong>.
</p>

<div class="hero-slider">

<div class="hero-slide active">
<img src="https://raw.githubusercontent.com/PetroInha/petroinha.github.io/main/_images/hd_shin.JPG">
</div>

<div class="hero-slide">
<img src="https://raw.githubusercontent.com/PetroInha/petroinha.github.io/main/_images/Pyrcz_3.jpg">
</div>

<div class="hero-slide">
<img src="https://raw.githubusercontent.com/PetroInha/petroinha.github.io/main/_images/2024_grad.jpg">
</div>

<div class="hero-slide">
<img src="https://raw.githubusercontent.com/PetroInha/petroinha.github.io/main/_images/2024summer.png">
</div>

<div class="hero-slide">
<img src="https://raw.githubusercontent.com/PetroInha/petroinha.github.io/main/_images/seminar_field_1.jpg">
</div>

<div class="slider-dots">
<span class="slider-dot active"></span>
<span class="slider-dot"></span>
<span class="slider-dot"></span>
<span class="slider-dot"></span>
<span class="slider-dot"></span>
</div>

</div>

</div>


<!-- RIGHT : iscue info -->

<div class="iscue-card">

<div class="iscue-success-badge">
  <div class="iscue-success-dot"></div>
  Successfully Completed
</div>

<h3>🌍 IsCUE 2026</h3>

<p style="margin:0 0 8px 0;">
<strong>The 4th International Symposium on CCS & Unconventional Energy</strong>
</p>

<p style="font-size:13px; line-height:1.55; opacity:0.93; margin:0;">
Three inspiring days in Daqing, China — researchers from 12+ countries advancing CCS, hydrogen, geothermal, and unconventional resources. Next stop: <strong>Vietnam 2027</strong>.
</p>

<div>
<span class="iscue-chip">✅ May 27–29, 2026 · Daqing, China</span>
<span class="iscue-chip">🇻🇳 IsCUE 2027 · Quy Nhon, Vietnam</span>
</div>

<a class="iscue-btn" href="/is-cue/">
See Event Recap →
</a>

</div>
</div>

<hr class="hr-soft" />

<div class="section-card float reveal">

<h2>🔬 <span style="color:#005BAC;"><strong>What We Do</strong></span></h2>

<p>
At <strong>CURE</strong>, we fuse <strong>physics</strong>, <strong>data</strong>, and <strong>AI</strong>
to engineer intelligence into the subsurface — from pore-scale imaging to field-scale carbon storage.
Click a topic to explore.
</p>

<div class="topic-explorer">

  <div class="topic-nav">
    <button class="topic-nav-btn active" data-topic="CCS">#CCS</button>
    <button class="topic-nav-btn" data-topic="UHS">#UHS</button>
    <button class="topic-nav-btn" data-topic="DRP">#DigitalRock</button>
    <button class="topic-nav-btn" data-topic="GenAI">#GenAI</button>
    <button class="topic-nav-btn" data-topic="UQ">#UQ</button>
  </div>

  <div class="topic-display" id="topic-display">
    <img id="topic-img" src="https://raw.githubusercontent.com/PetroInha/petroinha.github.io/main/_images/CCS_reduced.jpg" alt="CCS">
    <div class="topic-display-desc">
      <strong id="topic-title">Carbon Capture &amp; Storage (CCS)</strong>
      <p id="topic-desc">Monitoring CO₂ plume migration, assessing wellbore integrity, and quantifying leakage risk in geological storage formations. We develop ML-assisted diagnostics and high-fidelity simulation frameworks for safe, long-term storage.</p>
    </div>
  </div>

</div>

<p style="margin-top:20px;"><span style="color:#005BAC;"><strong>We don’t just model the subsurface — we engineer intelligence into it.</strong></span></p>

</div>

<script>
(function(){
  var topics = {
    CCS:   { img: ‘https://raw.githubusercontent.com/PetroInha/petroinha.github.io/main/_images/CCS_reduced.jpg’,   title: ‘Carbon Capture & Storage (CCS)’,       desc: ‘Monitoring CO₂ plume migration, assessing wellbore integrity, and quantifying leakage risk in geological storage formations. We develop ML-assisted diagnostics and high-fidelity simulation frameworks for safe, long-term storage.’ },
    UHS:   { img: ‘https://raw.githubusercontent.com/PetroInha/petroinha.github.io/main/_images/UHS_reduced.jpg’,   title: ‘Underground Hydrogen Storage (UHS)’,    desc: ‘Investigating cyclic injection and withdrawal dynamics, geochemical reactions, and microbial effects in porous reservoirs. We model hydrogen behavior to maximize storage safety and energy recovery efficiency.’ },
    DRP:   { img: ‘https://raw.githubusercontent.com/PetroInha/petroinha.github.io/main/_images/DRP_reduced.jpg’,   title: ‘Digital Rock Physics’,                  desc: ‘Reconstructing 3D pore microstructures from micro-CT imaging, simulating multiphase flow with lattice Boltzmann methods, and upscaling pore-scale properties to the reservoir scale for accurate formation evaluation.’ },
    GenAI: { img: ‘https://raw.githubusercontent.com/PetroInha/petroinha.github.io/main/_images/GenAI_reduced.jpg’, title: ‘Generative AI for Geoscience’,           desc: ‘Applying diffusion models, GANs, and SinFusion-based techniques to generate realistic geological realizations, augment scarce subsurface data, and enable physics-informed deep learning for seismic interpretation.’ },
    UQ:    { img: ‘https://raw.githubusercontent.com/PetroInha/petroinha.github.io/main/_images/UQ_reduced.jpg’,    title: ‘Uncertainty Quantification (UQ)’,        desc: ‘Deploying ensemble methods, surrogate models, and Bayesian frameworks to propagate geological uncertainty through reservoir simulations — enabling robust, risk-informed decisions for energy storage and production.’ }
  };

  function init() {
    var btns   = document.querySelectorAll(‘.topic-nav-btn’);
    var imgEl  = document.getElementById(‘topic-img’);
    var titleEl= document.getElementById(‘topic-title’);
    var descEl = document.getElementById(‘topic-desc’);

    if (!imgEl) return;

    btns.forEach(function(btn) {
      btn.addEventListener(‘click’, function() {
        var key = this.getAttribute(‘data-topic’);
        var d   = topics[key];
        if (!d) return;

        btns.forEach(function(b){ b.classList.remove(‘active’); });
        this.classList.add(‘active’);

        imgEl.style.opacity = ‘0’;
        imgEl.onload = function() {
          imgEl.style.opacity = ‘1’;
          imgEl.onload = null;
        };
        imgEl.src   = d.img;
        imgEl.alt   = key;
        titleEl.textContent = d.title;
        descEl.textContent  = d.desc;
      });
    });
  }

  if (document.readyState === ‘loading’) {
    document.addEventListener(‘DOMContentLoaded’, init);
  } else {
    init();
  }
})();
</script>

<hr class="hr-soft" />

<div class="section-card reveal">

<h2>📰 <span style="color:#005BAC;"><strong>Recent Highlights</strong></span></h2>

<div class="highlights-grid">

  <a class="hl-card" href="/is-cue/">
    <div class="hl-tag">✅ Symposium · May 2026</div>
    <p class="hl-title">IsCUE 2026 Successfully Completed</p>
    <p class="hl-sub">Daqing, China · 12+ countries · IsCUE 2027 next in Vietnam</p>
  </a>

  <a class="hl-card" href="/jekyll/update/2026/05/03/EGU26.html">
    <div class="hl-tag">🎤 Conference · May 2026</div>
    <p class="hl-title">Two Presentations at EGU 2026</p>
    <p class="hl-sub">Austria Center Vienna · ML-CCS & SinFusion geological modeling</p>
  </a>

</div>

</div>

<hr class="hr-soft" />

<div class="section-card float reveal" id="join">

<h2>🚀 <span style="color:#005BAC;"><strong>Join the CURE Lab</strong></span></h2>
<h3><span style="color:#005BAC;">Seeking Future Leaders</span></h3>

<p>We are looking for <strong>highly motivated MS/PhD students and research interns</strong> who want to work on:</p>

<ul>
  <li><span style="color:#005BAC;"><strong>AI + Geoenergy</strong></span></li>
  <li><span style="color:#005BAC;"><strong>CCS &amp; Hydrogen</strong></span></li>
  <li><span style="color:#005BAC;"><strong>Digital Rock Modeling</strong></span></li>
</ul>

<p>
At CURE, you will build strong computational skills, publish internationally, and grow into a globally competitive researcher.
</p>

<div class="cta-row">
  <a class="cta-btn" href="#apply">
    <span class="cta-ico ico-mail"></span>
    Apply Now
  </a>
  <a class="cta-btn secondary" href="/Members/">
    <span class="cta-ico ico-users"></span>
    Meet the Team
  </a>
  <span class="cta-note">Tip: short pre-contact is welcome for topic matching.</span>
</div>

</div>

<hr class="hr-soft" />

<div class="section-card float reveal" id="apply">

<h2>✉️ <span style="color:#005BAC;"><strong>How to Apply (지원 방법)</strong></span></h2>

<p>
CURE Lab에 관심 있는 학생은 아래 서류를 준비하여 이메일로 보내주세요.<br>
(연구실/주제 적합성 논의를 위해 <strong>사전 컨택을 권장</strong>합니다.)
</p>

<p><strong>제출 서류</strong></p>
<ol>
  <li><strong>자기소개서</strong> (지원 동기, 관심 연구 주제, 본인의 강점/경험)</li>
  <li><strong>CV</strong> (프로그래밍/시뮬레이션/실험 등 기술 스택, 연구·프로젝트 경험 포함)</li>
  <li><strong>성적표</strong></li>
</ol>

<p><strong>제출처</strong></p>
<ul>
  <li><strong>hyundon.shin@inha.ac.kr (PI)</strong></li>
  <li><strong>honggeun.jo@inha.ac.kr (Co-PI)</strong></li>
</ul>

<p><strong>Tip</strong>: 학부 인턴/진학 예정자는 관심 주제와 가능한 시작 시점을 함께 적어주시면 더 빠르게 매칭할 수 있습니다.</p>

</div>

<script>
/* Reveal sections as they enter the viewport */
(function(){
  const els = document.querySelectorAll('.reveal');
  if (!('IntersectionObserver' in window)) {
    els.forEach(el => el.classList.add('is-visible'));
    return;
  }
  const io = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if(entry.isIntersecting){
        entry.target.classList.add('is-visible');
        io.unobserve(entry.target);
      }
    });
  }, { threshold: 0.14 });

  els.forEach((el, idx) => {
    const d = Math.min(idx, 4);
    el.classList.add(`delay-${d}`);
    io.observe(el);
  });
})();
</script>

<hr class="hr-soft" />

<script>

const slides=document.querySelectorAll(".hero-slide");
const dots=document.querySelectorAll(".slider-dot");

let current=0;

function showSlide(i){

slides.forEach(s=>s.classList.remove("active"));
dots.forEach(d=>d.classList.remove("active"));

slides[i].classList.add("active");
dots[i].classList.add("active");

}

setInterval(()=>{

current++;

if(current>=slides.length){
current=0;
}

showSlide(current);

},5000);

</script>