# 🌤️ Weather Outfit AI: 실시간 위치 기반 AI 코디네이터

---

## 📌 프로젝트 개요

사용자의 실시간 GPS 좌표를 분석하여 기상청의 정밀한 단기예보 데이터를 가져오고, 이를 생성형 AI인 Gemini 3 Flash가 분석하여 최적의 의상을 추천해 주는 풀스택 웹 애플리케이션입니다. 단순한 수치 제공을 넘어, 사용자가 직관적으로 오늘 무엇을 입을지 결정할 수 있도록 돕는 대시보드를 제공합니다.

---

## 🎯 주요 기능

* **Real-time Geolocation:** 브라우저 API를 통해 사용자의 현재 위도/경도를 수집하고, 기상청 격자 좌표로 정밀하게 변환하여 동네 날씨를 조회합니다.
* **AI Address Mapping:** 위경도 좌표를 바탕으로 Gemini 3 모델이 현재 사용자가 위치한 실제 행정동(동, 읍, 면) 명칭을 유추하여 화면에 표시합니다.
* **Detailed Weather Dashboard:** 기온, 습도, 풍속은 물론 체감온도, 강수확률, 강수량 등의 핵심 기상 지표를 시각화합니다.
* **AI Style Advice:** Gemini 3 Flash 모델을 활용하여 현재 기상 조건에 최적화된 코디네안을 마크다운 형식으로 생성하여 제공합니다.

---

## 🛠️ 기술 스택 및 배포

**Frontend (웹 인터페이스 및 렌더링)**

* `Next.js`: 고성능 컴포넌트 기반 UI 프레임워크 사용
* `Tailwind CSS`: 다크 모드 및 반응형 그리드 레이아웃 구현
* `Lucide React`: 직관적인 기상 상태 표현을 위한 벡터 아이콘 라이브러리 연동
* `React-Markdown`: AI가 생성한 마크다운 형식의 조언을 깔끔한 UI로 렌더링

**Backend (API 서버 및 데이터 처리)**

* `Python`: 백엔드 비즈니스 로직 작성
* `Flask`: 가볍고 유연한 REST API 서버 구축
* `Google Generative AI`: 최신 LLM을 이용한 위치 기반 텍스트 생성
* `Flask-CORS`: 프론트엔드와 백엔드 간의 안전한 통신 환경 설정

**Data Pipeline**

* `기상청 단기예보 API`: 공공데이터포털을 통한 실시간 격자 데이터 수집
* `LCC 변환 알고리즘`: 위경도 ↔ 격자 좌표 간의 수학적 좌표 변환 로직 내장

---

## 🚀 로컬 환경 실행 방법

**Backend 서버 실행**

```bash
cd backend
# 가상환경 생성 및 활성화 권장
pip install -r requirements.txt
python main.py

```

**Frontend 클라이언트 실행**

```bash
cd frontend
npm install
npm run dev

```

---

## 📅 프로젝트 히스토리

* **2026.02.27:** 날씨 정보 조회 API 구현
* **2026.02.28:** 실시간 GPS 연동 및 Gemini 3 모델 기반 위치 추정
* **2026.03.01:** 대시보드 UI 고도화 작업 완료