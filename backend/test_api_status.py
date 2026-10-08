import os
import json
import urllib.request
import urllib.error
import ssl

def check_gemini():
    print("--- 1. Testing Google Gemini API ---")
    key = os.getenv("GEMINI_API_KEY", "AIzaSyA0aytMbMG2sRM8qoV5L7Fal_nG_0d5jV4")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={key}"
    payload = {
        "contents": [{"parts": [{"text": "Hello, respond with 'Gemini API is working!'"}]}]
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
    try:
        ctx = ssl._create_unverified_context()
        with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
            res = json.loads(resp.read().decode("utf-8"))
            candidates = res.get("candidates", [])
            if candidates:
                text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                print(f"[OK] Gemini API Success: {text.strip()}")
                return True
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8")
        print(f"[HTTP Error] Gemini status {e.code}: {err_msg[:200]}")
    except Exception as e:
        print(f"[Error] Gemini API test failed: {e}")
    return False

def check_weather():
    print("\n--- 2. Testing WeatherAPI ---")
    key = "eb4c814705864c7aa2f91049260508"
    url = f"https://api.weatherapi.com/v1/current.json?key={key}&q=Pune"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        ctx = ssl._create_unverified_context()
        with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            temp = data.get("current", {}).get("temp_c")
            cond = data.get("current", {}).get("condition", {}).get("text")
            print(f"[OK] WeatherAPI Success for Pune: {temp}°C, Condition: {cond}")
            return True
    except Exception as e:
        print(f"[Error] WeatherAPI failed: {e}")
    return False

def check_open_meteo():
    print("\n--- 3. Testing Open-Meteo Free Satellite API ---")
    url = "https://api.open-meteo.com/v1/forecast?latitude=18.5204&longitude=73.8567&current=temperature_2m,relative_humidity_2m"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        ctx = ssl._create_unverified_context()
        with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            curr = data.get("current", {})
            print(f"[OK] Open-Meteo Success: {curr.get('temperature_2m')}°C, Humidity: {curr.get('relative_humidity_2m')}%")
            return True
    except Exception as e:
        print(f"[Error] Open-Meteo failed: {e}")
    return False

if __name__ == "__main__":
    check_gemini()
    check_weather()
    check_open_meteo()
