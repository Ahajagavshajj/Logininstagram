from flask import Flask, request, jsonify
import requests
from datetime import datetime

app = Flask(__name__)

def IsExists(user, password):
    time = int(datetime.now().timestamp())  # تحديث الوقت لكل محاولة
    url = "https://www.instagram.com/api/v1/web/accounts/login/ajax/"
    
    payload = {
        'enc_password': f'#PWD_INSTAGRAM_BROWSER:0:{time}:{password}',
        'optIntoOneTap': 'false',
        'queryParams': {},
        'username': user
    }

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
    }

    # أول طلب للحصول على الكوكيز
    response = requests.post(url, headers=headers, data=payload)
    
    if 'csrftoken' not in response.cookies:
        return {"status": "error", "message": "Unable to get CSRF token"}
    
    csrf = response.cookies["csrftoken"]
    mid = response.cookies.get("mid", "")
    ig_did = response.cookies.get("ig_did", "")
    ig_nrcb = response.cookies.get("ig_nrcb", "")
    
    headers.update({
        'X-CSRFToken': csrf,
        'Cookie': f"csrftoken={csrf}; mid={mid}; ig_did={ig_did}; ig_nrcb={ig_nrcb};"
    })

    # المحاولة الثانية لتسجيل الدخول
    response = requests.post(url, headers=headers, data=payload)
    return response.json()


@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user = data.get("username")
    password = data.get("password")

    if not user or not password:
        return jsonify({"status": "error", "message": "username and password are required"}), 400

    result = IsExists(user, password)

    if result.get("status") == "ok" and result.get("authenticated") is True:
        return jsonify({"status": "success", "message": "User and password matching"})
    else:
        return jsonify({"status": "fail", "response": result})

if __name__ == '__main__':
    app.run(debug=True)
