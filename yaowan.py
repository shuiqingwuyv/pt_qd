import requests
import json

# 自定义变量
username = 'xxxx'  # 用户名
password = 'xxxx'  # 密码

# 自定义 HTTP 代理设置
proxies = {
    'http': 'http://10.0.0.170:20171',
    'https': 'http://10.0.0.170:20171',
}

print(f"\n当前使用的代理设置: {proxies}")

# --- 第一个 GET 请求，获取 flarum_session 和 x-csrf-token ---
headers_get = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,application/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'zh-CN,zh;q=0.9',
    'cache-control': 'no-cache',
    'pragma': 'no-cache',
    'priority': 'u=0, i',
    'referer': 'https://invites.fun/',
    'sec-ch-ua': '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
}

# 发起第一个 GET 请求 (带代理)
response_get = requests.get('https://invites.fun/', headers=headers_get, proxies=proxies)

# 获取 cookie 中的 flarum_session
flarum_session_get = response_get.cookies.get('flarum_session')

# 从响应头中提取 x-csrf-token
csrf_token_get = response_get.headers.get('x-csrf-token')

print("\n获取登录cookie - GET 请求响应标头:")
for header, value in response_get.headers.items():
    print(f"{header}: {value}")

if flarum_session_get:
    print(f"\n获取到 flarum_session (GET): {flarum_session_get}")
else:
    print("flarum_session cookie not found (GET).")

if csrf_token_get:
    print(f"x-csrf-token (GET): {csrf_token_get}")
else:
    print("x-csrf-token header not found (GET).")

# --- 第二个 POST 请求，执行登录操作并获取新的 cookies 和 UId ---
cookies_login = {
    'flarum_session': flarum_session_get,
}

headers_login = {
    'accept': '*/*',
    'accept-language': 'zh-CN,zh;q=0.9',
    'cache-control': 'no-cache',
    'content-type': 'application/json; charset=UTF-8',
    'origin': 'https://invites.fun',
    'pragma': 'no-cache',
    'priority': 'u=1, i',
    'referer': 'https://invites.fun/',
    'sec-ch-ua': '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
    'x-csrf-token': csrf_token_get,
}

json_data_login = {
    'identification': username,
    'password': password,
    'remember': True,
}

# 发起第二个 POST 请求 (带代理)
post_response_login = requests.post('https://invites.fun/login', cookies=cookies_login, headers=headers_login, json=json_data_login, proxies=proxies)

print("\n登录 POST 请求响应标头:")
for header, value in post_response_login.headers.items():
    print(f"{header}: {value}")

# 从 POST 响应中提取 flarum_remember, flarum_session
flarum_remember_post = post_response_login.cookies.get('flarum_remember')
flarum_session_post = post_response_login.cookies.get('flarum_session')

# 从 POST 响应头中获取 X-CSRF-Token
csrf_token_post = post_response_login.headers.get('X-CSRF-Token')
if not csrf_token_post:
    csrf_token_post = csrf_token_get

# 提取 UId
user_id = None
try:
    login_response_json = post_response_login.json()
    print("\n登录 POST 请求 JSON 响应内容:")
    print(json.dumps(login_response_json, indent=2, ensure_ascii=False))

    if 'userId' in login_response_json and login_response_json['userId'] is not None:
        user_id = login_response_json['userId']

except json.JSONDecodeError:
    print("登录响应不是有效的 JSON，无法提取 UId。")
    print(f"登录响应内容: {post_response_login.text}")
except Exception as e:
    print(f"解析 UId 时发生错误: {e}")

if flarum_remember_post:
    print(f"\n提取到的 flarum_remember (POST): {flarum_remember_post}")
else:
    print("flarum_remember 未找到 (POST)。")

if flarum_session_post:
    print(f"提取到的 flarum_session (POST): {flarum_session_post}")
else:
    print("flarum_session 未找到 (POST)。")

if csrf_token_post:
    print(f"提取到的 X-CSRF-Token (POST): {csrf_token_post}")
else:
    print("X-CSRF-Token 未找到 (POST)。")

if user_id:
    print(f"提取到的 UId: {user_id}")
else:
    print("UId 未找到。")

# --- 第三个 POST 请求，执行签到操作 ---
if flarum_remember_post and flarum_session_post and csrf_token_post and user_id:
    cookies_checkin = {
        'flarum_remember': flarum_remember_post,
        'flarum_session': flarum_session_post,
    }

    headers_checkin = {
        'accept': '*/*',
        'accept-language': 'zh-CN,zh;q=0.9',
        'cache-control': 'no-cache',
        'content-type': 'application/json; charset=UTF-8',
        'origin': 'https://invites.fun',
        'pragma': 'no-cache',
        'priority': 'u=1, i',
        'referer': 'https://invites.fun/',
        'sec-ch-ua': '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
        'x-csrf-token': csrf_token_post,
        'x-http-method-override': 'PATCH',
    }

    json_data_checkin = {
        'data': {
            'type': 'users',
            'attributes': {
                'canCheckin': False,
                'totalContinuousCheckIn': 2,
            },
            'id': str(user_id),
        },
    }

    checkin_url = f'https://invites.fun/api/users/{user_id}'

    # 发起签到 POST 请求 (带代理)
    response_checkin = requests.post(checkin_url, cookies=cookies_checkin, headers=headers_checkin, json=json_data_checkin, proxies=proxies)

    # 尝试解析签到 POST 请求的 JSON 响应
    try:
        checkin_response_json = response_checkin.json()

        # 提取关键信息
        extracted_username = checkin_response_json['data']['attributes']['username']
        extracted_id = checkin_response_json['data']['id']
        extracted_new_notification_count = checkin_response_json['data']['attributes']['newNotificationCount']
        extracted_total_continuous_checkin = checkin_response_json['data']['attributes']['totalContinuousCheckIn']
        extracted_money = checkin_response_json['data']['attributes']['money']

        # 格式化输出 - 修正了f-string中的反斜杠问题
        output = (
            "✅药丸签到结果\n"
            f"✨用户名：{extracted_username}\n"
            f"📧UID：{extracted_id}\n"
            f"🌸今日奖励：{extracted_new_notification_count}\n"
            f"💰当前余额：{extracted_money}\n"
            f"📆签到天数：{extracted_total_continuous_checkin}"
        )
        #print("\n" + output)
        print(QLAPI.systemNotify({ "title": "药丸签到通知", "content": output}))

    except json.JSONDecodeError:
        print("\n签到响应不是有效的 JSON，无法提取关键内容。")
        print("签到 POST 请求响应内容:")
        print(response_checkin.text)
    except KeyError as e:
        print(f"\n签到响应中缺少关键字段 '{e}'，无法提取信息。")
        print("签到 POST 请求响应内容:")
        print(response_checkin.text)
    except Exception as e:
        print(f"\n提取签到信息时发生未知错误: {e}")
        print("签到 POST 请求响应内容:")
        print(response_checkin.text)

else:
    print("\n缺少必要的 cookie、CSRF token 或 UId，无法执行签到请求。")
