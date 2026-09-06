import React, { createContext, useContext, useState, useEffect, useCallback, useRef } from 'react';
import apiClient from '../api/client';

const LocationContext = createContext(null);

const LS_KEY_LOCATION = 'user_location';
const LS_KEY_LAT = 'user_lat';
const LS_KEY_LON = 'user_lon';

export const LocationProvider = ({ children }) => {
  const [userLocation, setUserLocationState] = useState(() => {
    const saved = localStorage.getItem(LS_KEY_LOCATION);
    return saved && saved !== 'Detecting location...' ? saved : 'Detecting location...';
  });
  const [lat, setLatState] = useState(() => {
    const saved = localStorage.getItem(LS_KEY_LAT);
    return saved ? parseFloat(saved) : null;
  });
  const [lon, setLonState] = useState(() => {
    const saved = localStorage.getItem(LS_KEY_LON);
    return saved ? parseFloat(saved) : null;
  });
  const [locationReady, setLocationReady] = useState(() => {
    const saved = localStorage.getItem(LS_KEY_LOCATION);
    return !!saved && saved !== 'Detecting location...';
  });
  const [detecting, setDetecting] = useState(false);

  // Synchronize with backend profile if token exists
  const syncProfileLocation = useCallback(async (locName) => {
    if (!locName || locName === 'Detecting location...') return;
    const token = localStorage.getItem('access_token');
    if (!token) return;
    try {
      await apiClient.put('/users/profiles/me', { location: locName });
    } catch (e) {
      // Profile might not exist yet or request failed; ignore
    }
  }, []);

  // Persist-aware setters
  const setUserLocation = useCallback((loc) => {
    if (!loc) return;
    setUserLocationState(loc);
    localStorage.setItem(LS_KEY_LOCATION, loc);
    syncProfileLocation(loc);
  }, [syncProfileLocation]);

  const setCoords = useCallback((latitude, longitude) => {
    setLatState(latitude);
    setLonState(longitude);
    if (latitude != null) localStorage.setItem(LS_KEY_LAT, String(latitude));
    if (longitude != null) localStorage.setItem(LS_KEY_LON, String(longitude));
  }, []);

  // Resolve coordinates using backend weather reverse-geocoding (avoids browser CORS/403 on Nominatim)
  const resolveCoordinates = useCallback(async (latitude, longitude) => {
    try {
      const res = await apiClient.post('/weather/current', {
        latitude,
        longitude
      });
      if (res.data && res.data.location) {
        const cityLoc = res.data.location;
        setUserLocation(cityLoc);
        return cityLoc;
      }
    } catch (err) {
      console.warn('Backend reverse geocoding fallback:', err);
    }
    // Static proximity fallback if backend call failed
    const fallbackName = `Region (${latitude.toFixed(2)}°N, ${longitude.toFixed(2)}°E)`;
    setUserLocation(fallbackName);
    return fallbackName;
  }, [setUserLocation]);

  // Force re-detection from browser GPS
  const refreshLocation = useCallback(async () => {
    setDetecting(true);
    if (typeof navigator === 'undefined' || !navigator.geolocation) {
      setDetecting(false);
      return;
    }

    navigator.geolocation.getCurrentPosition(
      async (position) => {
        const { latitude, longitude } = position.coords;
        setCoords(latitude, longitude);
        await resolveCoordinates(latitude, longitude);
        setLocationReady(true);
        setDetecting(false);
      },
      (error) => {
        console.warn('Browser geolocation denied or error:', error.message);
        setDetecting(false);
      },
      { timeout: 10000, enableHighAccuracy: true }
    );
  }, [setCoords, resolveCoordinates]);

  // Manual location override (e.g., user types a city name in the dashboard or chatbot)
  const updateLocationManually = useCallback(async (locationName) => {
    if (!locationName || !locationName.trim()) return;
    const cleanName = locationName.trim();
    setUserLocation(cleanName);

    try {
      // Query backend to geocode the city name accurately
      const res = await apiClient.get(`/weather/current?location=${encodeURIComponent(cleanName)}`);
      if (res.data) {
        const newLat = res.data.latitude;
        const newLon = res.data.longitude;
        const resolvedName = res.data.location || cleanName;
        if (newLat && newLon) {
          setCoords(parseFloat(newLat), parseFloat(newLon));
        }
        setUserLocation(resolvedName);
      }
    } catch (e) {
      console.warn('Geocoding location via backend failed, using raw string:', e);
    }
    setLocationReady(true);
  }, [setUserLocation, setCoords]);

  // One-time auto-detection on first boot if no location is stored
  const hasInitialized = useRef(false);
  useEffect(() => {
    if (hasInitialized.current) return;
    hasInitialized.current = true;

    const savedLoc = localStorage.getItem(LS_KEY_LOCATION);
    if (savedLoc && savedLoc !== 'Detecting location...') {
      setLocationReady(true);
      return;
    }

    // Try detecting live browser GPS
    if (typeof navigator !== 'undefined' && navigator.geolocation) {
      setDetecting(true);
      navigator.geolocation.getCurrentPosition(
        async (position) => {
          const { latitude, longitude } = position.coords;
          setCoords(latitude, longitude);
          await resolveCoordinates(latitude, longitude);
          setLocationReady(true);
          setDetecting(false);
        },
        async () => {
          // Geolocation denied or unavailable - check profile or fallback
          try {
            const profileRes = await apiClient.get('/users/profiles/me');
            if (profileRes.data && profileRes.data.location && profileRes.data.location !== 'Unknown Location') {
              setUserLocation(profileRes.data.location);
              setLocationReady(true);
              setDetecting(false);
              return;
            }
          } catch (e) {
            // Profile check skipped
          }
          // Default region
          setCoords(21.1702, 72.8311);
          setUserLocation('Surat, Gujarat');
          setLocationReady(true);
          setDetecting(false);
        },
        { timeout: 8000 }
      );
    } else {
      setCoords(21.1702, 72.8311);
      setUserLocation('Surat, Gujarat');
      setLocationReady(true);
    }
  }, [setCoords, resolveCoordinates, setUserLocation]);

  return (
    <LocationContext.Provider
      value={{
        userLocation,
        lat,
        lon,
        locationReady,
        detecting,
        setUserLocation,
        setCoords,
        refreshLocation,
        updateLocationManually
      }}
    >
      {children}
    </LocationContext.Provider>
  );
};

export const useLocation = () => useContext(LocationContext);
