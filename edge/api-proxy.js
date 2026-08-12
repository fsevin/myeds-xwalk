// Allowed origins — update these to match your aem.live / aem.page URLs
const ALLOWED_ORIGINS = [
  'https://main--myeds-xwalk--fsevin.aem.live',
  'https://main--myeds-xwalk--fsevin.aem.page',
  'https://author-p42808-e1367915.adobeaemcloud.com',
  'http://localhost:3000',
];

// Cache TTLs in seconds
const GEOCODE_TTL = 86400; // 24h — location data is stable
const FORECAST_TTL = 900; // 15min — weather updates frequently
const RATES_TTL = 300; // 5min — financial rates can change during the day

function corsHeaders(origin) {
  const allow = ALLOWED_ORIGINS.includes(origin) ? origin : ALLOWED_ORIGINS[0];
  return {
    'Access-Control-Allow-Origin': allow,
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
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
    headers: { 'Content-Type': 'application/json; charset=utf-8', ...cors },
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

const FIREFLY_VALID_SIZES = [
  '1024x1024',
  '1344x768',
  '768x1344',
];

// IMS access tokens live ~24h; cache in-isolate so we don't re-authenticate on every image request.
let cachedImsToken = null;
let cachedImsTokenExpiry = 0;

async function getFireflyToken(env) {
  if (cachedImsToken && Date.now() < cachedImsTokenExpiry) {
    return cachedImsToken;
  }

  const res = await fetch('https://ims-na1.adobelogin.com/ims/token/v3', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({
      grant_type: 'client_credentials',
      client_id: env.FIREFLY_CLIENT_ID,
      client_secret: env.FIREFLY_CLIENT_SECRET,
      scope: env.FIREFLY_SCOPES,
    }),
  });

  if (!res.ok) {
    throw new Error(`IMS token request failed: ${res.status}`);
  }

  const data = await res.json();
  cachedImsToken = data.access_token;
  // Refresh a minute early to avoid using a token that expires mid-flight.
  cachedImsTokenExpiry = Date.now() + ((data.expires_in - 60) * 1000);
  return cachedImsToken;
}

function parsePromptAndSize(body) {
  const prompt = body?.prompt?.trim();
  const size = FIREFLY_VALID_SIZES.includes(body?.size) ? body.size : '1024x1024';
  return { prompt, size };
}

async function fireflyGenerate(prompt, size, env) {
  const [width, height] = size.split('x').map(Number);
  const token = await getFireflyToken(env);

  const res = await fetch('https://firefly-api.adobe.io/v3/images/generate', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Accept: 'application/json',
      Authorization: `Bearer ${token}`,
      'x-api-key': env.FIREFLY_CLIENT_ID,
    },
    body: JSON.stringify({
      prompt,
      size: { width, height },
      numVariations: 1,
    }),
  });

  if (!res.ok) {
    throw new Error(`Firefly generate failed: ${res.status}`);
  }

  const data = await res.json();
  const image = data?.outputs?.[0]?.image;
  if (!image?.url) {
    throw new Error('Firefly response missing image URL');
  }
  return image.url;
}

async function uploadImageToFirefly(bytes, mimeType, env) {
  const token = await getFireflyToken(env);

  const res = await fetch('https://firefly-api.adobe.io/v2/storage/image', {
    method: 'POST',
    headers: {
      'Content-Type': mimeType,
      Accept: 'application/json',
      Authorization: `Bearer ${token}`,
      'x-api-key': env.FIREFLY_CLIENT_ID,
    },
    body: bytes,
  });

  if (!res.ok) {
    throw new Error(`Firefly image upload failed: ${res.status}`);
  }

  const data = await res.json();
  const id = data?.images?.[0]?.id;
  if (!id) {
    throw new Error('Firefly upload response missing image id');
  }
  return id;
}

// Structure Reference: generates a new scene guided by the uploaded product photo's
// shape/composition, so the product reads as "the same" while the prompt drives context/style.
async function fireflyGenerateVariant(prompt, size, uploadId, strength, env) {
  const [width, height] = size.split('x').map(Number);
  const token = await getFireflyToken(env);

  const res = await fetch('https://firefly-api.adobe.io/v3/images/generate', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Accept: 'application/json',
      Authorization: `Bearer ${token}`,
      'x-api-key': env.FIREFLY_CLIENT_ID,
    },
    body: JSON.stringify({
      prompt,
      size: { width, height },
      numVariations: 1,
      contentClass: 'photo',
      structure: {
        strength,
        imageReference: { source: { uploadId } },
      },
    }),
  });

  if (!res.ok) {
    throw new Error(`Firefly generate failed: ${res.status}`);
  }

  const data = await res.json();
  const image = data?.outputs?.[0]?.image;
  if (!image?.url) {
    throw new Error('Firefly response missing image URL');
  }
  return image.url;
}

