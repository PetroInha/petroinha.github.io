---
layout: page
title: Members
permalink: /Members/
---

<style>
/* ── Global ── */
.data-flow{height:2px;background:linear-gradient(90deg,transparent,#005BAC,transparent);background-size:200% 100%;animation:dataFlow 4s linear infinite;margin:36px 0;}
@keyframes dataFlow{0%{background-position:200% 0;}100%{background-position:-200% 0;}}

/* ── Hero ── */
.mem-hero{background:linear-gradient(135deg,#002F6C,#005BAC);color:white;padding:40px 38px 34px;border-radius:18px;margin-bottom:40px;box-shadow:0 14px 40px rgba(0,0,0,0.16);position:relative;overflow:hidden;}
.mem-hero::before{content:"";position:absolute;top:-60px;right:-60px;width:220px;height:220px;background:rgba(255,255,255,0.05);border-radius:50%;}
.mem-hero h2{margin:0 0 8px;font-size:22px;font-weight:800;position:relative;z-index:1;}
.mem-hero p{margin:0;font-size:14px;opacity:0.88;line-height:1.7;max-width:700px;position:relative;z-index:1;}
.mem-hero-chips{display:flex;flex-wrap:wrap;gap:10px;margin-top:18px;position:relative;z-index:1;}
.mem-hero-chip{background:rgba(255,255,255,0.15);border:1px solid rgba(255,255,255,0.25);padding:5px 14px;border-radius:999px;font-size:12px;font-weight:600;}

/* ── Section headings ── */
.mem-section-title{font-size:17px;font-weight:800;color:#005BAC;margin:40px 0 20px;padding-bottom:8px;border-bottom:2px solid #e4edf8;display:flex;align-items:center;gap:10px;}

/* ── PI Cards ── */
.pi-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(400px,1fr));gap:26px;margin-bottom:8px;}
.pi-card{background:white;border-radius:18px;box-shadow:0 10px 30px rgba(0,0,0,0.09);overflow:hidden;display:flex;transition:transform .25s,box-shadow .25s;}
.pi-card:hover{transform:translateY(-4px);box-shadow:0 20px 44px rgba(0,0,0,0.13);}
.pi-accent{width:6px;background:linear-gradient(180deg,#002F6C,#005BAC);flex-shrink:0;}
.pi-photo{width:140px;height:160px;object-fit:cover;object-position:top;flex-shrink:0;}
.pi-body{padding:22px 22px 20px;flex:1;}
.pi-name{font-size:17px;font-weight:800;color:#005BAC;margin:0 0 3px;}
.pi-role{font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:0.6px;color:#888;margin-bottom:10px;}
.pi-detail{font-size:13px;color:#444;line-height:1.7;margin-bottom:10px;}
.pi-tags{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:10px;}
.pi-tag{background:#e8f0fb;color:#005BAC;font-size:11px;font-weight:600;padding:3px 10px;border-radius:999px;}
.pi-links{display:flex;gap:12px;flex-wrap:wrap;}
.pi-link{font-size:12px;color:#005BAC;font-weight:600;text-decoration:none;border:1px solid #c5d8f0;padding:4px 12px;border-radius:999px;transition:all .2s;}
.pi-link:hover{background:#005BAC;color:white;border-color:#005BAC;}

/* ── Graduate Student Cards ── */
.member-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(190px,1fr));gap:22px;margin-bottom:8px;}
.member-card{background:white;border-radius:16px;box-shadow:0 8px 22px rgba(0,0,0,0.08);overflow:hidden;text-align:center;transition:transform .25s,box-shadow .25s;position:relative;}
.member-card:hover{transform:translateY(-5px);box-shadow:0 18px 40px rgba(0,0,0,0.13);}
.member-photo{width:100%;height:200px;object-fit:cover;object-position:top;display:block;}
.member-badge{position:absolute;top:10px;right:10px;font-size:10px;font-weight:700;padding:3px 9px;border-radius:999px;letter-spacing:0.3px;}
.badge-phd{background:#002F6C;color:white;}
.badge-ms{background:#00695c;color:white;}
.member-body{padding:14px 14px 16px;}
.member-name{font-size:14px;font-weight:800;color:#111;margin:0 0 2px;}
.member-degree{font-size:11.5px;color:#888;margin:0 0 8px;}
.member-topics{display:flex;flex-wrap:wrap;gap:5px;justify-content:center;}
.member-topic{background:#f0f4fa;color:#005BAC;font-size:10.5px;font-weight:600;padding:3px 8px;border-radius:999px;}

/* ── Intern chips ── */
.intern-chips{display:flex;flex-wrap:wrap;gap:10px;margin:6px 0 18px;}
.intern-chip{background:#e8f0fb;color:#005BAC;padding:8px 16px;border-radius:999px;font-size:13px;font-weight:600;}
.recruit-note{font-size:13.5px;color:#555;background:#f7f9fc;border-left:4px solid #005BAC;padding:12px 18px;border-radius:0 10px 10px 0;margin-top:6px;}
.recruit-note a{color:#005BAC;font-weight:700;}

/* ── Alumni cards (recent) ── */
.alumni-cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:18px;margin-bottom:20px;}
.alumni-card{background:white;border-radius:14px;padding:18px 20px;box-shadow:0 6px 18px rgba(0,0,0,0.07);border-top:4px solid #005BAC;transition:transform .2s;}
.alumni-card:hover{transform:translateY(-3px);}
.alumni-card.ms{border-top-color:#00838f;}
.alumni-card.bs{border-top-color:#9e9e9e;}
.alumni-name{font-size:15px;font-weight:800;color:#111;margin:0 0 3px;}
.alumni-meta{font-size:12px;color:#888;margin-bottom:6px;}
.alumni-dest{font-size:13px;font-weight:600;color:#333;margin-bottom:6px;}
.alumni-dest span{display:inline-block;background:#f0f4fa;color:#005BAC;font-size:11px;padding:2px 9px;border-radius:999px;margin-left:6px;font-weight:700;}
.alumni-topics{font-size:12px;color:#666;}
.alumni-link{font-size:12px;color:#005BAC;font-weight:600;text-decoration:none;}
.alumni-link:hover{text-decoration:underline;}

/* ── Alumni compact list (older) ── */
.alumni-list{list-style:none;margin:0;padding:0;}
.alumni-list li{display:flex;flex-wrap:wrap;align-items:baseline;gap:6px 14px;padding:9px 0;border-bottom:1px solid #f0f3f8;font-size:13.5px;}
.alumni-list li:last-child{border-bottom:none;}
.aln{font-weight:700;color:#333;min-width:90px;}
.alyear{color:#aaa;font-size:12px;}
.aldest{color:#555;}
.altopic{color:#888;font-size:12px;}

/* ── Stats ── */
.stat-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:20px;margin:8px 0 50px;}
.stat-card{background:white;border-radius:16px;padding:28px 24px;text-align:center;box-shadow:0 8px 24px rgba(0,0,0,0.08);border-top:4px solid #005BAC;transition:transform .3s,box-shadow .3s;}
.stat-card:hover{transform:translateY(-5px);box-shadow:0 18px 38px rgba(0,0,0,0.13);}
.stat-card.hl{background:linear-gradient(135deg,#003580,#005BAC);color:white;border-top:none;}
.stat-num{font-size:40px;font-weight:800;line-height:1;margin-bottom:6px;}
.stat-lbl{font-size:13px;opacity:0.85;}

@media(max-width:700px){
  .pi-grid{grid-template-columns:1fr;}
  .pi-card{flex-direction:column;}
  .pi-photo{width:100%;height:200px;}
  .member-grid{grid-template-columns:repeat(auto-fill,minmax(150px,1fr));}
  .mem-hero{padding:26px 20px;}
}
</style>


<!-- ════════════════ HERO ════════════════ -->
<div class="mem-hero">
<h2>CURE Lab — Our Team</h2>
<p>We cultivate future leaders in AI-powered subsurface engineering, geological carbon storage, and carbon-neutral geoenergy systems — bridging cutting-edge research with real-world impact.</p>
<div class="mem-hero-chips">
  <span class="mem-hero-chip">📍 Inha University</span>
  <span class="mem-hero-chip">🎓 2 PIs · 10 Graduate Students</span>
  <span class="mem-hero-chip">🌏 Korea · Peru · Indonesia · Colombia</span>
  <span class="mem-hero-chip">🏭 95% Industry Placement</span>
</div>
</div>


<!-- ════════════════ LEADERSHIP ════════════════ -->
<div class="mem-section-title">Leadership</div>

<div class="pi-grid">

<div class="pi-card">
  <div class="pi-accent"></div>
  <img class="pi-photo" src="https://raw.githubusercontent.com/PetroInha/petroinha.github.io/main/_images/hd_shin.JPG" alt="Prof. Hyundon Shin">
  <div class="pi-body">
    <div class="pi-name">Prof. Hyundon Shin</div>
    <div class="pi-role">Professor · Dept. of Energy Resources Engineering</div>
    <div class="pi-detail">
      Ph.D., University of Alberta<br>
      <em>Former:</em> KNOC · Shell · Husky · Suncor · ConocoPhillips
    </div>
    <div class="pi-tags">
      <span class="pi-tag">Oil Sands · SAGD</span>
      <span class="pi-tag">Shale Gas</span>
      <span class="pi-tag">CCS</span>
      <span class="pi-tag">Hydrogen Storage</span>
      <span class="pi-tag">Reservoir Simulation</span>
    </div>
    <div class="pi-links">
      <a class="pi-link" href="https://scholar.google.com/citations?user=kiVyUyQAAAAJ" target="_blank">Google Scholar</a>
    </div>
  </div>
</div>

<div class="pi-card">
  <div class="pi-accent"></div>
  <img class="pi-photo" src="https://raw.githubusercontent.com/PetroInha/petroinha.github.io/main/_images/hj_photo.jfif" alt="Prof. Honggeun Jo">
  <div class="pi-body">
    <div class="pi-name">Prof. Honggeun Jo</div>
    <div class="pi-role">Assistant Professor · Dept. of Energy Resources Engineering</div>
    <div class="pi-detail">
      Ph.D., University of Texas at Austin<br>
      <em>Former:</em> KOGAS · Halliburton · LLNL · BP
    </div>
    <div class="pi-tags">
      <span class="pi-tag">Subsurface AI</span>
      <span class="pi-tag">Digital Rock Physics</span>
      <span class="pi-tag">CCS Modeling</span>
      <span class="pi-tag">Generative AI</span>
      <span class="pi-tag">Uncertainty Quantification</span>
    </div>
    <div class="pi-links">
      <a class="pi-link" href="https://scholar.google.com/citations?user=u0OE5CIAAAAJ" target="_blank">Google Scholar</a>
    </div>
  </div>
</div>

</div>


<div class="data-flow"></div>


<!-- ════════════════ GRADUATE STUDENTS ════════════════ -->
<div class="mem-section-title">Graduate Students</div>

<div class="member-grid">

<div class="member-card">
  <img class="member-photo" src="https://raw.githubusercontent.com/PetroInha/petroinha.github.io/main/_images/_kim.jpg" alt="김남화">
  <span class="member-badge badge-phd">Ph.D.</span>
  <div class="member-body">
    <div class="member-name">김남화</div>
    <div class="member-degree">Ph.D. Candidate (2020~)</div>
    <div class="member-topics">
      <span class="member-topic">ML-SAGD</span>
      <span class="member-topic">CO₂ Optimization</span>
    </div>
  </div>
</div>

<div class="member-card">
  <img class="member-photo" src="https://raw.githubusercontent.com/PetroInha/petroinha.github.io/main/_images/_KHKim.png" alt="김광현">
  <span class="member-badge badge-phd">Ph.D.</span>
  <div class="member-body">
    <div class="member-name">김광현</div>
    <div class="member-degree">Ph.D. Candidate, part-time</div>
    <div class="member-topics">
      <span class="member-topic">Geological Modeling</span>
    </div>
  </div>
</div>

<div class="member-card">
  <img class="member-photo" src="https://raw.githubusercontent.com/PetroInha/petroinha.github.io/main/_images/_bop.jpg" alt="Bop Duana Afrireksa">
  <span class="member-badge badge-phd">Ph.D.</span>
  <div class="member-body">
    <div class="member-name">Bop Duana Afrireksa</div>
    <div class="member-degree">Ph.D. Candidate</div>
    <div class="member-topics">
      <span class="member-topic">CO₂ Injectivity</span>
      <span class="member-topic">Reservoir Modeling</span>
    </div>
  </div>
</div>

<div class="member-card">
  <img class="member-photo" src="https://raw.githubusercontent.com/PetroInha/petroinha.github.io/main/_images/_YJKim.png" alt="이영진">
  <span class="member-badge badge-phd">Ph.D.</span>
  <div class="member-body">
    <div class="member-name">이영진</div>
    <div class="member-degree">Ph.D. (2026~) · M.S. 2026</div>
    <div class="member-topics">
      <span class="member-topic">ES-SAGD</span>
      <span class="member-topic">Optimization</span>
    </div>
  </div>
</div>

<div class="member-card">
  <img class="member-photo" src="https://raw.githubusercontent.com/PetroInha/petroinha.github.io/main/_images/_DHKim.png" alt="김동희">
  <span class="member-badge badge-ms">M.S.</span>
  <div class="member-body">
    <div class="member-name">김동희</div>
    <div class="member-degree">M.S. (2025~)</div>
    <div class="member-topics">
      <span class="member-topic">Digital Rock</span>
      <span class="member-topic">H₂ Storage</span>
    </div>
  </div>
</div>

<div class="member-card">
  <img class="member-photo" src="https://raw.githubusercontent.com/PetroInha/petroinha.github.io/main/_images/_Aitiana.jpg" alt="Aitiana Sanchez">
  <span class="member-badge badge-ms">M.S.</span>
  <div class="member-body">
    <div class="member-name">Aitiana V.S. Ismodes</div>
    <div class="member-degree">M.S. (2025~)</div>
    <div class="member-topics">
      <span class="member-topic">Digital Rock</span>
      <span class="member-topic">CCS</span>
    </div>
  </div>
</div>

<div class="member-card">
  <img class="member-photo" src="https://raw.githubusercontent.com/PetroInha/petroinha.github.io/main/_images/_JHSeol.png" alt="설정환">
  <span class="member-badge badge-ms">M.S.</span>
  <div class="member-body">
    <div class="member-name">설정환</div>
    <div class="member-degree">M.S. (2025~)</div>
    <div class="member-topics">
      <span class="member-topic">Lithium Production</span>
      <span class="member-topic">CCS Injectivity</span>
    </div>
  </div>
</div>

<div class="member-card">
  <img class="member-photo" src="https://raw.githubusercontent.com/PetroInha/petroinha.github.io/main/_images/_jinwoo.PNG" alt="어진우">
  <span class="member-badge badge-ms">M.S.</span>
  <div class="member-body">
    <div class="member-name">어진우</div>
    <div class="member-degree">M.S. (2026~)</div>
    <div class="member-topics">
      <span class="member-topic">Generative AI</span>
      <span class="member-topic">Digital Rock</span>
    </div>
  </div>
</div>

<div class="member-card">
  <img class="member-photo" src="https://raw.githubusercontent.com/PetroInha/petroinha.github.io/main/_images/_jinwoo.PNG" alt="이용훈">
  <span class="member-badge badge-ms">M.S.</span>
  <div class="member-body">
    <div class="member-name">이용훈</div>
    <div class="member-degree">M.S. (2026~)</div>
    <div class="member-topics">
      <span class="member-topic">SAGD Simulation</span>
      <span class="member-topic">Experiment</span>
    </div>
  </div>
</div>

</div>


<div class="data-flow"></div>


<!-- ════════════════ UNDERGRADS ════════════════ -->
<div class="mem-section-title">Undergraduate Interns</div>

<div class="intern-chips">
  <span class="intern-chip">정지혜 · SAGD</span>
  <span class="intern-chip">김보희 · ML</span>
  <span class="intern-chip" style="opacity:0.55;">최유미 · ML</span>
  <span class="intern-chip" style="opacity:0.55;">강태구 · ML</span>
</div>

<div class="recruit-note">
  <strong>학부연구생 상시모집중</strong> — 에너지·AI·지구과학에 관심 있는 학부생을 환영합니다.<br>
  Contact: <a href="mailto:honggeun.jo@inha.ac.kr">honggeun.jo@inha.ac.kr</a>
</div>


<div class="data-flow"></div>


<!-- ════════════════ ALUMNI ════════════════ -->
<div class="mem-section-title">Alumni</div>

<!-- Ph.D. Alumni -->
<p style="font-size:13px;font-weight:700;text-transform:uppercase;letter-spacing:0.8px;color:#005BAC;margin:0 0 14px;">Ph.D.</p>
<div class="alumni-cards">

<div class="alumni-card">
  <div class="alumni-name">Viet Nguyen-Le</div>
  <div class="alumni-meta">Ph.D. · 2022.2</div>
  <div class="alumni-dest">Geological Survey of Canada <span>Government</span></div>
  <div class="alumni-topics">Shale Gas · EGR · SAGD</div><br>
  <a class="alumni-link" href="https://scholar.google.com/citations?user=48-9_CgAAAAJ" target="_blank">Google Scholar →</a>
</div>

<div class="alumni-card">
  <div class="alumni-name">김민</div>
  <div class="alumni-meta">Ph.D. · 2020.8</div>
  <div class="alumni-dest">한국석유공사 <span>KNOC</span></div>
  <div class="alumni-topics">Heavy Oil Recovery · EOR · ML · CCUS</div><br>
  <a class="alumni-link" href="https://scholar.google.co.kr/citations?user=-aINUeYAAAAJ" target="_blank">Google Scholar →</a>
</div>

</div>

<!-- M.S. Alumni — Recent (2022+) as cards -->
<p style="font-size:13px;font-weight:700;text-transform:uppercase;letter-spacing:0.8px;color:#00838f;margin:24px 0 14px;">M.S. — Recent</p>
<div class="alumni-cards">

<div class="alumni-card ms">
  <div class="alumni-name">박은실</div>
  <div class="alumni-meta">M.S. · 2026.2</div>
  <div class="alumni-dest">SLB (Schlumberger) <span>Industry</span></div>
  <div class="alumni-topics">InSAR · THM Simulation · CCS Monitoring</div>
</div>

<div class="alumni-card ms">
  <div class="alumni-name">공희성</div>
  <div class="alumni-meta">M.S. · 2025.3</div>
  <div class="alumni-dest">한국석유공사 <span>KNOC</span></div>
  <div class="alumni-topics">ES-SAGD</div>
</div>

<div class="alumni-card ms">
  <div class="alumni-name">김현민</div>
  <div class="alumni-meta">M.S. · 2025.3</div>
  <div class="alumni-dest">삼성중공업 해양엔지니어링팀 <span>Industry</span></div>
  <div class="alumni-topics">4D Seismic · CCS Monitoring</div><br>
  <a class="alumni-link" href="https://pubs.geoscienceworld.org/gsw/lithosphere/article/2024/4/lithosphere_2024_209/650382/" target="_blank">Publication →</a>
</div>

<div class="alumni-card ms">
  <div class="alumni-name">백인욱</div>
  <div class="alumni-meta">M.S. · 2025.3</div>
  <div class="alumni-dest">국토교통과학기술진흥원 <span>Government</span></div>
  <div class="alumni-topics">CO₂-EGR · CCS</div>
</div>

<div class="alumni-card ms">
  <div class="alumni-name">백진현</div>
  <div class="alumni-meta">M.S. · 2025.3</div>
  <div class="alumni-dest">한국에너지기술연구원 <span>Research</span></div>
  <div class="alumni-topics">SAGD · Oil Sands</div>
</div>

<div class="alumni-card ms">
  <div class="alumni-name">Yenny Andrea Rincon Cuenca</div>
  <div class="alumni-meta">M.S. · 2024.8</div>
  <div class="alumni-dest">Ecopetrol <span>Industry</span></div>
  <div class="alumni-topics">CCS Storage Capacity Modeling</div>
</div>

</div>

<!-- M.S. Alumni — Earlier as compact list -->
<p style="font-size:13px;font-weight:700;text-transform:uppercase;letter-spacing:0.8px;color:#00838f;margin:24px 0 12px;">M.S. — Earlier</p>
<ul class="alumni-list">
  <li><span class="aln">신현수</span><span class="alyear">2020.2</span><span class="aldest">포스코인터네셔널</span><span class="altopic">Shale Gas DCA</span></li>
  <li><span class="aln">양형서</span><span class="alyear">2020.2</span><span class="aldest">한국석유공사</span><span class="altopic">Shale Gas · EGR · SAGD</span></li>
  <li><span class="aln">이준용</span><span class="alyear">2019.2</span><span class="aldest">한국석유공사</span><span class="altopic">Oil Sands · SAGD</span></li>
  <li><span class="aln">전창혁</span><span class="alyear">2019.2</span><span class="aldest">포스코인터네셔널</span><span class="altopic">포항분지 CCS</span></li>
  <li><span class="aln">윤지수</span><span class="alyear">2018.8</span><span class="aldest">前 정보통신기획평가원</span><span class="altopic">Oil Sands · SAGD</span></li>
  <li><span class="aln">김가람</span><span class="alyear">2018.8</span><span class="aldest">한국수자원공사</span><span class="altopic">Oil Sands · SAGD</span></li>
  <li><span class="aln">손국희</span><span class="alyear">2018.2</span><span class="aldest">중소기업기술정보진흥원</span><span class="altopic">Oil Sands · SAGD</span></li>
  <li><span class="aln">김정호</span><span class="alyear">2015.2</span><span class="aldest">LG 에너지솔루션</span><span class="altopic">Oil Sands · SAGD</span></li>
</ul>

<!-- Bachelor's Alumni -->
<p style="font-size:13px;font-weight:700;text-transform:uppercase;letter-spacing:0.8px;color:#888;margin:24px 0 14px;">Bachelor's</p>
<div class="alumni-cards">

<div class="alumni-card bs">
  <div class="alumni-name">고메스</div>
  <div class="alumni-meta">B.S. · 2024.8</div>
  <div class="alumni-dest">현대건설 신재생에너지사업부 <span>Industry</span></div>
  <div class="alumni-topics">Renewable Energy</div>
</div>

<div class="alumni-card bs">
  <div class="alumni-name">한솔</div>
  <div class="alumni-meta">B.S. · 2024.8</div>
  <div class="alumni-dest">포스코인터네셔널 <span>Industry</span></div>
  <div class="alumni-topics">Mineral Exploration</div>
</div>

<div class="alumni-card bs">
  <div class="alumni-name">조지원</div>
  <div class="alumni-meta">B.S. · 2024.8</div>
  <div class="alumni-dest">지멘스 코리아 <span>Industry</span></div>
  <div class="alumni-topics">Blue Hydrogen</div>
</div>

<div class="alumni-card bs">
  <div class="alumni-name">성준</div>
  <div class="alumni-meta">B.S. · 2024.2</div>
  <div class="alumni-dest">효성중공업 <span>Industry</span></div>
  <div class="alumni-topics">Geological Modeling</div>
</div>

<div class="alumni-card bs">
  <div class="alumni-name">전희진</div>
  <div class="alumni-meta">B.S. · 2023.8</div>
  <div class="alumni-dest">TBU</div>
  <div class="alumni-topics">Geological Modeling</div>
</div>

</div>


<div class="data-flow"></div>


<!-- ════════════════ STATS ════════════════ -->
<div class="stat-grid">
  <div class="stat-card hl">
    <div class="stat-num" data-target="95">0</div>
    <div class="stat-lbl">Industry Placement Rate (%)</div>
  </div>
  <div class="stat-card">
    <div class="stat-num" data-target="21">0</div>
    <div class="stat-lbl">Graduated Students</div>
  </div>
  <div class="stat-card">
    <div class="stat-num" data-target="8">0</div>
    <div class="stat-lbl">Partner Companies &amp; Institutes</div>
  </div>
  <div class="stat-card">
    <div class="stat-num" data-target="5">0</div>
    <div class="stat-lbl">Countries Represented</div>
  </div>
</div>

<script>
(function(){
  var counters = document.querySelectorAll('.stat-num[data-target]');
  var started = false;
  function runCounters(){
    if(started) return;
    started = true;
    counters.forEach(function(el){
      var target = +el.getAttribute('data-target');
      var duration = 1200;
      var step = Math.ceil(duration / (target * 10));
      var cur = 0;
      var timer = setInterval(function(){
        cur = Math.min(cur + Math.ceil(target/60), target);
        el.textContent = cur;
        if(cur >= target) clearInterval(timer);
      }, step);
    });
  }
  if('IntersectionObserver' in window){
    var obs = new IntersectionObserver(function(entries){
      if(entries[0].isIntersecting) runCounters();
    }, {threshold:0.3});
    obs.observe(document.querySelector('.stat-grid'));
  } else {
    runCounters();
  }
})();
</script>
