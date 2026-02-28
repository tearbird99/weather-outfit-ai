import os
import math
import requests
from google import genai
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

app = Flask(__name__)
CORS(app) # 프론트엔드 통신 허용

# API 키 및 클라이언트 설정
SERVICE_KEY = os.getenv("WEATHER_API_KEY")
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# 기상청 LCC 투영법 변환 상수
RE = 6371.00877
GRID = 5.0
SLAT1 = 30.0
SLAT2 = 60.0
OLON = 126.0
OLAT = 38.0
XO = 43
YO = 136

def convert_to_grid(lat, lon):
    """위경도를 기상청 격자 좌표(nx, ny)로 변환"""
    PI = math.pi
    DEGRAD = PI / 180.0
    re = RE / GRID
    slat1 = SLAT1 * DEGRAD
    slat2 = SLAT2 * DEGRAD
    olon = OLON * DEGRAD
    olat = OLAT * DEGRAD
    sn = math.tan(PI * 0.25 + slat2 * 0.5) / math.tan(PI * 0.25 + slat1 * 0.5)
    sn = math.log(math.cos(slat1) / math.cos(slat2)) / math.log(sn)
    sf = math.tan(PI * 0.25 + slat1 * 0.5)
    sf = math.pow(sf, sn) * math.cos(slat1) / sn
    ro = math.tan(PI * 0.25 + olat * 0.5)
    ro = re * sf / math.pow(ro, sn)
    ra = math.tan(PI * 0.25 + lat * DEGRAD * 0.5)
    ra = re * sf / math.pow(ra, sn)
    theta = lon * DEGRAD - olon
    if theta > PI: theta -= 2.0 * PI
    if theta < -PI: theta += 2.0 * PI
    theta *= sn
    nx = math.floor(ra * math.sin(theta) + XO + 0.5)
    ny = math.floor(ro - ra * math.cos(theta) + YO + 0.5)
    return int(nx), int(ny)

def get_base_time():
    """기상청 데이터 발표 시각 계산"""
    now = datetime.now()
    times = [2, 5, 8, 11, 14, 17, 20, 23]
    h = now.hour
    latest = 2
    for t in times:
        if h >= t: latest = t
        else: break
    return f"{latest:02d}00"

@app.route('/api/weather', methods=['GET'])
def fetch_weather():
    lat = request.args.get('lat', type=float)
    lon = request.args.get('lon', type=float)

    # 좌표 변환 또는 기본값 설정
    if lat and lon:
        nx, ny = convert_to_grid(lat, lon)
    else:
        nx, ny = 60, 127
    
    # 기상청 단기예보 API 호출
    url = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst"
    params = {
        'serviceKey': SERVICE_KEY,
        'pageNo': '1',
        'numOfRows': '1000',
        'dataType': 'JSON',
        'base_date': datetime.now().strftime("%Y%m%d"),
        'base_time': get_base_time(),
        'nx': nx,
        'ny': ny
    }

    try:
        r = requests.get(url, params=params)
        items = r.json()['response']['body']['items']['item']
        # 기온, 습도, 풍속 데이터 추출
        w = {i['category']: i['fcstValue'] for i in items if i['category'] in ['TMP', 'REH', 'WSD']}
        
        # AI에게 위치 유추 및 코디 추천 요청
        prompt = f"""
        위도 {lat}, 경도 {lon} (기상청 격자 {nx}, {ny}) 지역의 날씨는 기온 {w['TMP']}도, 습도 {w['REH']}%, 풍속 {w['WSD']}m/s야.
        1. 이 좌표가 속한 한국의 '동, 읍, 면' 단위 행정구역 명칭을 찾아줘.
        2. 해당 지역 날씨에 맞는 코디를 한 문장으로 추천해줘.
        답변 형식: [행정구역 명칭] | [코디 추천 내용]
        """
        
        response = client.models.generate_content(
            model="gemini-3-flash-preview", 
            contents=prompt
        )
        
        # AI 응답 파싱 및 예외 처리
        ai_text = response.text.strip()
        if "|" in ai_text:
            address, recommendation = ai_text.split("|")
        else:
            address = f"격자 {nx}, {ny} 인근"
            recommendation = ai_text

        return jsonify({
            "success": True,
            "weather": w,
            "recommendation": recommendation.strip(),
            "address": address.strip(),
            "server_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)