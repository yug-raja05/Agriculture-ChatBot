import os
import logging
import urllib.request
import urllib.parse
import json
import ssl
import time
import datetime
import math
from typing import Dict, Any, List, Optional, Union
from app.core.config import settings
from app.core.caching import execute_with_retry_and_cache

logger = logging.getLogger(__name__)

# --- Compass Helper ---
def map_degrees_to_compass(degrees: Any) -> str:
    if degrees is None or str(degrees).strip().lower() in ["nan", "null", "none", ""]:
        return "Not Available"
    try:
        deg = float(degrees)
        if math.isnan(deg):
            return "Not Available"
        compass_brackets = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
        idx = int((deg + 11.25) / 22.5) % 16
        return compass_brackets[idx]
    except Exception:
        return "Not Available"

# --- NaN/Null Cleaner Helper ---
def sanitize_val(val: Any, default: Any = "Not Available") -> Any:
    if val is None or str(val).strip().lower() in ["nan", "null", "none", ""]:
        return default
    try:
        # Check float NaN
        fval = float(val)
        if math.isnan(fval):
            return default
        return fval
    except Exception:
        return str(val)

# --- WMO Weather Code Mapper ---
def map_wmo_code_to_condition(code: Any) -> tuple[str, str]:
    try:
        c = int(sanitize_val(code, 0))
    except Exception:
        c = 0
    wmo_map = {
        0: ("Clear", "Clear sky conditions"),
        1: ("Clear", "Mainly clear sky"),
        2: ("Cloudy", "Partly cloudy sky"),
        3: ("Cloudy", "Overcast sky"),
        45: ("Foggy", "Fog and low visibility"),
        48: ("Foggy", "Depositing rime fog"),
        51: ("Drizzle", "Light intensity drizzle"),
        53: ("Drizzle", "Moderate intensity drizzle"),
        55: ("Drizzle", "Dense intensity drizzle"),
        61: ("Rain", "Slight rain showers"),
        63: ("Rain", "Moderate rain showers"),
        65: ("Rain", "Heavy rainfall"),
        80: ("Rain", "Slight rain showers"),
        81: ("Rain", "Moderate rain showers"),
        82: ("Rain", "Violent rain storms"),
        95: ("Thunderstorm", "Thunderstorms and lightning active"),
    }
    return wmo_map.get(c, ("Partly Cloudy", "Partly cloudy conditions"))

# --- Agricultural Advisory Helper ---
def generate_agricultural_advisory(
    temp: Any,
    humidity: Any,
    wind_speed: Any,
    rain_prob: Any,
    uv_index: Any
) -> Dict[str, str]:
    # Clean floats
    t = float(sanitize_val(temp, 28.0))
    h = float(sanitize_val(humidity, 60.0))
    w = float(sanitize_val(wind_speed, 10.0))
    rp = float(sanitize_val(rain_prob, 0.0))
    uv = float(sanitize_val(uv_index, 5.0))
    
    # Irrigation
    irrigation_advice = "Suitable time for irrigation. Evaporation rates are moderate."
    if t > 35.0:
        irrigation_advice = "Irrigate crops during early morning or evening to minimize water evaporation."
    elif rp > 70.0:
        irrigation_advice = "Postpone irrigation. High probability of natural precipitation."
        
    # Spraying
    spraying_advice = "Suitable time for chemical spray."
    if w > 15.0:
        spraying_advice = "Postpone chemical pesticide spraying due to high wind drift risks."
    elif rp > 60.0:
        spraying_advice = "Postpone pesticide sprays. Upcoming rainfall can wash away active ingredients."
        
    # Harvest
    harvest_recommendation = "Favorable. Conditions are dry and clear."
    if rp > 50.0:
        harvest_recommendation = "Caution: Upcoming rain forecast. Delay harvesting to prevent crop rot or mold."
        
    # Sowing
    sowing_recommendation = "Favorable. Soil moisture levels are optimal."
    if t < 10.0:
        sowing_recommendation = "Caution: Low temperature. Warm soil crops may experience delayed germination."

    # Warnings
    warnings = []
    if t > 40.0:
        warnings.append("Heat Warning: Extreme heat. Implement shading and micro-sprinklers.")
    if t < 4.0:
        warnings.append("Frost Warning: Frost hazard. Use light irrigation or mulching to insulate crop roots.")
    if rp > 80.0:
        warnings.append("Heavy Rainfall Warning: Avoid waterlogging. Clear drainage channels.")
    if w > 25.0:
        warnings.append("Wind Warning: Strong winds. Support tall crops (like banana or sugarcane) to prevent lodging.")

    return {
        "suitable_irrigation_time": "Early Morning / Late Evening" if t > 35.0 else "Anytime",
        "irrigation_advice": irrigation_advice,
        "suitable_spraying_time": "Early Morning" if w > 15.0 or rp > 60.0 else "Anytime",
        "spraying_advice": spraying_advice,
        "harvest_recommendation": harvest_recommendation,
        "sowing_recommendation": sowing_recommendation,
        "warnings": " | ".join(warnings) if warnings else "No active weather warnings. Great time for farming activities."
    }

