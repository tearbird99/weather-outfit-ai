import os
import requests
from google import genai
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
from datetime import datetime

# 환경 변수 로드
load_dotenv()

app = Flask(__name__)
CORS(app)

# API 키 설정
SERVICE_KEY = os.getenv("WEATHER_API_KEY")
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def get_base_time():
    # 기상청 발표 시간 계산
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
    # 좌표 파라미터 수신
    nx = request.args.get('nx', default=60, type=int)
    ny = request.args.get('ny', default=127, type=int)
    
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
        # 기상청 데이터 호출
        r = requests.get(url, params=params)
        items = r.json()['response']['body']['items']['item']
        
        # 기온, 습도, 풍속 추출
        w = {i['category']: i['fcstValue'] for i in items if i['category'] in ['TMP', 'REH', 'WSD']}
        
        # Gemini 3 프리뷰 모델 호출
        prompt = f"기온 {w['TMP']}도, 습도 {w['REH']}%, 풍속 {w['WSD']}m/s. 한 문장 코디 추천."
        response = client.models.generate_content(
            model="gemini-3-flash-preview", 
            contents=prompt
        )
        
        return jsonify({
            "success": True,
            "weather": w,
            "recommendation": response.text
        })

    except Exception as e:
        # 에러 로그 출력
        print(f"DEBUG: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)