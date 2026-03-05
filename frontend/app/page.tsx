"use client";

import { useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";
import { 
  Sun, Cloud, CloudRain, Snowflake, 
  Thermometer, Droplets, Wind, 
  Umbrella, Waves 
} from "lucide-react";

// 날씨 아이콘 매핑 (Snowflake로 렌더링 오류 방지)
const WeatherIcon = ({ name, size = 24 }: { name: string, size?: number }) => {
  switch (name) {
    case "Sun": return <Sun size={size} className="text-orange-500" />;
    case "CloudRain": return <CloudRain size={size} className="text-blue-500" />;
    case "Snow": return <Snowflake size={size} className="text-blue-200" />;
    default: return <Cloud size={size} className="text-gray-400" />;
  }
};

export default function Home() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // 위치 기반 날씨 데이터 호출 (GPS 미승인 시 서울 좌표 사용)
    const getWeatherData = (lat?: number, lon?: number) => {
      const query = lat && lon ? `lat=${lat}&lon=${lon}` : `nx=60&ny=127`;
      fetch(`https://weather-outfit-ai-ey6r.onrender.com/api/weather?${query}`)
        .then(res => res.json())
        .then(json => {
          if (json.success) setData(json);
          setLoading(false);
        }).catch(() => setLoading(false));
    };

    // 브라우저 Geolocation API 연동
    if ("geolocation" in navigator) {
      navigator.geolocation.getCurrentPosition(
        (pos) => getWeatherData(pos.coords.latitude, pos.coords.longitude),
        () => getWeatherData()
      );
    } else { getWeatherData(); }
  }, []);

  if (loading) return <div className="p-10 text-center font-sans">날씨 정보를 가져오는 중...</div>;
  if (!data) return <div className="p-10 text-center font-sans">데이터를 불러올 수 없습니다.</div>;

  return (
    // 대화면 대응을 위해 max-w-5xl로 확장
    <main className="p-10 max-w-5xl mx-auto font-sans min-h-screen bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 transition-colors">
      {/* 헤더: 주소, 조회 시간, 현재 상태 아이콘 */}
      <header className="mb-12 flex justify-between items-end border-b pb-8 border-gray-100 dark:border-gray-800">
        <div>
          <h1 className="text-4xl font-black mb-3 tracking-tighter">오늘의 동네 코디</h1>
          <div className="flex items-center gap-4 text-sm text-gray-500">
            <p className="text-blue-500 font-bold text-xl flex items-center gap-1">📍 {data.address}</p>
            <span>|</span>
            <p>📅 {data.server_time}</p>
          </div>
        </div>
        <div className="bg-gray-50 dark:bg-gray-800 p-6 rounded-3xl shadow-sm flex items-center gap-4">
          <span className="text-lg font-medium opacity-60">현재 상태</span>
          <WeatherIcon name={data.icon} size={64} />
        </div>
      </header>
      
      {/* 3열 그리드: 온도/체감온도, 강수 정보, 풍속/습도 */}
      <section className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10 text-sm">
        <div className="p-8 bg-gray-50 dark:bg-gray-800 rounded-[2.5rem] flex flex-col justify-center">
          <div className="flex items-center gap-2 mb-2 opacity-50"><Thermometer size={18} /><p className="font-bold uppercase tracking-widest text-[10px]">Temperature</p></div>
          <div className="flex items-baseline gap-3">
            <span className="text-6xl font-black">{data.weather.TMP}°</span>
            <span className="text-xl text-gray-400 font-semibold">체감 {data.weather.FEELS}°</span>
          </div>
        </div>

        <div className="p-8 bg-blue-50/50 dark:bg-blue-900/20 rounded-[2.5rem] flex flex-col justify-center border border-blue-100/50 dark:border-blue-800/30">
          <div className="flex items-center gap-2 mb-4 opacity-60 text-blue-600 dark:text-blue-400"><Umbrella size={20} /><p className="font-bold uppercase tracking-widest text-[10px]">Precipitation</p></div>
          <p className="text-3xl font-black">{data.weather.POP}% <span className="text-lg opacity-40">/ {data.weather.PCP}</span></p>
          <p className="text-xs mt-2 opacity-50">강수확률 및 예상 강수량</p>
        </div>

        <div className="grid grid-rows-2 gap-4">
          <div className="p-5 bg-green-50/50 dark:bg-green-900/20 rounded-3xl flex items-center justify-between px-8 border border-green-100/50 dark:border-green-800/30">
            <div className="flex items-center gap-3"><Wind size={24} className="text-green-500" /><span className="font-bold">풍속</span></div>
            <p className="text-2xl font-black">{data.weather.WSD}<span className="text-sm ml-1 font-normal opacity-50">m/s</span></p>
          </div>
          <div className="p-5 bg-orange-50/50 dark:bg-orange-900/20 rounded-3xl flex items-center justify-between px-8 border border-orange-100/50 dark:border-orange-800/30">
            <div className="flex items-center gap-3"><Droplets size={24} className="text-orange-500" /><span className="font-bold">습도</span></div>
            <p className="text-2xl font-black">{data.weather.REH}<span className="text-sm ml-1 font-normal opacity-50">%</span></p>
          </div>
        </div>
      </section>

      {/* AI 추천 코디 결과 하단 배치 */}
      <section className="p-10 bg-blue-600 text-white rounded-[3rem] shadow-2xl shadow-blue-200 dark:shadow-none">
        <div className="flex items-center gap-3 mb-6">
          <div className="px-3 py-1 bg-white/20 rounded-full text-[10px] font-bold tracking-widest uppercase">AI Style Guide</div>
        </div>
        <div className="text-2xl font-medium leading-relaxed tracking-tight break-keep">
          <ReactMarkdown>{data.recommendation}</ReactMarkdown>
        </div>
      </section>
    </main>
  );
}