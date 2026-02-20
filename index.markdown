---
layout: home
# Feel free to add content and custom Front Matter to this file.
# To modify the layout, see https://jekyllrb.com/docs/themes/#overriding-theme-defaults
---

<style>
/* ====== Scroll Reveal Core ====== */
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

/* ====== Section Card Wrapper ====== */
.section-card{
  background: rgba(0,0,0,0.02);
  border: 1px solid rgba(0,0,0,0.06);
  border-radius: 18px;
  padding: 22px 22px;
  position: relative;
}

/* 1) Subtle Float (Breathing) Animation */
@keyframes floaty {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-6px); }
}
.section-card.float {
  animation: floaty 6.5s ease-in-out infinite;
}
.section-card.float:hover{
  animation-play-state: paused;
}

/* ====== Chips ====== */
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

/* ====== Fancy Divider ====== */
.hr-soft{
  border:none;
  height:1px;
  background:linear-gradient(90deg, rgba(0,91,172,0), rgba(0,91,172,0.55), rgba(0,91,172,0));
  margin: 26px 0;
}

/* 2) CTA Button + Glow */
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

.cta-note{
  font-size:13px;
  color:#555;
}

/* Small inline icon */
.cta-ico{
  width:18px; height:18px;
  display:inline-block;
  background:currentColor;
  -webkit-mask: var(--mask) no-repeat center / contain;
  mask: var(--mask) no-repeat center / contain;
}
.ico-mail{ --mask: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path fill="black" d="M20 4H4a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V6a2 2 0 0 0-2-2Zm0 4-8 5-8-5V6l8 5 8-5v2Z"/></svg>'); }
.ico-users{ --mask: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path fill="black" d="M16 11a4 4 0 1 0-4-4 4 4 0 0 0 4 4Zm-8 0a4 4 0 1 0-4-4 4 4 0 0 0 4 4Zm0 2c-3.33 0-6 1.34-6 3v2h12v-2c0-1.66-2.67-3-6-3Zm8 0c-.42 0-.82.03-1.2.08A4.9 4.9 0 0 1 18 16v2h6v-2c0-1.66-2.67-3-6-3Z"/></svg>'); }

/* Reduced Motion */
@media (prefers-reduced-motion: reduce){
  .reveal{ opacity:1; transform:none; transition:none; }
  .section-card.float{ animation:none; }
  .cure-chip{ transition:none; }
  .cta-btn{ transition:none; }
}
</style>

<div class="reveal">
  
# <span style="color:#005BAC;"><strong>CURE@Inha</strong></span>  
### <span style="color:#005BAC;">Subsurface Intelligence for the Energy Transition</span>

We fuse **physics**, **data**, and **AI** to build next-generation geoenergy systems—  
from **CO₂ storage** to **underground hydrogen storage**.

</div>

<div class="hr-soft"></div>

<div class="section-card float reveal">
  
## <span style="color:#005BAC;"><strong>What We Do</strong></span>

At CURE (Center for Unconventional Resources & Energy), we integrate:

- <span style="color:#005BAC;"><strong>Reservoir Physics</strong></span> & high-fidelity simulation  
- <span style="color:#005BAC;"><strong>Digital Rock</strong></span> & multiscale characterization  
- <span style="color:#005BAC;"><strong>Generative AI</strong></span> & uncertainty quantification  
- <span style="color:#005BAC;"><strong>CCS</strong></span> & <span style="color:#005BAC;"><strong>Underground Hydrogen Storage</strong></span>

<span style="color:#005BAC;"><strong>We don’t just model the subsurface — we engineer intelligence into it.</strong></span>

<div class="cure-chips">
  <span class="cure-chip">#CCS</span>
  <span class="cure-chip">#UHS</span>
  <span class="cure-chip">#DigitalRock</span>
  <span class="cure-chip">#GenAI</span>
  <span class="cure-chip">#UQ</span>
</div>

</div>

<div class="hr-soft"></div>

<div class="section-card float reveal">
  
## 🔬 <span style="color:#005BAC;"><strong>Research Thrusts</strong></span>

- CO₂ Storage Integrity & Risk  
- AI-driven Geological Modeling  
- Digital Rock Physics (imaging → flow → mechanics)  
- Subsurface Uncertainty & Optimization  

</div>

<div class="hr-soft"></div>

<div class="section-card float reveal" id="join">
  
## 🚀 <span style="color:#005BAC;"><strong>Join the CURE Lab</strong></span>  
### <span style="color:#005BAC;">Seeking Future Leaders</span>

We are looking for **highly motivated MS/PhD students and research interns** who want to work on:

- <span style="color:#005BAC;"><strong>AI + Geoenergy</strong></span>  
- <span style="color:#005BAC;"><strong>CCS & Hydrogen</strong></span>  
- <span style="color:#005BAC;"><strong>Digital Rock Modeling</strong></span>

At CURE, you will build strong computational skills, publish internationally, and grow into a globally competitive researcher.

<!-- 2) CTA Buttons -->
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

<div class="hr-soft"></div>

<div class="section-card float reveal" id="apply">
  
## ✉️ <span style="color:#005BAC;"><strong>How to Apply (지원 방법)</strong></span>

CURE Lab에 관심 있는 학생은 아래 서류를 준비하여 이메일로 보내주세요.  
(연구실/주제 적합성 논의를 위해 **사전 컨택을 권장**합니다.)

**제출 서류**
1) **자기소개서** (지원 동기, 관심 연구 주제, 본인의 강점/경험)  
2) **CV** (프로그래밍/시뮬레이션/실험 등 기술 스택, 연구·프로젝트 경험 포함)  
3) **성적표**

**제출처**
- **hyundon.shin@inha.ac.kr (PI)**  
- **honggeun.jo@inha.ac.kr (Co-PI)**  

**Tip**: 학부 인턴/진학 예정자는 관심 주제와 가능한 시작 시점을 함께 적어주시면 더 빠르게 매칭할 수 있습니다.

</div>

<script>
/* ====== Scroll Reveal (fade-up + stagger) ====== */
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

<!--
3) If you want a "landing page" remaster tailored to your current Jekyll theme:
- Share which theme you use (e.g., minima / just-the-docs / cayman / etc.)
- Or paste your _config.yml theme line + main layout name.
Then I can match typography, spacing, and button styles perfectly to your site.
-->