async function handleFireflyGenerateVariant(request, env, cors) {
  let form;
  try {
    form = await request.formData();
  } catch {
    return jsonError('Invalid form data', 400, cors);
  }

  const prompt = form.get('prompt')?.toString().trim();
  if (!prompt) return jsonError('Missing prompt', 400, cors);

  const size = FIREFLY_VALID_SIZES.includes(form.get('size')) ? form.get('size') : '1024x1024';

  const strengthRaw = Number(form.get('strength'));
  const strength = Number.isFinite(strengthRaw) ? Math.min(100, Math.max(1, strengthRaw)) : 65;

  const image = form.get('image');
  if (!(image instanceof File) || image.size === 0) {
    return jsonError('Missing image', 400, cors);
  }

  let url;
  try {
    const bytes = await image.arrayBuffer();
    const uploadId = await uploadImageToFirefly(bytes, image.type || 'image/jpeg', env);
    url = await fireflyGenerateVariant(prompt, size, uploadId, strength, env);
  } catch (e) {
    return jsonError(e.message, 502, cors);
  }

  const imageRes = await fetch(url);
  if (!imageRes.ok) {
    return jsonError(`Failed to download generated image: ${imageRes.status}`, 502, cors);
  }

  return new Response(imageRes.body, {
    status: 200,
    headers: {
      'Content-Type': imageRes.headers.get('Content-Type') || 'image/png',
      ...cors,
    },
  });
}

async function handleFireflyGenerate(request, env, cors) {
  let body;
  try {
    body = await request.json();
  } catch {
    return jsonError('Invalid JSON body', 400, cors);
  }

  const { prompt, size } = parsePromptAndSize(body);
  if (!prompt) return jsonError('Missing prompt', 400, cors);

  let url;
  try {
    url = await fireflyGenerate(prompt, size, env);
  } catch (e) {
    return jsonError(e.message, 502, cors);
  }

  return new Response(
    JSON.stringify({ url }),
    { status: 200, headers: { 'Content-Type': 'application/json', ...cors } },
  );
}

// Same as handleFireflyGenerate, but streams the image bytes back directly instead of a
// presigned URL — used by the ai-image block, which re-uploads the bytes into AEM's DAM
// and needs them client-side without depending on the Firefly URL's ~1h expiry or S3 CORS.
async function handleFireflyGenerateImage(request, env, cors) {
  let body;
  try {
    body = await request.json();
  } catch {
    return jsonError('Invalid JSON body', 400, cors);
  }

  const { prompt, size } = parsePromptAndSize(body);
  if (!prompt) return jsonError('Missing prompt', 400, cors);

  let url;
  try {
    url = await fireflyGenerate(prompt, size, env);
  } catch (e) {
    return jsonError(e.message, 502, cors);
  }

  const imageRes = await fetch(url);
  if (!imageRes.ok) {
    return jsonError(`Failed to download generated image: ${imageRes.status}`, 502, cors);
  }

  return new Response(imageRes.body, {
    status: 200,
    headers: {
      'Content-Type': imageRes.headers.get('Content-Type') || 'image/png',
      ...cors,
    },
  });
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
    headers: { 'Content-Type': 'application/json; charset=utf-8', ...cors },
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

    if (pathname === '/api/firefly/generate') {
      if (request.method !== 'POST') return new Response('Method Not Allowed', { status: 405 });
      return handleFireflyGenerate(request, env, cors);
    }

    if (pathname === '/api/firefly/generate-image') {
      if (request.method !== 'POST') return new Response('Method Not Allowed', { status: 405 });
      return handleFireflyGenerateImage(request, env, cors);
    }

    if (pathname === '/api/firefly/generate-variant') {
      if (request.method !== 'POST') return new Response('Method Not Allowed', { status: 405 });
      return handleFireflyGenerateVariant(request, env, cors);
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
