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
    
        # 추출 카테고리 확장: POP(강수확률), PCP(강수량) 추가
        w = {i['category']: i['fcstValue'] for i in items if i['category'] in ['TMP', 'REH', 'WSD', 'POP', 'PCP', 'SKY', 'PTY']}
    
        # 체감온도 계산 로직 유지
        tmp = float(w['TMP'])
        wsd = float(w['WSD'])
        feels_like = round(13.12 + 0.6215 * tmp - 11.37 * math.pow(wsd * 3.6, 0.16) + 0.3965 * tmp * math.pow(wsd * 3.6, 0.16), 1)

        # Prompt에 강수 정보 추가하여 코디 조언 정교화
        prompt = f"""
        위치: {lat}, {lon} / 날씨: 기온 {w['TMP']}도(체감 {feels_like}도), 강수확률 {w['POP']}%, 강수량 {w['PCP']}, 습도 {w['REH']}%, 풍속 {w['WSD']}m/s.
        1. 행정구역(동, 읍, 면).
        2. Lucide 아이콘(Sun, Cloud, CloudRain, Snow).
        3. 날씨와 강수여부를 고려한 한 문장 코디 추천.
        답변 형식: [행정구역] | [아이콘명] | [코디 추천]
        """
    
        response = client.models.generate_content(model="gemini-3-flash-preview", contents=prompt)
        ai_parts = response.text.strip().split("|")
        
        address = ai_parts[0].strip() if len(ai_parts) > 0 else "지역 불명"
        icon_type = ai_parts[1].strip() if len(ai_parts) > 1 else "Cloud"
        recommendation = ai_parts[2].strip() if len(ai_parts) > 2 else ai_parts[0]

        return jsonify({
            "success": True,
            "weather": {**w, "FEELS": feels_like},
            "recommendation": recommendation,
            "address": address,
            "icon": icon_type,
            "server_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)