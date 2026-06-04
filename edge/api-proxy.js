// Allowed origins — update these to match your aem.live / aem.page URLs
const ALLOWED_ORIGINS = [
  'https://main--myeds-xwalk--adobe-rnd.aem.live',
  'https://main--myeds-xwalk--adobe-rnd.aem.page',
  'http://localhost:3000',
];

// Cache TTLs in seconds
const GEOCODE_TTL = 86400; // 24h — location data is stable
const FORECAST_TTL = 900;  // 15min — weather updates frequently
const RATES_TTL = 300;     // 5min — financial rates can change during the day

function corsHeaders(origin) {
  const allow = ALLOWED_ORIGINS.includes(origin) ? origin : ALLOWED_ORIGINS[0];
  return {
    'Access-Control-Allow-Origin': allow,
    'Access-Control-Allow-Methods': 'GET, OPTIONS',
    'Access-Control-Max-Age': '86400',
  };
}

function jsonError(message, status, cors) {
  return new Response(JSON.stringify({ error: message }), {
    status,
    headers: { 'Content-Type': 'application/json', ...cors },
  });
}

async function cachedFetch(upstreamUrl, ttl, init = {}) {
  const cache = caches.default;
  const key = new Request(upstreamUrl);

  const hit = await cache.match(key);
  if (hit) return hit;

  const res = await fetch(upstreamUrl, init);
  if (!res.ok) return res;

  const response = new Response(res.body, res);
  response.headers.set('Cache-Control', `public, max-age=${ttl}`);
  await cache.put(key, response.clone());
  return response;
}

async function handleGeocode(request, cors) {
  const { searchParams } = new URL(request.url);
  const name = searchParams.get('name');
  if (!name) return jsonError('Missing name', 400, cors);

  const upstream = `https://geocoding-api.open-meteo.com/v1/search?name=${encodeURIComponent(name)}&count=1&language=en&format=json`;
  const res = await cachedFetch(upstream, GEOCODE_TTL);
  return new Response(res.body, {
    status: res.status,
    headers: { 'Content-Type': 'application/json', ...cors },
  });
}

async function handleRates(env, cors) {
  const res = await cachedFetch(
    env.AEM_GRAPHQL_URL,
    RATES_TTL,
    { headers: { Authorization: `Bearer ${env.AEM_TOKEN}` } },
  );

  if (!res.ok) {
    return jsonError(`AEM request failed: ${res.status}`, 502, cors);
  }

  const json = await res.json();
  const item = json?.data?.cfmodelcustomerByPath?.item;

  if (!item) {
    return jsonError('Rate data not found in AEM response', 404, cors);
  }

  return new Response(
    JSON.stringify({ mainRate: item.mainRate, bankRate: item.bankRate }),
    { status: 200, headers: { 'Content-Type': 'application/json', ...cors } },
  );
}

async function handleForecast(request, cors) {
  const { searchParams } = new URL(request.url);
  const lat = searchParams.get('latitude');
  const lon = searchParams.get('longitude');
  if (!lat || !lon) return jsonError('Missing latitude or longitude', 400, cors);

  const upstream = new URL('https://api.open-meteo.com/v1/forecast');
  upstream.searchParams.set('latitude', lat);
  upstream.searchParams.set('longitude', lon);
  upstream.searchParams.set('current', 'temperature_2m,weather_code,wind_speed_10m');
  upstream.searchParams.set('timezone', 'auto');
  upstream.searchParams.set('temperature_unit', searchParams.get('temperature_unit') || 'celsius');

  const res = await cachedFetch(upstream.toString(), FORECAST_TTL);
  return new Response(res.body, {
    status: res.status,
    headers: { 'Content-Type': 'application/json', ...cors },
  });
}

export default {
  async fetch(request, env) {
    const { pathname } = new URL(request.url);
    const origin = request.headers.get('Origin') || '';
    const cors = corsHeaders(origin);

    if (request.method === 'OPTIONS') {
      return new Response(null, { status: 204, headers: cors });
    }
    if (request.method !== 'GET') {
      return new Response('Method Not Allowed', { status: 405 });
    }

    if (pathname === '/api/geocode') return handleGeocode(request, cors);
    if (pathname === '/api/forecast') return handleForecast(request, cors);
    if (pathname === '/api/rates') return handleRates(env, cors);

    return new Response('Not Found', { status: 404 });
  },
};