class WeatherProvider:
    """
    Abstract Weather Provider Interface.
    """
    def fetch_current(self, lat: float, lon: float) -> Dict[str, Any]:
        raise NotImplementedError()

    def fetch_forecast(self, lat: float, lon: float) -> Dict[str, Any]:
        raise NotImplementedError()

class OpenWeatherProvider(WeatherProvider):
    def fetch_current(self, lat: float, lon: float) -> Dict[str, Any]:
        api_key = settings.WEATHER_API_KEY
        if not api_key or "placeholder" in api_key or api_key == "":
            raise ValueError("WEATHER_API_KEY is not configured or is a placeholder.")
            
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"
        logger.info(f"[OpenWeather API Request] GET {url}")
        
        ctx = ssl._create_unverified_context()
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        
        with urllib.request.urlopen(req, context=ctx, timeout=5) as response:
            data = json.loads(response.read().decode('utf-8'))
            
        logger.info(f"[OpenWeather API Response] {json.dumps(data)[:300]}...")
        
        main = data.get("main", {})
        wind = data.get("wind", {})
        weather_list = data.get("weather", [])
        weather_obj = weather_list[0] if weather_list else {}
        
        temp = sanitize_val(main.get("temp"))
        feels_like = sanitize_val(main.get("feels_like"))
        humidity = sanitize_val(main.get("humidity"))
        wind_speed = sanitize_val(wind.get("speed"))
        wind_deg = wind.get("deg")
        pressure = sanitize_val(main.get("pressure"))
        visibility = sanitize_val(data.get("visibility"))
        if isinstance(visibility, (int, float)):
            visibility = visibility / 1000.0  # meters to km
            
        sys = data.get("sys", {})
        sunrise = sys.get("sunrise")
        sunset = sys.get("sunset")
        
        def format_epoch(epoch: Any) -> str:
            if not epoch:
                return "Not Available"
            return datetime.datetime.fromtimestamp(epoch).strftime('%I:%M %p')

        # Detect rain probability for current weather if category matches
        cond = weather_obj.get("main", "Clear")
        rain_prob = 0.0
        if cond.lower() in ["rain", "thunderstorm", "drizzle"]:
            rain_prob = 100.0

        return {
            "latitude": lat,
            "longitude": lon,
            "temperature": temp,
            "feels_like": feels_like,
            "humidity": humidity,
            "wind_speed": wind_speed,
            "wind_direction": map_degrees_to_compass(wind_deg),
            "pressure": pressure,
            "visibility": visibility,
            "rain_probability": rain_prob,
            "uv_index": 5.0,  # Default fallback index
            "sunrise": format_epoch(sunrise),
            "sunset": format_epoch(sunset),
            "weather_condition": cond,
            "weather_description": weather_obj.get("description", "Clear sky").title(),
            "last_updated": datetime.datetime.now().strftime('%Y-%m-%d %I:%M %p'),
            "provider": "OpenWeather"
        }

    def fetch_forecast(self, lat: float, lon: float) -> Dict[str, Any]:
        api_key = settings.WEATHER_API_KEY
        if not api_key or "placeholder" in api_key or api_key == "":
            raise ValueError("WEATHER_API_KEY is not configured or is a placeholder.")
            
        url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={api_key}&units=metric"
        logger.info(f"[OpenWeather API Request] GET {url}")
        
        ctx = ssl._create_unverified_context()
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, context=ctx, timeout=5) as response:
            data = json.loads(response.read().decode('utf-8'))
            
        forecast_list = data.get("list", [])
        days_data = []
        today_str = datetime.date.today().strftime('%Y-%m-%d')
        seen_days = set()
        
        for item in forecast_list:
            dt_txt = item.get("dt_txt", "")
            if not dt_txt:
                continue
            day_str = dt_txt.split(" ")[0]
            if day_str == today_str or day_str in seen_days:
                continue
            seen_days.add(day_str)
            
            day_name = datetime.datetime.strptime(day_str, '%Y-%m-%d').strftime('%a')
            main = item.get("main", {})
            temp = sanitize_val(main.get("temp"))
            rain_prob = round(item.get("pop", 0) * 100, 1)
            
            days_data.append({
                "day": day_name,
                "temp": temp,
                "rain_prob": rain_prob
            })
            if len(days_data) >= 3:
                break
        
        if not days_data:
            days_data = [{"day": "Tomorrow", "temp": 32.0, "rain_prob": 20.0}]
        return {"forecast_days": days_data, "provider": "OpenWeather"}

