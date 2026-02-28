"use client";

import { useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";

export default function Home() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Flask 백엔드 API 데이터 호출
    fetch("http://localhost:5000/api/weather?nx=60&ny=127")
      .then((res) => res.json())
      .then((json) => {
        if (json.success) setData(json);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Fetch error:", err);
        setLoading(false);
      });
  }, []);

  if (loading) return <div className="p-10 text-gray-900 dark:text-gray-100">로딩 중...</div>;
  if (!data) return <div className="p-10 text-gray-900 dark:text-gray-100">데이터 없음</div>;

  return (
    <main className="p-10 font-sans min-h-screen bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 transition-colors">
      <h1 className="text-2xl font-bold mb-6">오늘의 날씨 코디</h1>
      
      {/* 날씨 정보 섹션 */}
      <section className="mb-8 p-6 bg-gray-100 dark:bg-gray-800 rounded-lg">
        <h2 className="text-lg font-semibold mb-4 text-gray-800 dark:text-gray-200">현재 날씨</h2>
        <div className="flex gap-10">
          <div>
            <p className="text-sm text-gray-500 dark:text-gray-400">기온</p>
            <p className="text-xl font-bold">{data.weather.TMP}°C</p>
          </div>
          <div>
            <p className="text-sm text-gray-500 dark:text-gray-400">습도</p>
            <p className="text-xl font-bold">{data.weather.REH}%</p>
          </div>
          <div>
            <p className="text-sm text-gray-500 dark:text-gray-400">풍속</p>
            <p className="text-xl font-bold">{data.weather.WSD}m/s</p>
          </div>
        </div>
      </section>

      {/* AI 코디 추천 섹션 (마크다운 적용) */}
      <section className="p-6 bg-blue-50 dark:bg-blue-950 border border-blue-100 dark:border-blue-800 rounded-lg">
        <h2 className="text-lg font-semibold mb-2 text-blue-900 dark:text-blue-200">AI 추천 코디</h2>
        <div className="text-blue-900 dark:text-blue-200 leading-relaxed prose dark:prose-invert max-w-none">
          <ReactMarkdown>{data.recommendation}</ReactMarkdown>
        </div>
      </section>
    </main>
  );
}