import os
import requests
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

app = Flask(__name__)
CORS(app) # Next.js 통신 허용

SERVICE_KEY = os.getenv("WEATHER_API_KEY")
BASE_URL = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst"

def get_base_time():
    # 기상청 발표 시간 기준 계산
    now = datetime.now()
    times = [2, 5, 8, 11, 14, 17, 20, 23]
    current_hour = now.hour
    
    latest_time = 2
    for t in times:
        if current_hour >= t:
            latest_time = t
        else:
            break
            
    return f"{latest_time:02d}00"

@app.route('/api/weather', methods=['GET'])
def fetch_weather():
    # 좌표 파라미터 수신 (기본값 서울)
    nx = request.args.get('nx', default=60, type=int)
    ny = request.args.get('ny', default=127, type=int)
    
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
        response = requests.get(BASE_URL, params=params)
        data = response.json()

        if data['response']['header']['resultCode'] == '00':
            items = data['response']['body']['items']['item']
            
            # 기온, 습도, 풍속, 강수형태 추출
            result = {}
            for item in items:
                if item['category'] in ['TMP', 'REH', 'WSD', 'PTY']:
                    result[item['category']] = item['fcstValue']
            
            return jsonify({"success": True, "data": result})
        return jsonify({"success": False, "message": "API error"}), 400

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)