class WeatherAPIProvider(WeatherProvider):
    def fetch_current(self, lat: float, lon: float) -> Dict[str, Any]:
        api_key = settings.WEATHER_API_KEY
        if not api_key or "placeholder" in api_key or api_key == "":
            raise ValueError("WEATHER_API_KEY is not configured or is a placeholder.")
            
        # Using forecast endpoint to fetch current + daily astro parameters in single call
        url = f"https://api.weatherapi.com/v1/forecast.json?key={api_key}&q={lat},{lon}&days=1"
        logger.info(f"[WeatherAPI Request] GET {url}")
        
        ctx = ssl._create_unverified_context()
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, context=ctx, timeout=5) as response:
            data = json.loads(response.read().decode('utf-8'))
            
        logger.info(f"[WeatherAPI Response] {json.dumps(data)[:300]}...")
        
        curr = data.get("current", {})
        cond_obj = curr.get("condition", {})
        forecastday = data.get("forecast", {}).get("forecastday", [])
        astro = forecastday[0].get("astro", {}) if forecastday else {}
        day_obj = forecastday[0].get("day", {}) if forecastday else {}
        
        temp = sanitize_val(curr.get("temp_c"))
        feels_like = sanitize_val(curr.get("feelslike_c"))
        humidity = sanitize_val(curr.get("humidity"))
        wind_speed = sanitize_val(curr.get("wind_kph"))
        wind_deg = curr.get("wind_degree")
        pressure = sanitize_val(curr.get("pressure_mb"))
        visibility = sanitize_val(curr.get("vis_km"))
        uv = sanitize_val(curr.get("uv"))
        
        rain_prob = sanitize_val(day_obj.get("daily_chance_of_rain"), 0.0)
        sunrise = sanitize_val(astro.get("sunrise"))
        sunset = sanitize_val(astro.get("sunset"))
        
        return {
            "latitude": lat,
            "longitude": lon,
            "temperature": temp,
            "feels_like": feels_like,
            "humidity": humidity,
            "wind_speed": wind_speed,
            "wind_direction": map_degrees_to_compass(wind_deg),
            "pressure": pressure,
            "visibility": visibility,
            "rain_probability": rain_prob,
            "uv_index": uv,
            "sunrise": sunrise,
            "sunset": sunset,
            "weather_condition": cond_obj.get("text", "Clear"),
            "weather_description": cond_obj.get("text", "Clear sky").title(),
            "last_updated": curr.get("last_updated", datetime.datetime.now().strftime('%Y-%m-%d %I:%M %p')),
            "provider": "WeatherAPI"
        }

    def fetch_forecast(self, lat: float, lon: float) -> Dict[str, Any]:
        api_key = settings.WEATHER_API_KEY
        if not api_key or "placeholder" in api_key or api_key == "":
            raise ValueError("WEATHER_API_KEY is not configured or is a placeholder.")
            
        url = f"https://api.weatherapi.com/v1/forecast.json?key={api_key}&q={lat},{lon}&days=4"
        logger.info(f"[WeatherAPI Request] GET {url}")
        
        ctx = ssl._create_unverified_context()
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, context=ctx, timeout=5) as response:
            data = json.loads(response.read().decode('utf-8'))
            
        forecastday = data.get("forecast", {}).get("forecastday", [])
        days_data = []
        today_str = datetime.date.today().strftime('%Y-%m-%d')
        
        for item in forecastday:
            date_str = item.get("date", "")
            if date_str == today_str:
                continue
            day_name = datetime.datetime.strptime(date_str, '%Y-%m-%d').strftime('%a')
            day_info = item.get("day", {})
            temp = sanitize_val(day_info.get("avgtemp_c"))
            rain_prob = sanitize_val(day_info.get("daily_chance_of_rain"), 0.0)
            
            days_data.append({
                "day": day_name,
                "temp": temp,
                "rain_prob": rain_prob
            })
            if len(days_data) >= 3:
                break
                
        if not days_data:
            days_data = [{"day": "Tomorrow", "temp": 32.0, "rain_prob": 10.0}]
        return {"forecast_days": days_data, "provider": "WeatherAPI"}

