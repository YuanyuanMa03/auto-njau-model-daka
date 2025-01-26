import hashlib

def get_sign(t):
    # 对字典的键进行排序
    sorted_keys = sorted(t.keys())
    
    # 构建字符串
    o = ""
    for i, key in enumerate(sorted_keys):
        value = t[key]
        o += f"{key}={value}"
        if i < len(sorted_keys) - 1:
            o += "&"
    
    # 计算 MD5
    n = hashlib.md5(o.encode('utf-8')).hexdigest()
    
    # 拼接固定字符串并再次计算 MD5
    final_sign = hashlib.md5((n.upper() + "WE1mfER7artAoJEwXKaCjw==").encode('utf-8')).hexdigest().upper()
    
    return final_sign

if __name__ == "__main__":
    # 示例用法
    example_dict = {
        "deviceSerial": "",
        "longitude": 118.63575764973959,
        "latitude": 32.00933892144097,
        "clockSite": "江苏省南京市浦口区江浦街道南京农业大学(滨江校区)",
        "address": "江苏省南京市浦口区江浦街道",
        "deviceName": "微信小程序",
        "wifiName": "NJAU",
        "wifiMac": "58:ae:a8:f7:69:e0"
    }

    sign = get_sign(example_dict)
    print(sign)
