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
background:linear-gradient(135deg,#003E82,#005BAC);
color:white;
border-radius:18px;
padding:24px;
box-shadow:0 16px 40px rgba(0,0,0,0.18);
transition:transform 0.25s ease, box-shadow 0.25s ease;
}

.iscue-card:hover{
transform:translateY(-4px);
box-shadow:0 22px 48px rgba(0,0,0,0.22);
}

.iscue-card h3{
margin-top:0;
font-weight:700;
}

.iscue-chip{
display:inline-block;
background:rgba(255,255,255,0.18);
padding:6px 12px;
border-radius:999px;
font-size:13px;
margin-right:6px;
margin-top:6px;
}

.iscue-btn{
display:inline-block;
margin-top:14px;
padding:10px 14px;
border-radius:10px;
background:white;
color:#005BAC !important;
font-weight:700;
text-decoration:none;
}

.iscue-btn:hover{
background:#f1f6ff;
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

/* Chips */
.cure-chips{ display:flex; flex-wrap:wrap; gap:10px; margin:12px 0 6px 0; }
.cure-chip{
  display:inline-block;
  padding:7px 14px;
  border-radius:999px;
  border:1.5px solid #005BAC;
  color:#005BAC;
  background:rgba(0, 91, 172, 0.08);
  font-weight:700;
  font-size:0.92rem;
  letter-spacing:0.2px;
  transition:transform 180ms ease, background 180ms ease, color 180ms ease, box-shadow 180ms ease;
}
.cure-chip:hover{
  background:#005BAC;
  color:#fff;
  transform:translateY(-2px) scale(1.02);
  box-shadow:0 10px 18px rgba(0,0,0,0.10);
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

</div>


<!-- RIGHT : iscue info -->

<div class="iscue-card">

<h3>🌍 IsCUE 2026</h3>

<p>
<strong>International Symposium on CCS & Unconventional Energy</strong>
</p>

<p style="font-size:14px; line-height:1.5; opacity:0.95">

Carbon storage · Hydrogen · Geothermal ·  
Direct Lithium Extraction · Unconventional Oil & Gas

</p>

<div>

<span class="iscue-chip">📅 May 27–29 2026</span>

<span class="iscue-chip">📍 NEPU, China</span>

</div>

<a class="iscue-btn" href="/is-cue/">
Symposium Details →
</a>

</div>
</div>

<hr class="hr-soft" />

<div class="section-card float reveal">

<h2><span style="color:#005BAC;"><strong>What We Do</strong></span></h2>

<p>At CURE (Center for Unconventional Resources &amp; Energy), we integrate:</p>

<ul>
  <li><span style="color:#005BAC;"><strong>Reservoir Physics</strong></span> &amp; high-fidelity simulation</li>
  <li><span style="color:#005BAC;"><strong>Digital Rock</strong></span> &amp; multiscale characterization</li>
  <li><span style="color:#005BAC;"><strong>Generative AI</strong></span> &amp; uncertainty quantification</li>
  <li><span style="color:#005BAC;"><strong>CCS</strong></span> &amp; <span style="color:#005BAC;"><strong>Underground Hydrogen Storage</strong></span></li>
</ul>

<p><span style="color:#005BAC;"><strong>We don’t just model the subsurface — we engineer intelligence into it.</strong></span></p>

<div class="cure-chips">
  <span class="cure-chip">#CCS</span>
  <span class="cure-chip">#UHS</span>
  <span class="cure-chip">#DigitalRock</span>
  <span class="cure-chip">#GenAI</span>
  <span class="cure-chip">#UQ</span>
</div>

</div>

<hr class="hr-soft" />

<div class="section-card float reveal">

<h2>🔬 <span style="color:#005BAC;"><strong>Research Thrusts</strong></span></h2>

<ul>
  <li>CO₂ Storage Integrity &amp; Risk</li>
  <li>AI-driven Geological Modeling</li>
  <li>Digital Rock Physics (imaging → flow → mechanics)</li>
  <li>Subsurface Uncertainty &amp; Optimization</li>
</ul>

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