class OpenMeteoProvider(WeatherProvider):
    def fetch_current(self, lat: float, lon: float) -> Dict[str, Any]:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,apparent_temperature,wind_speed_10m,wind_direction_10m,pressure_msl,visibility,weather_code&daily=sunrise,sunset,uv_index_max,precipitation_probability_max&timezone=auto"
        logger.info(f"[Open-Meteo Request] GET {url}")
        
        ctx = ssl._create_unverified_context()
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, context=ctx, timeout=5) as response:
            data = json.loads(response.read().decode('utf-8'))
            
        logger.info(f"[Open-Meteo Response] {json.dumps(data)[:300]}...")
        
        current = data.get("current", {})
        daily = data.get("daily", {})
        
        temp = sanitize_val(current.get("temperature_2m"))
        feels_like = sanitize_val(current.get("apparent_temperature"))
        humidity = sanitize_val(current.get("relative_humidity_2m"))
        wind_speed = sanitize_val(current.get("wind_speed_10m"))
        wind_deg = current.get("wind_direction_10m")
        pressure = sanitize_val(current.get("pressure_msl"))
        visibility = current.get("visibility")
        if isinstance(visibility, (int, float)):
            visibility = visibility / 1000.0 # meters to km
        visibility = sanitize_val(visibility)
        
        uv_list = daily.get("uv_index_max", [])
        uv = sanitize_val(uv_list[0] if uv_list else None, 5.0)
        
        rain_list = daily.get("precipitation_probability_max", [])
        rain_prob = sanitize_val(rain_list[0] if rain_list else None, 0.0)
        
        code = current.get("weather_code", 0)
        condition, desc = map_wmo_code_to_condition(code)
        
        sunrise_list = daily.get("sunrise", [])
        sunset_list = daily.get("sunset", [])
        
        def format_time_str(iso_str: str) -> str:
            try:
                dt = datetime.datetime.fromisoformat(iso_str)
                return dt.strftime('%I:%M %p')
            except Exception:
                return "Not Available"

        sunrise_str = format_time_str(sunrise_list[0]) if sunrise_list else "Not Available"
        sunset_str = format_time_str(sunset_list[0]) if sunset_list else "Not Available"
        
        return {
            "latitude": lat,
            "longitude": lon,
            "temperature": temp,
            "feels_like": feels_like,
            "humidity": humidity,
            "wind_speed": wind_speed,
            "wind_direction": map_degrees_to_compass(wind_deg),
            "pressure": pressure,
            "visibility": visibility,
            "rain_probability": rain_prob,
            "uv_index": uv,
            "sunrise": sunrise_str,
            "sunset": sunset_str,
            "weather_condition": condition,
            "weather_description": desc,
            "last_updated": datetime.datetime.now().strftime('%Y-%m-%d %I:%M %p'),
            "provider": "OpenMeteo"
        }

    def fetch_forecast(self, lat: float, lon: float) -> Dict[str, Any]:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=temperature_2m_max,precipitation_probability_max&timezone=auto"
        logger.info(f"[Open-Meteo Request] GET {url}")
        
        ctx = ssl._create_unverified_context()
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, context=ctx, timeout=5) as response:
            data = json.loads(response.read().decode('utf-8'))
            
        daily = data.get("daily", {})
        times = daily.get("time", [])
        temps = daily.get("temperature_2m_max", [])
        probs = daily.get("precipitation_probability_max", [])
        
        days_data = []
        today_str = datetime.date.today().strftime('%Y-%m-%d')
        
        for i in range(len(times)):
            date_str = times[i]
            if date_str == today_str:
                continue
            day_name = datetime.datetime.strptime(date_str, '%Y-%m-%d').strftime('%a')
            temp = sanitize_val(temps[i] if i < len(temps) else None)
            rain_prob = sanitize_val(probs[i] if i < len(probs) else None, 0.0)
            
            days_data.append({
                "day": day_name,
                "temp": temp,
                "rain_prob": rain_prob
            })
            if len(days_data) >= 3:
                break
                
        if not days_data:
            days_data = [{"day": "Tomorrow", "temp": 30.0, "rain_prob": 10.0}]
        return {"forecast_days": days_data, "provider": "OpenMeteo"}

