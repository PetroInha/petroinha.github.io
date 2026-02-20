---
layout: page
title: Lectures
permalink: /Lectures/
---

# 📚 Courses & Teaching

Our curriculum integrates **geoscience, engineering, digital technology, and AI**  
to educate future leaders in geoenergy and carbon-neutral systems.

---

# 🧭 전공기초 교과목

Fundamental courses that build core knowledge in subsurface science and computational skills.

1. 에너지자원지질 (Energy Resources Geology)  
2. 컴퓨터 프로그래밍  

---

# 🌱 탄소중립 Track 교과목

Focused on sustainable energy systems, decarbonization technologies, and energy data science.

1. 신재생에너지 (Renewable Energy)  
2. 미래가스공학 (Natural Gas Engineering)  
3. 에너지 빅데이터 (Energy Big Data)  
4. 에너지자원과 인공지능 (Energy Resources and AI)  

---

# 🌍 지오에너지 Track 교과목

Advanced engineering courses covering subsurface energy systems and carbon storage technologies.

1. 지오에너지공학개론 (Introduction to GeoEnergy Engineering)  
2. 이산화탄소 포집 및 저장 기술 (CO2 Capture and Storage Technology)  
3. 시추 및 지층평가공학 (Drilling and Foramtion Evaluation Engineering)  
4. 지오에너지 모델링 (GeoEnergy Modelling)  
5. 지오에너지 생산 및 설비 (Geoenergy Production and Facility)  
6. 비전통석유개발  

---

# 🎓 대학원 교과목

Research-oriented advanced courses integrating modeling, AI, and energy transition technologies.

1. 추계학적 지구통계 모델링 (Stochastical Modelling)  
2. 지오에너지 머신러닝 (GeoEnergy Machine Learning)  
3. 기후환경과 에너지기술  
4. 가스공학특론  
5. 디지털 트윈과 저류층 시뮬레이션  
6. 탄소감축 및 기후변화 대응기술  
7. 에너지산업과 신재생에너지  
8. 신재생에너지 산업 및 기술 동향  
9. 인류의 그림자, 에너지 바로 알기  

---
## 🗺️ <span style="color:#005BAC;"><strong>Curriculum Map</strong></span>

```mermaid
flowchart TB

%% ========= Styles =========
classDef core fill:#E8F2FF,stroke:#005BAC,stroke-width:2px,color:#003B6D;
classDef carbon fill:#F0FBF6,stroke:#2E8B57,stroke-width:2px,color:#1F5C3A;
classDef geo fill:#FFF3E8,stroke:#E67E22,stroke-width:2px,color:#7A3E00;
classDef grad fill:#F5F0FF,stroke:#6F42C1,stroke-width:2px,color:#3B2473;

%% ========= Nodes =========
subgraph CORE["🧭 전공기초 교과목"]
direction TB
C1["에너지자원지질<br/>(Energy Resources Geology)"]:::core
C2["컴퓨터 프로그래밍"]:::core
end

subgraph CARBON["🌱 탄소중립 Track 교과목"]
direction TB
T1["신재생에너지<br/>(Renewable Energy)"]:::carbon
T2["미래가스공학<br/>(Natural Gas Engineering)"]:::carbon
T3["에너지 빅데이터<br/>(Energy Big Data)"]:::carbon
T4["에너지자원과 인공지능<br/>(Energy Resources and AI)"]:::carbon
end

subgraph GEO["🌍 지오에너지 Track 교과목"]
direction TB
G1["지오에너지공학개론<br/>(Introduction to GeoEnergy Engineering)"]:::geo
G2["이산화탄소 포집 및 저장 기술<br/>(CO2 Capture and Storage Technology)"]:::geo
G3["시추 및 지층평가공학<br/>(Drilling and Foramtion Evaluation Engineering)"]:::geo
G4["지오에너지 모델링<br/>(GeoEnergy Modelling)"]:::geo
G5["지오에너지 생산 및 설비<br/>(Geoenergy Production and Facility)"]:::geo
G6["비전통석유개발"]:::geo
end

subgraph GRAD["🎓 대학원 교과목"]
direction TB
M1["추계학적 지구통계 모델링<br/>(Stochastical Modelling)"]:::grad
M2["지오에너지 머신러닝<br/>(GeoEnergy Machine Learning)"]:::grad
M3["디지털 트윈과 저류층 시뮬레이션"]:::grad
M4["가스공학특론"]:::grad
M5["기후환경과 에너지기술"]:::grad
M6["탄소감축 및 기후변화 대응기술"]:::grad
M7["에너지산업과 신재생에너지"]:::grad
M8["신재생에너지 산업 및 기술 동향"]:::grad
M9["인류의 그림자, 에너지 바로 알기"]:::grad
end

%% ========= Core → Tracks =========
C1 --> G1
C1 --> G2
C1 --> G3
C2 --> T3
C2 --> T4
C2 --> G4

%% ========= Track Internal Links =========
T3 --> T4
G1 --> G4
G3 --> G4
G4 --> G5
G5 --> G6
G2 --> G4

%% ========= Cross-Track Bridges =========
T2 --> G2
T4 --> G2
T4 --> G4
T3 --> M2

%% ========= Tracks → Graduate =========
G4 --> M3
G2 --> M6
G1 --> M1
T4 --> M2
T2 --> M4
T1 --> M7
T1 --> M8
T2 --> M4
T3 --> M2
G4 --> M1

%% ========= Graduate Synergies =========
M1 --> M2
M2 --> M3
M5 --> M6
M7 --> M8