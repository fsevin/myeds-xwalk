const WMO_ICONS = {
  0: '☀️',
  1: '🌤️',
  2: '⛅',
  3: '☁️',
  45: '🌫️',
  48: '🌫️',
  51: '🌦️',
  53: '🌦️',
  55: '🌧️',
  61: '🌧️',
  63: '🌧️',
  65: '🌧️',
  71: '🌨️',
  73: '🌨️',
  75: '🌨️',
  80: '🌦️',
  81: '🌦️',
  82: '🌧️',
  95: '⛈️',
  96: '⛈️',
  99: '⛈️',
};

function weatherLabel(code) {
  return {
    0: 'Clear sky',
    1: 'Mainly clear',
    2: 'Partly cloudy',
    3: 'Overcast',
    45: 'Fog',
    48: 'Depositing rime fog',
    51: 'Light drizzle',
    53: 'Moderate drizzle',
    55: 'Dense drizzle',
    61: 'Slight rain',
    63: 'Moderate rain',
    65: 'Heavy rain',
    71: 'Slight snow',
    73: 'Moderate snow',
    75: 'Heavy snow',
    80: 'Rain showers',
    81: 'Moderate showers',
    82: 'Violent showers',
    95: 'Thunderstorm',
    96: 'Thunderstorm with hail',
    99: 'Thunderstorm with heavy hail',
  }[code] || 'Unknown';
}

async function fetchJSON(url) {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`Request failed: ${res.status}`);
  return res.json();
}

async function geocodeLocation(location) {
  const url = `https://geocoding-api.open-meteo.com/v1/search?name=${encodeURIComponent(location)}&count=1&language=en&format=json`;
  const data = await fetchJSON(url);
  return data?.results?.[0] || null;
}

async function fetchWeather(lat, lon, unit) {
  const url = new URL('https://api.open-meteo.com/v1/forecast');
  url.searchParams.set('latitude', lat);
  url.searchParams.set('longitude', lon);
  url.searchParams.set('current', 'temperature_2m,weather_code,wind_speed_10m');
  url.searchParams.set('timezone', 'auto');
  url.searchParams.set('temperature_unit', unit || 'celsius');
  return fetchJSON(url.toString());
}

function createCard({ name, country, current, unit }) {
  const code = current.weather_code;
  const icon = WMO_ICONS[code] || '🌡️';
  const label = weatherLabel(code);

  const unitSymbol = unit === 'fahrenheit' ? '°F' : '°C';

  return `
    <div class="weather-card">
      <div class="weather-card__header">
        <div>
          <p class="weather-card__location">${name}${country ? `, ${country}` : ''}</p>
          <p class="weather-card__summary">${icon} ${label}</p>
        </div>
        <div class="weather-card__temp">${Math.round(current.temperature_2m)}${unitSymbol}</div>
      </div>

      <div class="weather-card__meta">
        <div><span>Wind</span><strong>${Math.round(current.wind_speed_10m)} km/h</strong></div>
        <div><span>Condition</span><strong>${label}</strong></div>
      </div>
    </div>
  `;
}

export default async function decorate(block) {
  const location = block.querySelector('div:first-child p')?.textContent?.trim()
    || block.dataset.location
    || '';

  const unit =
    block.querySelector('div:nth-child(2) p')?.textContent?.trim().toLowerCase()
    || block.dataset.temperatureUnit
    || 'celsius';

  block.innerHTML = `<div class="weather-weather__loading">Loading weather…</div>`;

  try {
    const place = await geocodeLocation(location);
    if (!place) {
      block.innerHTML = `<p class="weather-weather__error">No location found for “${location}”.</p>`;
      return;
    }

    const weather = await fetchWeather(place.latitude, place.longitude, unit);

    block.innerHTML = createCard({
      name: place.name,
      country: place.country,
      current: weather.current_weather || weather.current,
      unit,
    });
  } catch (e) {
    block.innerHTML = `<p class="weather-weather__error">Unable to load weather right now.</p>`;
  }
}