class WeatherProviderRegistry:
    def __init__(self):
        self._providers = {
            "openweather": OpenWeatherProvider(),
            "weatherapi": WeatherAPIProvider(),
            "open_meteo": OpenMeteoProvider()
        }

    def get_provider(self) -> WeatherProvider:
        active_name = settings.ACTIVE_WEATHER_PROVIDER
        return self._providers.get(active_name, self._providers["open_meteo"])

class WeatherService:
    """
    Unified Weather Service.
    Integrates geocoding, providers selection, automatic retries, and database caching.
    """
    def __init__(self):
        self.registry = WeatherProviderRegistry()

    async def geocode_city(self, city_name: str) -> tuple[float, float, str]:
        """
        Resolves city name to coordinates (lat, lon, resolved_name) using Open-Meteo Geocoding.
        """
        logger.info(f"[Geocoding Request] Resolving city name: '{city_name}'")
        clean_name = city_name.strip().lower()
        base_city = city_name.split(",")[0].strip()
        
        try:
            # Append ', India' to disambiguate Indian locations (prevents Goa→Genoa, etc.)
            search_query = base_city if ',' in city_name else f"{base_city}, India"
            encoded_city = urllib.parse.quote(search_query)
            url = f"https://geocoding-api.open-meteo.com/v1/search?name={encoded_city}&count=5"
            ctx = ssl._create_unverified_context()
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            
            t0 = time.time()
            with urllib.request.urlopen(req, context=ctx, timeout=5) as response:
                data = json.loads(response.read().decode('utf-8'))
            logger.info(f"[Geocoding Response] Fetched in {time.time() - t0:.3f}s")
            
            results = data.get("results", [])
            if results:
                # Prefer Indian results when multiple matches exist
                india_results = [r for r in results if r.get("country_code", "").upper() == "IN" or r.get("country", "").lower() == "india"]
                res = india_results[0] if india_results else results[0]
                lat = float(res["latitude"])
                lon = float(res["longitude"])
                name = res["name"]
                admin = res.get("admin1", "")
                display = f"{name}, {admin}" if admin and admin.lower() != name.lower() else name
                return lat, lon, display
        except Exception as e:
            logger.warning(f"Free geocoding search failed: {e}. Checking offline fallback cache mappings.")

        # Comprehensive Indian States & Agricultural Hubs Geocoding Catalog
        fallbacks = {
            # States & Regional Capitals
            "maharashtra": (19.7515, 75.7139, "Maharashtra"),
            "gujarat": (22.2587, 71.1924, "Gujarat"),
            "punjab": (31.1471, 75.3412, "Punjab"),
            "haryana": (29.0588, 76.0856, "Haryana"),
            "rajasthan": (27.0238, 74.2179, "Rajasthan"),
            "madhya pradesh": (22.9734, 78.6569, "Madhya Pradesh"),
            "uttar pradesh": (26.8467, 80.9462, "Uttar Pradesh"),
            "karnataka": (15.3173, 75.7139, "Karnataka"),
            "tamil nadu": (11.1271, 78.6569, "Tamil Nadu"),
            "telangana": (18.1124, 79.0193, "Telangana"),
            "andhra pradesh": (15.9129, 79.7400, "Andhra Pradesh"),
            "bihar": (25.0961, 85.3131, "Bihar"),
            "west bengal": (22.9868, 87.8550, "West Bengal"),
            "odisha": (20.9517, 85.0985, "Odisha"),
            "kerala": (10.8505, 76.2711, "Kerala"),
            "assam": (26.2006, 92.9376, "Assam"),
            "goa": (15.4909, 73.8278, "Goa"),
            "nagaland": (25.6751, 94.1086, "Nagaland"),
            "meghalaya": (25.5788, 91.8933, "Meghalaya"),
            "manipur": (24.6637, 93.9063, "Manipur"),
            "mizoram": (23.1645, 92.9376, "Mizoram"),
            "tripura": (23.9408, 91.9882, "Tripura"),
            "sikkim": (27.5330, 88.5122, "Sikkim"),
            "arunachal pradesh": (28.2180, 94.7278, "Arunachal Pradesh"),
            "jharkhand": (23.6102, 85.2799, "Jharkhand"),
            "chhattisgarh": (21.2787, 81.8661, "Chhattisgarh"),
            "uttarakhand": (30.0668, 79.0193, "Uttarakhand"),
            "himachal pradesh": (31.1048, 77.1734, "Himachal Pradesh"),
            "jammu": (32.7266, 74.8570, "Jammu & Kashmir"),
            "kashmir": (34.0837, 74.7973, "Kashmir"),
            # Goa Cities
            "panaji": (15.4909, 73.8278, "Panaji, Goa"),
            "margao": (15.2832, 73.9862, "Margao, Goa"),
            "vasco": (15.3982, 73.8113, "Vasco da Gama, Goa"),
            "mapusa": (15.5937, 73.8100, "Mapusa, Goa"),
            # Northeast Cities
            "kohima": (25.6751, 94.1086, "Kohima, Nagaland"),
            "dimapur": (25.9065, 93.7272, "Dimapur, Nagaland"),
            "imphal": (24.8170, 93.9368, "Imphal, Manipur"),
            "shillong": (25.5788, 91.8933, "Shillong, Meghalaya"),
            "aizawl": (23.7271, 92.7176, "Aizawl, Mizoram"),
            "agartala": (23.8315, 91.2868, "Agartala, Tripura"),
            "gangtok": (27.3389, 88.6065, "Gangtok, Sikkim"),
            "itanagar": (27.0844, 93.6053, "Itanagar, Arunachal Pradesh"),
            # Maharashtra Agricultural Hubs
            "pune": (18.5204, 73.8567, "Pune, Maharashtra"),
            "nashik": (19.9975, 73.7898, "Nashik, Maharashtra"),
            "nagpur": (21.1458, 79.0882, "Nagpur, Maharashtra"),
            "mumbai": (19.0760, 72.8777, "Mumbai, Maharashtra"),
            "kolhapur": (16.7050, 74.2433, "Kolhapur, Maharashtra"),
            "solapur": (17.6599, 75.9064, "Solapur, Maharashtra"),
            "aurangabad": (19.8762, 75.3433, "Chhatrapati Sambhaji Nagar, Maharashtra"),
            "jalgaon": (21.0077, 75.5626, "Jalgaon, Maharashtra"),
            "akola": (20.7002, 77.0082, "Akola, Maharashtra"),
            "amravati": (20.9374, 77.7796, "Amravati, Maharashtra"),
            "satara": (17.6805, 74.0183, "Satara, Maharashtra"),
            "sangli": (16.8524, 74.5815, "Sangli, Maharashtra"),
            "ahmednagar": (19.0952, 74.7496, "Ahmednagar, Maharashtra"),
            "latur": (18.4088, 76.5604, "Latur, Maharashtra"),
            "nanded": (19.1383, 77.3210, "Nanded, Maharashtra"),
            # Gujarat Agricultural Hubs
            "ahmedabad": (23.0225, 72.5714, "Ahmedabad, Gujarat"),
            "surat": (21.1702, 72.8311, "Surat, Gujarat"),
            "rajkot": (22.3039, 70.8022, "Rajkot, Gujarat"),
            "vadodara": (22.3072, 73.1812, "Vadodara, Gujarat"),
            "anand": (22.5645, 72.9289, "Anand, Gujarat"),
            "gandhinagar": (23.2156, 72.6369, "Gandhinagar, Gujarat"),
            "bhavnagar": (21.7645, 72.1519, "Bhavnagar, Gujarat"),
            "junagadh": (21.5222, 70.4579, "Junagadh, Gujarat"),
            "jamnagar": (22.4707, 70.0577, "Jamnagar, Gujarat"),
            "mehsana": (23.5880, 72.3693, "Mehsana, Gujarat"),
            "kutch": (23.7337, 69.8597, "Kutch, Gujarat"),
            # North & Central Agricultural Hubs
            "ludhiana": (30.9010, 75.8573, "Ludhiana, Punjab"),
            "amritsar": (31.6340, 74.8723, "Amritsar, Punjab"),
            "jalandhar": (31.3260, 75.5762, "Jalandhar, Punjab"),
            "bathinda": (30.2110, 74.9455, "Bathinda, Punjab"),
            "karnal": (29.6857, 76.9905, "Karnal, Haryana"),
            "hisar": (29.1492, 75.7217, "Hisar, Haryana"),
            "delhi": (28.6139, 77.2090, "Delhi"),
            "jaipur": (26.9124, 75.7873, "Jaipur, Rajasthan"),
            "jodhpur": (26.2389, 73.0243, "Jodhpur, Rajasthan"),
            "kota": (25.2138, 75.8648, "Kota, Rajasthan"),
            "bikaner": (28.0229, 73.3119, "Bikaner, Rajasthan"),
            "indore": (22.7196, 75.8577, "Indore, Madhya Pradesh"),
            "bhopal": (23.2599, 77.4126, "Bhopal, Madhya Pradesh"),
            "gwalior": (26.2183, 78.1828, "Gwalior, Madhya Pradesh"),
            "jabalpur": (23.1815, 79.9864, "Jabalpur, Madhya Pradesh"),
            "ujjain": (23.1765, 75.7885, "Ujjain, Madhya Pradesh"),
            "lucknow": (26.8467, 80.9462, "Lucknow, Uttar Pradesh"),
            "kanpur": (26.4499, 80.3319, "Kanpur, Uttar Pradesh"),
            "varanasi": (25.3176, 82.9739, "Varanasi, Uttar Pradesh"),
            "agra": (27.1767, 78.0081, "Agra, Uttar Pradesh"),
            "patna": (25.5941, 85.1376, "Patna, Bihar"),
            # South & East Hubs
            "bangalore": (12.9716, 77.5946, "Bengaluru, Karnataka"),
            "bengaluru": (12.9716, 77.5946, "Bengaluru, Karnataka"),
            "mysore": (12.2958, 76.6394, "Mysuru, Karnataka"),
            "mysuru": (12.2958, 76.6394, "Mysuru, Karnataka"),
            "hyderabad": (17.3850, 78.4867, "Hyderabad, Telangana"),
            "chennai": (13.0827, 80.2707, "Chennai, Tamil Nadu"),
            "coimbatore": (11.0168, 76.9558, "Coimbatore, Tamil Nadu"),
            "vijayawada": (16.5062, 80.6480, "Vijayawada, Andhra Pradesh"),
            "kolkata": (22.5726, 88.3639, "Kolkata, West Bengal"),
            "bhubaneswar": (20.2961, 85.8245, "Bhubaneswar, Odisha")
        }
        base_clean = base_city.lower()
        if clean_name in fallbacks:
            return fallbacks[clean_name]
        if base_clean in fallbacks:
            return fallbacks[base_clean]
            
        for k, v in fallbacks.items():
            if k in clean_name or k in base_clean:
                return v

        # Dynamic fallback to Maharashtra / central agricultural coordinates
        return (19.7515, 75.7139, city_name.title())

    async def reverse_geocode(self, lat: float, lon: float) -> str:
        """
        Resolves coordinates to closest city name.
        """
        logger.info(f"[Reverse Geocoding] Resolving coordinates: {lat}, {lon}")
        try:
            url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json"
            ctx = ssl._create_unverified_context()
            req = urllib.request.Request(url, headers={'User-Agent': 'AgriGenius/1.0'})
            with urllib.request.urlopen(req, context=ctx, timeout=5) as response:
                data = json.loads(response.read().decode('utf-8'))
            address = data.get("address", {})
            city = address.get("city") or address.get("town") or address.get("village") or address.get("suburb") or address.get("state")
            if city:
                return city
        except Exception:
            pass

        # Static offline proximity lookup
        fallbacks = [
            (23.0225, 72.5714, "Ahmedabad"),
            (21.1702, 72.8311, "Surat"),
            (22.3039, 70.8022, "Rajkot"),
            (12.9716, 77.5946, "Bangalore"),
            (18.9750, 72.8258, "Mumbai"),
            (28.6139, 77.2090, "Delhi"),
            (30.9010, 75.8573, "Ludhiana"),
            (31.6340, 74.8723, "Amritsar")
        ]
        best_city = f"Coordinates ({round(lat, 4)}, {round(lon, 4)})"
        min_dist = 9999.0
        for c_lat, c_lon, c_name in fallbacks:
            dist = (lat - c_lat)**2 + (lon - c_lon)**2
            if dist < min_dist:
                min_dist = dist
                best_city = c_name
        if min_dist < 0.25:
            return best_city
        return f"Area Near {round(lat, 2)}N, {round(lon, 2)}E"

    async def get_current_weather(self, lat_or_city: Union[float, str], lon: Optional[float] = None) -> Dict[str, Any]:
        prov = self.registry.get_provider()
        
        # 1. Resolve coordinates and location string
        if isinstance(lat_or_city, str):
            resolved_city = lat_or_city.strip()
            lat, lon, resolved_city = await self.geocode_city(resolved_city)
        else:
            lat = lat_or_city
            if lon is None:
                raise ValueError("Missing longitude coordinate for weather fetch.")
            resolved_city = await self.reverse_geocode(lat, lon)

        # 2. Invoke fetch using cache and retry system
        async def fetch():
            def do_fetch():
                try:
                    return prov.fetch_current(lat, lon)
                except Exception as e:
                    logger.warning(f"Primary weather provider failed: {e}. Trying Open-Meteo fallback...")
                    try:
                        fallback = OpenMeteoProvider()
                        return fallback.fetch_current(lat, lon)
                    except Exception as err2:
                        logger.warning(f"Open-Meteo fallback failed: {err2}. Returning offline weather data.")
                        return {
                            "latitude": lat,
                            "longitude": lon,
                            "temperature": 26.5,
                            "feels_like": 28.0,
                            "humidity": 65,
                            "wind_speed": 10.0,
                            "wind_direction": "N",
                            "pressure": 1010,
                            "visibility": 10.0,
                            "rain_probability": 15.0,
                            "uv_index": 5.0,
                            "sunrise": "06:00 AM",
                            "sunset": "06:30 PM",
                            "weather_condition": "Clear",
                            "weather_description": "Clear Sky",
                            "last_updated": datetime.datetime.now().strftime('%Y-%m-%d %I:%M %p'),
                            "provider": "Offline Fallback"
                        }
            return await asyncio.to_thread(do_fetch)

        cache_key = {"lat": round(lat, 4), "lon": round(lon, 4), "type": "current"}
        res = await execute_with_retry_and_cache(
            cache_key_dict=cache_key,
            collection_name="weather_cache",
            api_call_func=fetch,
            cache_ttl_seconds=3600
        )
        
        # 3. Apply overrides and agricultural advice
        res["location"] = resolved_city
        res["latitude"] = lat
        res["longitude"] = lon
        res["farming_advice"] = generate_agricultural_advisory(
            res.get("temperature"),
            res.get("humidity"),
            res.get("wind_speed"),
            res.get("rain_probability"),
            res.get("uv_index")
        )
        return res

    async def get_forecast(self, lat_or_city: Union[float, str], lon: Optional[float] = None) -> Dict[str, Any]:
        prov = self.registry.get_provider()
        
        if isinstance(lat_or_city, str):
            resolved_city = lat_or_city.strip()
            lat, lon, resolved_city = await self.geocode_city(resolved_city)
        else:
            lat = lat_or_city
            if lon is None:
                raise ValueError("Missing longitude coordinate for weather forecast.")
            resolved_city = await self.reverse_geocode(lat, lon)

        async def fetch():
            def do_fetch():
                try:
                    return prov.fetch_forecast(lat, lon)
                except Exception as e:
                    logger.warning(f"Primary forecast provider failed: {e}. Trying Open-Meteo fallback...")
                    try:
                        fallback = OpenMeteoProvider()
                        return fallback.fetch_forecast(lat, lon)
                    except Exception as err2:
                        logger.warning(f"Open-Meteo forecast fallback failed: {err2}. Returning offline forecast.")
                        return {
                            "forecast_days": [
                                {"day": "Tomorrow", "temp": 27.5, "rain_prob": 30.0},
                                {"day": "Day After", "temp": 28.0, "rain_prob": 15.0},
                                {"day": "Day 3", "temp": 26.0, "rain_prob": 40.0}
                            ],
                            "provider": "Offline Fallback"
                        }
            return await asyncio.to_thread(do_fetch)

        cache_key = {"lat": round(lat, 4), "lon": round(lon, 4), "type": "forecast"}
        res = await execute_with_retry_and_cache(
            cache_key_dict=cache_key,
            collection_name="weather_cache",
            api_call_func=fetch,
            cache_ttl_seconds=14400
        )
        res["location"] = resolved_city
        res["latitude"] = lat
        res["longitude"] = lon
        return res

weather_service = WeatherService()
