from flask import Flask, request, jsonify, render_template
import requests
import time
from datetime import datetime
from flask_cors import CORS
from concurrent.futures import ThreadPoolExecutor, as_completed
from sign import get_sign
import random
import math
import logging

# logging.basicConfig(filename='daka_app.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logging.basicConfig(filename='/home/ubuntu/daka_app.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


app = Flask(__name__)
CORS(app)  # 允许所有源跨域访问

def get_headers(token):
    return {
        'Authorization': f'Bearer {token}',
        'terminal': '0',
        'UNI-Request-Source': '4',
        'Pragma': 'no-cache',
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.53(0x1800352e) NetType/WIFI Language/zh_CN',
        'content-type': 'application/json'
    }
    
def fetch_data(url, headers):
    try:
        response = requests.get(url, headers=headers)
        return response.json()
    except Exception as e:
        logging.error(f"请求失败: {e}")
        return None

def get_account_info(token):
    try:
        headers = get_headers(token)
        # 使用并行请求加快响应速度
        with ThreadPoolExecutor() as executor:
            futures = {
                'response1': executor.submit(fetch_data, "https://api.hikiot.com/api-saas/v1/account/detail", headers),
                'response2': executor.submit(fetch_data, f"https://api.hikiot.com/api-attendance/v1/statistics/individual/daily?month={datetime.now().strftime('%Y-%m')}&personNo=&ID=myStatic", headers),
                'response3': executor.submit(fetch_data, "https://api.hikiot.com/api-attendance/mobile-clock/v1/individual-clock-rules", headers),
            }

            # 等待所有请求完成
            response1 = futures['response1'].result()
            response2 = futures['response2'].result()
            response3 = futures['response3'].result()

            if not response1 or not response2 or not response3:
                return False  # 如果任何一个请求失败，返回 False

            account_info = {
                'nick_name': response1['data'].get('nickName', '未设置昵称'),
                'phone': response1['data'].get('phone', '未绑定手机号'),
                'team_name': response2['data'].get('orgName', '无团队身份'),
                'name': response2['data'].get('personName', '未设置姓名'),
                'rule': response3['data'].get('shiftDetail', '未设置打卡规则'),
                'message': 'success'
            }
            logging.info(f"获取到用户信息: {account_info['name']}")

            return account_info

    except Exception as e:
        logging.error(f"发生错误: {e}")
        return False

@app.route('/api/test_token', methods=['POST'])
def test_token():
    data = request.get_json()
    token = data.get('token')
    if len(token) != 36:
        return jsonify({'message': 'token格式错误'})
    account_info = get_account_info(token)
    if account_info:
        return jsonify(account_info)
    else:
        return jsonify({'message': 'token无效 请重新获取'})

@app.route('/api/get_today_status', methods=['POST'])
def get_today_status():
    data = request.get_json()
    token = data.get('token')
    if len(token) != 36:
        return jsonify({'message': 'token格式错误'})
    # 获取今日打卡状态
    try:
        response = requests.request("GET", "https://api.hikiot.com/api-attendance/mobile-clock/v1/require-commuting", headers=get_headers(token)).json()
        if response['code'] == 0:
            return response['data']
        else:
            return jsonify({'message': '获取打卡状态失败'})
    except Exception as e:
        logging.error(f"出现错误: {e}")
        return jsonify({'message': 'token无效 请重新获取'})

@app.route('/api/get_daka_config', methods=['GET'])
def get_daka_config():
    return jsonify({
        'message': 'success', 
        'location': '南京农业大学(滨江校区)农学院',
        'address': '江苏省南京市浦口区江浦街道',
        'longitude': 118.636838,
        'latitude': 32.011898,
        'wifi': 'NJAU',
        'device_name': '微信小程序',
        'wifi_mac': '58:ae:a8:32:59:90'
        })


def add_random_offset(latitude, longitude, max_distance=50):
    # 纬度和经度单位转换
    lat_offset = max_distance / 111000  # 纬度偏移
    lng_offset = max_distance / (111000 * abs(math.cos(math.radians(latitude))))  # 经度偏移
    
    # 生成随机偏移，正负50米范围内
    new_latitude = latitude + random.uniform(-lat_offset, lat_offset)
    new_longitude = longitude + random.uniform(-lng_offset, lng_offset)
    
    return new_latitude, new_longitude
@app.route('/api/daka', methods=['POST'])
def daka():
    data = request.get_json()
    token = data.get('token')
    if len(token) != 36:
        return jsonify({'message': 'token格式错误'})
    # 打卡
    try:
        headers = get_headers(token)
        latitude = 32.011898
        longitude = 118.636838
        new_latitude, new_longitude = add_random_offset(latitude, longitude)
        data = {
            "deviceSerial": "",
            "longitude": new_longitude,
            "latitude": new_latitude,
            "clockSite": "江苏省南京市浦口区江浦街道南京农业大学(滨江校区)",
            "address": "江苏省南京市浦口区江浦街道",
            "deviceName": "微信小程序",
            "wifiName": "NJAU",
            "wifiMac": "58:ae:a8:32:59:90"
        }
        headers.update({
            "sign": get_sign(data),
            "timestamp": str(int(time.time() * 1000)),
            "authPerm": "PUNCHCLOCKFUN",
            "appNo": "__UNI__89A1A02",
        })
        response = requests.post("https://api.hikiot.com/api-attendance/mobile-clock/v1/normal", headers=headers, json=data).json()
        logging.info(response)
        if response['code'] == 0:
            logging.info(f"打卡成功: {response['msg']}")
            return jsonify({'message': 'success'})
        else:
            logging.error(f"打卡失败: {response['msg']}")
            return jsonify({'message': response['msg']})
    except Exception as e:
        logging.error(f"发生错误: {e}")
        return jsonify({'message': 'token无效 请重新获取'})

@app.route('/')
def index():
    return render_template('index.html')
    
    
if __name__ == '__main__':
    app.run(debug=True, port=6010, host='127.0.0.1')