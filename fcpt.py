import requests
import json
import unicodedata
import re
from datetime import datetime

# --- 用户可配置的变量 ---
PROXY_ADDRESS = ""  # 代理地址，例如 "http://127.0.0.1:8080"
IDENTIFICATION = "xxxx"  # 登录邮箱
PASSWORD = "xxxx"  # 登录密码


# --- 全局变量，用于存储在不同请求间传递的信息 ---
initial_x_csrf_token = None
initial_flarum_session_cookie_value = None
login_x_csrf_token = None
combined_cookies_for_next_request = None
extracted_user_id_from_login = None  # 新增变量，用于存储从登录响应中提取的 userId

# 配置代理
proxies = {}
if PROXY_ADDRESS:
    proxies = {
        "http": PROXY_ADDRESS,
        "https": PROXY_ADDRESS
    }
    print(f"使用代理: {PROXY_ADDRESS}")

# --- 第一步：获取初始 CSRF Token 和 Flarum Session Cookie ---
print("--- 第一步：获取初始 CSRF Token 和 Flarum Session Cookie ---")
initial_url = "https://pting.club/"

try:
    initial_response = requests.get(initial_url, proxies=proxies)
    initial_response.raise_for_status()

    initial_x_csrf_token = initial_response.headers.get('x-csrf-token')
    if initial_x_csrf_token:
        print(f"初始 GET 请求成功获取到 x-csrf-token: {initial_x_csrf_token}")
    else:
        print("初始 GET 请求未在响应头中找到 x-csrf-token。")

    for cookie_name, cookie_value in initial_response.cookies.items():
        if cookie_name == 'flarum_session':
            initial_flarum_session_cookie_value = f"{cookie_name}={cookie_value}"
            print(f"初始 GET 请求成功获取到 flarum_session cookie 值: {initial_flarum_session_cookie_value}")
            break
    if not initial_flarum_session_cookie_value:
        print("初始 GET 请求未在 Set-Cookie 中找到 flarum_session。")

except requests.exceptions.RequestException as e:
    print(f"初始 GET 请求失败: {e}")
    exit("无法继续，初始 GET 请求失败。")

if not initial_x_csrf_token or not initial_flarum_session_cookie_value:
    exit("无法继续，缺少初始 CSRF token 或 Flarum Session Cookie。")

print("\n--- 第二步：执行登录 POST 请求 ---")
login_url = "https://pting.club/login"

# 使用用户配置的登录凭证
login_payload = {
    "identification": IDENTIFICATION,
    "password": PASSWORD,
    "remember": True
}

login_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
    "Accept": "*/*",
    "Origin": "https://pting.club",
    "Referer": "https://pting.club/login.html",
    "X-Requested-With": "XMLHttpRequest",
    "Content-Type": "application/json",
    "x-csrf-token": initial_x_csrf_token,
    "Cookie": initial_flarum_session_cookie_value
}

try:
    login_response = requests.post(login_url, headers=login_headers, data=json.dumps(login_payload), proxies=proxies)
    login_response.raise_for_status()
    print("\n登录响应内容:")
    print(login_response.text)

    # --- 从登录响应中提取 userId ---
    try:
        login_response_json = login_response.json()
        if "userId" in login_response_json:
            extracted_user_id_from_login = str(login_response_json["userId"]) # 转换为字符串，以便后续拼接URL
            print(f"从登录响应中成功提取到 userId: {extracted_user_id_from_login}")
        else:
            print("登录响应中未找到 'userId' 字段。")
    except json.JSONDecodeError:
        print("登录响应不是有效的 JSON 格式，无法提取 userId。")
    # --- 提取结束 ---

    print(f"登录请求成功，状态码: {login_response.status_code}")

    login_x_csrf_token = login_response.headers.get('x-csrf-token')
    if login_x_csrf_token:
        print(f"登录成功后获取到新的 x-csrf-token: {login_x_csrf_token}")
    else:
        print("登录成功响应头中未找到新的 x-csrf-token。")

    flarum_remember_cookie_value = None
    new_flarum_session_cookie_value = None

    for cookie_name, cookie_value in login_response.cookies.items():
        if cookie_name == 'flarum_remember':
            flarum_remember_cookie_value = f"{cookie_name}={cookie_value}"
            print(f"登录成功后获取到 flarum_remember: {flarum_remember_cookie_value}")
        elif cookie_name == 'flarum_session':
            if cookie_value != initial_flarum_session_cookie_value.split('=')[1]:
                new_flarum_session_cookie_value = f"{cookie_name}={cookie_value}"
                print(f"登录成功后获取到新的 flarum_session: {new_flarum_session_cookie_value}")
            else:
                print("登录后 flarum_session cookie 值未改变。")


    if flarum_remember_cookie_value and new_flarum_session_cookie_value:
        combined_cookies_for_next_request = f"{flarum_remember_cookie_value}; {new_flarum_session_cookie_value}"
        print(f"合并后的 Cookies 用于后续请求: {combined_cookies_for_next_request}")
    elif flarum_remember_cookie_value:
        combined_cookies_for_next_request = flarum_remember_cookie_value
        print(f"只有 flarum_remember 用于后续请求: {combined_cookies_for_next_request}")
    elif new_flarum_session_cookie_value:
        combined_cookies_for_next_request = new_flarum_session_cookie_value
        print(f"只有新的 flarum_session 用于后续请求: {combined_cookies_for_next_request}")
    else:
        print("未获取到任何可用于后续请求的 cookies。")

