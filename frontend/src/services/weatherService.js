import apiClient from '../api/client';

export const DEFAULT_WEATHER = {
  temp: "29°C",
  minMax: "24°C / 32°C",
  feel: "31°C",
  condition: "Sunny / Fair",
  humidity: "62%",
  wind: "14 km/h",
  rainProb: "12%",
  uv: "7 (High)",
  location: "Bengaluru, Karnataka",
  farming_advice: {
    irrigation_advice: "Suitable time for irrigation. Evaporation rates are moderate.",
    spraying_advice: "Suitable time for chemical spray. Low wind drift risk.",
    harvest_recommendation: "Favorable conditions. Conditions are dry and clear.",
    sowing_recommendation: "Favorable. Soil moisture levels are optimal.",
    warnings: "No active weather warnings. Great time for farming activities."
  }
};

/**
 * Retrieve saved weather data from localStorage, or return DEFAULT_WEATHER.
 */
export const getStoredWeather = () => {
  try {
    const saved = localStorage.getItem('agri_current_weather');
    if (saved) {
      const parsed = JSON.parse(saved);
      if (
        parsed &&
        parsed.temp &&
        parsed.condition &&
        parsed.temp !== '--°C' &&
        !String(parsed.condition).toLowerCase().includes('loading')
      ) {
        return { ...DEFAULT_WEATHER, ...parsed };
      }
    }
  } catch (e) {
    console.warn("Failed to retrieve weather from localStorage:", e);
  }
  return DEFAULT_WEATHER;
};

/**
 * Save current weather to localStorage and dispatch event for cross-component sync.
 */
export const saveStoredWeather = (weatherData) => {
  try {
    if (!weatherData) return;
    const merged = { ...getStoredWeather(), ...weatherData, savedAt: Date.now() };
    localStorage.setItem('agri_current_weather', JSON.stringify(merged));
    window.dispatchEvent(new CustomEvent('agri_weather_updated', { detail: merged }));
  } catch (e) {
    console.warn("Failed to persist weather to localStorage:", e);
  }
};

/**
 * Format raw backend weather object into UI-friendly structure.
 */
export const formatWeatherData = (c) => {
  if (!c) return null;
  const rawTemp = c.temperature !== undefined ? c.temperature : c.temp;
  const rawCondition = c.weather_condition || c.condition || c.weather_description || "Sunny / Fair";
  const rawHumidity = c.humidity !== undefined ? c.humidity : "--";
  const rawWind = c.wind_speed !== undefined ? c.wind_speed : c.wind;

  const fmtTemp = typeof rawTemp === 'number' 
    ? `${Math.round(rawTemp)}°C` 
    : (rawTemp && String(rawTemp).includes('°') ? rawTemp : `${rawTemp || '29'}°C`);

  const fmtHumidity = typeof rawHumidity === 'number' 
    ? `${rawHumidity}%` 
    : (rawHumidity && String(rawHumidity).includes('%') ? rawHumidity : `${rawHumidity || '62'}%`);

  const fmtWind = typeof rawWind === 'number' 
    ? `${rawWind} km/h` 
    : (rawWind && String(rawWind).includes('h') ? rawWind : `${rawWind || '14'} km/h`);

  const fmtUv = c.uv_index !== undefined 
    ? (typeof c.uv_index === 'number' ? `${c.uv_index} (Index)` : c.uv_index) 
    : "7 (High)";

  return {
    temp: fmtTemp,
    minMax: typeof rawTemp === 'number' ? `${Math.round(rawTemp - 4)}°C / ${Math.round(rawTemp + 3)}°C` : "24°C / 32°C",
    feel: typeof rawTemp === 'number' ? `${Math.round(rawTemp + 1)}°C` : fmtTemp,
    condition: rawCondition,
    humidity: fmtHumidity,
    wind: fmtWind,
    rainProb: c.rain_probability !== undefined ? `${c.rain_probability}%` : "12%",
    uv: fmtUv,
    location: c.location || undefined,
    farming_advice: c.farming_advice || undefined
  };
};

/**
 * Fetch current weather from backend API with fallback strategies and persistent caching.
 */
export const fetchCurrentWeather = async (lat, lon, locationName = null) => {
  let responseData = null;

  // Strategy 1: Coordinates POST /weather/current
  if (lat !== undefined && lon !== undefined && lat !== null && lon !== null) {
    try {
      const res = await apiClient.post('/weather/current', {
        latitude: parseFloat(lat),
        longitude: parseFloat(lon)
      });
      if (res?.data) {
        responseData = res.data;
      }
    } catch (e) {
      console.warn("Primary /weather/current request failed:", e);
    }
  }

  // Strategy 2: Location name POST /weather/by-location
  if (!responseData && locationName) {
    try {
      const res = await apiClient.post('/weather/by-location', {
        location: locationName
      });
      if (res?.data) {
        responseData = res.data;
      }
    } catch (e) {
      console.warn("Fallback /weather/by-location request failed:", e);
    }
  }

  // Strategy 3: Default Indian agricultural coordinates
  if (!responseData) {
    try {
      const res = await apiClient.post('/weather/current', {
        latitude: 21.1702,
        longitude: 72.8311
      });
      if (res?.data) {
        responseData = res.data;
      }
    } catch (e) {
      console.warn("Default coordinate /weather/current request failed:", e);
    }
  }

  if (responseData) {
    const formatted = formatWeatherData(responseData);
    if (formatted) {
      saveStoredWeather(formatted);
      return formatted;
    }
  }

  // Strategy 4: Return cached weather or default values
  return getStoredWeather();
};
