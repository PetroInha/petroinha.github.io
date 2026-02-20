---
layout: home
# Feel free to add content and custom Front Matter to this file.
# To modify the layout, see https://jekyllrb.com/docs/themes/#overriding-theme-defaults
---

<style>
/* ====== Scroll Reveal Core ====== */
.reveal {
  opacity: 0;
  transform: translateY(18px);
  transition: opacity 700ms ease, transform 700ms ease;
  will-change: opacity, transform;
}
.reveal.is-visible {
  opacity: 1;
  transform: translateY(0);
}
.reveal.delay-1 { transition-delay: 80ms; }
.reveal.delay-2 { transition-delay: 160ms; }
.reveal.delay-3 { transition-delay: 240ms; }
.reveal.delay-4 { transition-delay: 320ms; }

/* ====== Section Card Wrapper (subtle) ====== */
.section-card {
  background: rgba(0,0,0,0.02);
  border: 1px solid rgba(0,0,0,0.06);
  border-radius: 18px;
  padding: 22px 22px;
}

/* ====== Chips (outlined + hover) ====== */
.cure-chips { display:flex; flex-wrap:wrap; gap:10px; margin:12px 0 6px 0; }
.cure-chip {
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
.cure-chip:hover {
  background:#005BAC;
  color:#fff;
  transform:translateY(-2px) scale(1.02);
  box-shadow:0 10px 18px rgba(0,0,0,0.10);
}

/* ====== Fancy Divider ====== */
.hr-soft {
  border: none;
  height: 1px;
  background: linear-gradient(90deg, rgba(0,91,172,0), rgba(0,91,172,0.55), rgba(0,91,172,0));
  margin: 26px 0;
}

/* ====== Reduced Motion ====== */
@media (prefers-reduced-motion: reduce){
  .reveal { opacity:1; transform:none; transition:none; }
  .cure-chip { transition:none; }
}
</style>

<div class="reveal">
  
# <span style="color:#005BAC;"><strong>CURE@Inha</strong></span>  
### <span style="color:#005BAC;">Subsurface Intelligence for the Energy Transition</span>

We fuse **physics**, **data**, and **AI** to build next-generation geoenergy systems—  
from **CO₂ storage** to **underground hydrogen storage**.

</div>

<div class="hr-soft"></div>

<div class="section-card reveal">
  
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

<div class="section-card reveal">
  
## 🔬 <span style="color:#005BAC;"><strong>Research Thrusts</strong></span>

- CO₂ Storage Integrity & Risk  
- AI-driven Geological Modeling  
- Digital Rock Physics (imaging → flow → mechanics)  
- Subsurface Uncertainty & Optimization  

</div>

<div class="hr-soft"></div>

<div class="section-card reveal">
  
## 🚀 <span style="color:#005BAC;"><strong>Join the CURE Lab</strong></span>  
### <span style="color:#005BAC;">Seeking Future Leaders</span>

We are looking for **highly motivated MS/PhD students and research interns** who want to work on:

- <span style="color:#005BAC;"><strong>AI + Geoenergy</strong></span>  
- <span style="color:#005BAC;"><strong>CCS & Hydrogen</strong></span>  
- <span style="color:#005BAC;"><strong>Digital Rock Modeling</strong></span>

At CURE, you will build strong computational skills, publish internationally, and grow into a globally competitive researcher.

</div>

<div class="hr-soft"></div>

<div class="section-card reveal">
  
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
/* ====== Scroll Reveal (fade-up) ====== */
(function() {
  const els = document.querySelectorAll('.reveal');
  if (!('IntersectionObserver' in window)) {
    els.forEach(el => el.classList.add('is-visible'));
    return;
  }

  const io = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('is-visible');
        io.unobserve(entry.target);
      }
    });
  }, { threshold: 0.12 });

  // Stagger by DOM order
  els.forEach((el, idx) => {
    const d = Math.min(idx, 4);
    el.classList.add(`delay-${d}`);
    io.observe(el);
  });
})();
</script>