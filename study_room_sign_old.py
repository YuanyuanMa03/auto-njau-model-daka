import time
import hashlib
import random
import string
import requests
from datetime import datetime

class SignUtil:
    @staticmethod
    def timestamp():
        # 获取当前的Unix时间戳（毫秒）
        return str(int(time.time() * 1000))

    @staticmethod
    def nonce(length=32):
        # 生成指定长度的随机字符串
        chars = string.ascii_letters + string.digits
        nonce_str = ''.join(random.choice(chars) for _ in range(length))
        # 在第9位插入字符 'g' 和第13位插入字符 'z'
        nonce_str = nonce_str[:8] + 'g' + nonce_str[8:]
        nonce_str = nonce_str[:12] + 'z' + nonce_str[12:]
        return nonce_str

    @staticmethod
    def sign(timestamp, nonce, token):
        # 拼接字符串并计算MD5哈希
        sign_str = timestamp + nonce + token
        md5_hash = hashlib.md5(sign_str.encode()).hexdigest()
        return md5_hash

# 模拟HTTP请求拦截器
class HttpClient:
    def __init__(self, base_url):
        self.session = requests.Session()
        self.base_url = base_url
        self.token = self.get_token()

    def get_token(self):
        # 模拟从存储中获取token（可以替换成实际获取token的方法）
        return "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyIjoie1wibmlja05hbWVcIjpcIumHkeW3neaZr1wiLFwib3BlbklkXCI6XCJvektOMTVWRFFtN1NWX0E3QlJDWnhmLU41MHI0XCJ9In0.rJIYTwGjDuJ-DuxtzTiZzLqZW36pJduOuqTRAKh88rI"  # 替换成实际的token值

    def request(self, method, url, **kwargs):
        # 获取签名相关参数
        timestamp = SignUtil.timestamp()
        nonce = SignUtil.nonce()
        token = self.token
        
        # 设置HTTP头部信息
        headers = kwargs.get("headers", {})
        headers["Accept-Token"] = token
        headers["t"] = timestamp
        headers["n"] = nonce
        headers["s"] = SignUtil.sign(timestamp, nonce, token)
        headers["Content-Type"] = "application/json"
        headers["User-Agent"] = "Mozilla/5.0 (iPhone; CPU iPhone OS 18_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.52(0x18003426) NetType/WIFI Language/zh_CN"
        headers["Referer"] = "https://servicewechat.com/wx7303abb12bf8f14a/18/page-frame.html"
        
        kwargs["headers"] = headers
        
        # 发送请求
        response = self.session.request(method, self.base_url + url, **kwargs)
        return response

def sign():
    print("开始签到")
    try:
        json={
            "mainId": "1848715885847195648",
            "isMakeCard": 0,
            "signDate": datetime.now().strftime("%Y-%m-%d"),
            "signTime": datetime.now().strftime("%H:%M"),
            "addressId": "1848715885863972864",
            "latitude": "32.012006",
            "longitude": "118.636892"
        }
        print(json)
        client = HttpClient(base_url="https://minips.ydxz123.cn")
        response = client.request("POST", "/sign/record/submit", json=json)
        if response.json().get("code") == "00000":
            print("签到成功")
        else:
            print(f"签到失败，错误原因：{response.json().get('msg')}")
    except Exception as e:
        print(f"签到失败，出现异常：{str(e)}")
    

# 使用示例
if __name__ == "__main__":
    delay = random.randint(3, 10) * 60
    print(f"随机延迟{delay}秒")
    time.sleep(delay)
    sign()