except requests.exceptions.HTTPError as errh:
    print(f"登录 Http Error: {errh}")
    if errh.response is not None:
        try:
            print(f"登录错误响应内容: {errh.response.json()}")
        except json.JSONDecodeError:
            print(f"登录错误响应内容(非JSON): {errh.response.text}")
    exit("无法继续，登录请求失败。")
except requests.exceptions.RequestException as err:
    print(f"登录请求失败: {err}")
    exit("无法继续，登录请求失败。")

if not login_x_csrf_token or not combined_cookies_for_next_request or not extracted_user_id_from_login:
    exit("无法继续，缺少登录后 CSRF token、合并的 Cookies 或提取的 userId。")

print("\n--- 第三步：执行修改用户数据 (PATCH 模拟) 请求 ---")
# 使用从登录响应中提取的 userId
patch_user_url = f"https://pting.club/api/users/{extracted_user_id_from_login}"

patch_payload = {
    "data": {
        "type": "users",
        "attributes": {
            "canCheckin": False,
            "totalContinuousCheckIn": 2
        },
        "id": extracted_user_id_from_login # 使用提取的 userId
    }
}

patch_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
    "Accept": "*/*",
    "Origin": "https://pting.club",
    "Referer": "https://pting.club/",
    "Content-Type": "application/json; charset=UTF-8",
    "x-csrf-token": login_x_csrf_token,
    "Cookie": combined_cookies_for_next_request,
    "X-HTTP-Method-Override": "PATCH",
}

try:
    patch_response = requests.post(patch_user_url, headers=patch_headers, data=json.dumps(patch_payload), proxies=proxies)
    patch_response.raise_for_status()

    print(f"修改用户数据请求成功，状态码: {patch_response.status_code}")
    
    response_data = patch_response.json()

    extracted_username = None
    # extracted_comment_count = None # 这个不再用于今日奖励
    # extracted_discussion_count = None # 这个不再用于签到天数
    extracted_join_time = None
    extracted_group_name_singular = None

    # 新增变量用于存储从 patch_response 中提取的值
    extracted_total_continuous_check_in = None
    extracted_money = None
    extracted_last_checkin_money = None


    if "data" in response_data and "attributes" in response_data["data"]:
        attributes = response_data["data"]["attributes"]
        extracted_username = attributes.get("username")
        # 提取新的字段
        extracted_total_continuous_check_in = attributes.get("totalContinuousCheckIn")
        extracted_money = attributes.get("money")
        extracted_last_checkin_money = attributes.get("lastCheckinMoney")

        extracted_join_time = attributes.get("joinTime")
        
    if "included" in response_data:
        for item in response_data["included"]:
            if item.get("type") == "groups" and "attributes" in item:
                extracted_group_name_singular = item["attributes"].get("nameSingular")
                if extracted_group_name_singular:
                    extracted_group_name_singular = unicodedata.normalize('NFKC', extracted_group_name_singular)

    print("\n" + "="*30)
    print("✅蜂巢签到结果")
    print(f"✨用户名：{extracted_username if extracted_username else 'N/A'}")
    print(f"📧UID：{extracted_user_id_from_login if extracted_user_id_from_login else 'N/A'}") # 使用提取的UID
    print(f"🌸今日奖励：{extracted_last_checkin_money if extracted_last_checkin_money is not None else 'N/A'}")
    print(f"💰当前余额：{extracted_money if extracted_money is not None else 'N/A'}")
    print(f"📆签到天数：{extracted_total_continuous_check_in if extracted_total_continuous_check_in is not None else 'N/A'}")
    
    output = (
    "✅药丸签到结果\n"
    f"✨用户名：{extracted_username if extracted_username else 'N/A'}\n"
    f"📧UID：{extracted_user_id_from_login if extracted_user_id_from_login else 'N/A'}\n"
    f"🌸今日奖励：{extracted_last_checkin_money if extracted_last_checkin_money is not None else 'N/A'}\n"
    f"💰当前余额：{extracted_money if extracted_money is not None else 'N/A'}\n"
    f"📆签到天数：{extracted_total_continuous_check_in if extracted_total_continuous_check_in is not None else 'N/A'}\n"
    )
    # 这里假设 QLAPI 是一个外部定义的类或对象，为了让代码能够运行，我注释掉了这行
    print(QLAPI.systemNotify({ "title": "蜂巢签到", "content": output}))
    
    formatted_join_time = "N/A"
    if extracted_join_time:
        try:
            dt_object = datetime.fromisoformat(extracted_join_time.replace('Z', '+00:00'))
            formatted_join_time = dt_object.strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            formatted_join_time = extracted_join_time

    print(f"🕐签到时间：{formatted_join_time}")
    
    if extracted_group_name_singular:
        print(f"👥用户组名称 (nameSingular)：{extracted_group_name_singular}")
    print("="*30 + "\n")

except requests.exceptions.HTTPError as errh:
    print(f"修改用户数据 Http Error: {errh}")
    if errh.response is not None:
        try:
            print(f"修改用户数据错误响应内容: {errh.response.json()}")
        except json.JSONDecodeError:
            print(f"修改用户数据错误响应内容(非JSON): {errh.response.text}")
except requests.exceptions.ConnectionError as errc:
    print(f"修改用户数据 Error Connecting: {errc}")
except requests.exceptions.Timeout as errt:
    print(f"修改用户数据 Timeout Error: {errt}")
except requests.exceptions.RequestException as err:
    print(f"修改用户数据 OOps: Something Else {err}")

print("\n--- 所有请求完成 ---")
