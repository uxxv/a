import os
import requests
import json
import time

# 1. 获取 Cookie
cookie = os.environ.get("JD_COOKIE")

if not cookie:
    print("❌ 错误: 未找到 JD_COOKIE 环境变量，请在 GitHub Secrets 中配置。")
    exit(1)

# 2. 配置请求
url = "https://api.m.jd.com/client.action"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
    "Content-Type": "application/x-www-form-urlencoded",
    "Cookie": cookie
}

# 3. 构建参数
body = {
    "fp": "-1",
    "shshshfp": "-1",
    "shshshfpa": "-1",
    "referUrl": "-1",
    "userAgent": "-1",
    "jda": "-1",
    "rnVersion": "3.9"
}

params = {
    "functionId": "signBeanAct",
    "body": json.dumps(body, separators=(',', ':')),
    "appid": "ld",
    "client": "apple",
    "clientVersion": "10.0.4",
    "networkType": "wifi",
    "osVersion": "14.8.1",
    "uuid": str(int(time.time() * 1000)),
    "openudid": str(int(time.time() * 1000)),
    "jsonp": "jsonp_" + str(int(time.time() * 1000)) + "_58482"
}

# 4. JSONP 解析辅助函数
def parse_jsonp(text):
    try:
        if "jsonp_" in text:
            start = text.find('(') + 1
            end = text.rfind(')')
            return json.loads(text[start:end])
        return json.loads(text)
    except:
        return None

# 5. 执行请求
try:
    print("🚀 开始执行京东签到...")
    response = requests.post(url, params=params, headers=headers, timeout=10)
    
    data = parse_jsonp(response.text)
    
    if data:
        code = str(data.get("code"))
        # code 0 表示成功，code 3 表示 Cookie 失效
        if code == "0":
            print("✅ 签到成功！")
            # 尝试打印奖励信息
            try:
                daily_award = data.get("data", {}).get("dailyAward", {})
                award_count = daily_award.get('beanAward', {}).get('beanCount', '0')
                print(f"🎉 获得奖励: {award_count} 京豆")
            except:
                print("🎉 签到成功 (具体奖励解析失败)")
                
        elif code == "3":
            print("❌ 签到失败: Cookie 已失效或缺少 pt_key (需要重新获取)")
            exit(1) # 退出代码 1 会让 GitHub Action 显示红色失败图标，方便你通过邮件收到通知
            
        else:
            # 有时候重复签到会返回其他 code，也算成功
            msg = data.get("errorMessage", "无错误信息")
            if "已签到" in str(data) or "已签到" in response.text:
                print("✅ 今天已经签到过了")
            else:
                print(f"⚠️ 签到未成功: {msg}")
                print(f"原始返回: {response.text}")
    else:
        print("❌ 无法解析服务器响应")

except Exception as e:
    print(f"❌ 请求发生错误: {e}")
    exit(1)
