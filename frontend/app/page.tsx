"use client";

import { useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";

export default function Home() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // 날씨 데이터 호출 함수 (위경도 유무에 따라 쿼리 분기)
    const getWeatherData = (lat?: number, lon?: number) => {
      const query = lat && lon ? `lat=${lat}&lon=${lon}` : `nx=60&ny=127`;
      const url = `http://localhost:5000/api/weather?${query}`;

      fetch(url)
        .then((res) => res.json())
        .then((json) => {
          if (json.success) setData(json);
          setLoading(false);
        })
        .catch(() => setLoading(false));
    };

    // 브라우저 Geolocation API를 이용한 위치 정보 획득
    if ("geolocation" in navigator) {
      navigator.geolocation.getCurrentPosition(
        (pos) => getWeatherData(pos.coords.latitude, pos.coords.longitude),
        () => getWeatherData() // 권한 거부 시 기본 좌표 사용
      );
    } else {
      getWeatherData();
    }
  }, []);

  // 로딩 및 에러 처리 UI
  if (loading) return <div className="p-10 text-gray-900 dark:text-gray-100">위치 동기화 중...</div>;
  if (!data) return <div className="p-10 text-gray-900 dark:text-gray-100">데이터를 불러올 수 없습니다.</div>;

  return (
    <main className="p-10 font-sans min-h-screen bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 transition-colors">
      {/* 헤더: 시간 및 AI가 추출한 행정동 표시 */}
      <header className="mb-8">
        <h1 className="text-3xl font-black mb-2 tracking-tight">오늘의 동네 코디</h1>
        <div className="text-sm space-y-1">
          <p className="text-gray-400">📅 조회 시각: {data.server_time}</p>
          <div className="flex items-center gap-1 text-blue-500 font-bold text-lg">
            <span className="text-xl">📍</span>
            <p>{data.address}</p>
          </div>
        </div>
      </header>

      {/* 날씨 정보 카드 (기온, 습도, 풍속) */}
      <section className="mb-8 p-6 bg-gray-50 dark:bg-gray-800 rounded-2xl border border-gray-100 dark:border-gray-700">
        <h2 className="text-xs uppercase tracking-widest font-bold mb-4 opacity-50">Weather Report</h2>
        <div className="flex justify-between items-center max-w-sm">
          <div>
            <p className="text-xs opacity-60">온도</p>
            <p className="text-3xl font-black">{data.weather.TMP}°</p>
          </div>
          <div className="w-px h-8 bg-gray-200 dark:bg-gray-700"></div>
          <div>
            <p className="text-xs opacity-60">습도</p>
            <p className="text-3xl font-black">{data.weather.REH}%</p>
          </div>
          <div className="w-px h-8 bg-gray-200 dark:bg-gray-700"></div>
          <div>
            <p className="text-xs opacity-60">바람</p>
            <p className="text-3xl font-black">{data.weather.WSD}m/s</p>
          </div>
        </div>
      </section>

      {/* AI 코디 추천 결과 (마크다운 렌더링) */}
      <section className="p-8 bg-blue-600 text-white rounded-3xl shadow-xl shadow-blue-200 dark:shadow-none">
        <h2 className="text-sm font-bold mb-4 opacity-80 uppercase tracking-tighter">AI Style Advice</h2>
        <div className="text-xl font-medium leading-snug">
          <ReactMarkdown>{data.recommendation}</ReactMarkdown>
        </div>
      </section>
    </main>
  );
}