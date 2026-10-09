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
  '2688x1536',
];

// Image5 is only exposed through the async v4 endpoint (there is no sync v5/v4 endpoint);
// the model is selected via this header rather than a body field.
const FIREFLY_MODEL_VERSION = 'image5';
const FIREFLY_JOB_POLL_INTERVAL_MS = 1500;
const FIREFLY_JOB_POLL_TIMEOUT_MS = 60_000;

// video1_standard's supported sizes per Firefly's video usage notes — one preset per
// aspect ratio, matching the options exposed on the product-variant-video block.
const FIREFLY_VIDEO_VALID_SIZES = [
  '1920x1080',
  '1080x1920',
  '1080x1080',
];
const FIREFLY_VIDEO_MODEL_VERSION = 'video1_standard';
// Video jobs render a 5s clip and routinely take a minute or two — poll less often and
// over a much longer window than the image job above.
const FIREFLY_VIDEO_JOB_POLL_INTERVAL_MS = 6000;
const FIREFLY_VIDEO_JOB_POLL_TIMEOUT_MS = 180_000;

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

// Maps the block's WxH size options onto Image5's coarse aspectRatio classes. Only used for
// pure text-to-image generation — see fireflyGenerateVariant for why reference-image requests
// can't use this.
function sizeToAspectRatio(size) {
  const [width, height] = size.split('x').map(Number);
  if (width === height) return '1:1';
  return width > height ? '16:9' : '9:16';
}

// Image5 only exists behind the async v4 endpoint — there's no sync v4/v5 "generate" call.
// Every request accepted (202) returns a jobId/statusUrl that must be polled until the job
// reports succeeded/failed/cancelled/timeout.
async function pollFireflyJob(
  statusUrl,
  token,
  env,
  pollIntervalMs = FIREFLY_JOB_POLL_INTERVAL_MS,
  pollTimeoutMs = FIREFLY_JOB_POLL_TIMEOUT_MS,
) {
  const deadline = Date.now() + pollTimeoutMs;

  while (Date.now() < deadline) {
    // Each iteration depends on the previous poll's outcome (and the delay below) before
    // deciding whether to continue — this is inherently sequential, not a batch of
    // independent requests, so looped awaits are intentional here.
    // eslint-disable-next-line no-await-in-loop
    const res = await fetch(statusUrl, {
      headers: {
        Accept: 'application/json',
        Authorization: `Bearer ${token}`,
        'x-api-key': env.FIREFLY_CLIENT_ID,
      },
    });

    if (!res.ok) {
      throw new Error(`Firefly job status check failed: ${res.status}`);
    }

    // eslint-disable-next-line no-await-in-loop
    const data = await res.json();

    if (data.status === 'succeeded') {
      // Image jobs nest the result under `image`; video jobs (despite the comment this
      // replaces claiming otherwise) nest it under `video` instead — check both so this
      // poller stays shared between the image and video generation flows.
      const output = data.result?.outputs?.[0];
      const url = output?.image?.url || output?.video?.url;
      if (!url) {
        throw new Error('Firefly job succeeded but response is missing an output URL');
      }
      return url;
    }

    if (['failed', 'cancelled', 'timeout'].includes(data.status)) {
      throw new Error(`Firefly job ${data.status}: ${data.message || data.error_code || 'unknown error'}`);
    }

    // eslint-disable-next-line no-await-in-loop
    await new Promise((resolve) => { setTimeout(resolve, pollIntervalMs); });
  }

  throw new Error('Firefly job timed out waiting for a result');
}

async function submitFireflyJob(payload, env) {
  const token = await getFireflyToken(env);

  const res = await fetch('https://firefly-api.adobe.io/v4/images/generate-async', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Accept: 'application/json',
      Authorization: `Bearer ${token}`,
      'x-api-key': env.FIREFLY_CLIENT_ID,
      'x-model-version': FIREFLY_MODEL_VERSION,
    },
    body: JSON.stringify(payload),
  });

  if (res.status !== 202) {
    throw new Error(`Firefly generate failed: ${res.status}`);
  }

  const { statusUrl } = await res.json();
  if (!statusUrl) {
    throw new Error('Firefly response missing statusUrl');
  }

  return pollFireflyJob(statusUrl, token, env);
}

async function fireflyGenerate(prompt, size, env) {
  return submitFireflyJob({
    prompt,
    modelId: 'firefly_image',
    aspectRatio: sizeToAspectRatio(size),
    numVariations: 1,
    referenceBlobs: [],
  }, env);
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

// Image5 reference: conditions generation on the uploaded product photo (color, shape,
// general design) via referenceBlobs, so the product reads as "the same" while the prompt
// drives the new scene. Unlike the old Structure Reference, this isn't pixel-preserving —
// fine detail like small logos can still be redrawn. Per Adobe's spec, aspectRatio must be
// omitted (or "auto") whenever referenceBlobs is populated, so the block's size field no
// longer has any effect here — the output dimensions follow the reference image instead.
async function fireflyGenerateVariant(prompt, uploadId, env) {
  return submitFireflyJob({
    prompt,
    modelId: 'firefly_image',
    aspectRatio: 'auto',
    numVariations: 1,
    referenceBlobs: [{ source: { uploadId }, usage: 'general' }],
  }, env);
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

  // Note: Image5's reference-image mode always derives output dimensions from the uploaded
  // image (aspectRatio forced to "auto" — see fireflyGenerateVariant), so a 'size' form field
  // is no longer read here; it has no effect on the generated variant.
  const image = form.get('image');
  if (!(image instanceof File) || image.size === 0) {
    return jsonError('Missing image', 400, cors);
  }

  let url;
  try {
    const bytes = await image.arrayBuffer();
    const uploadId = await uploadImageToFirefly(bytes, image.type || 'image/jpeg', env);
    url = await fireflyGenerateVariant(prompt, uploadId, env);
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

// Video analog of fireflyGenerateVariant: anchors video1_standard's first frame (placement
// position 0) on the uploaded product photo via /v3/videos/generate, instead of Image5's
// referenceBlobs. cameraMotion/shotSize/shotAngle/promptStyle are pinned to the values
// verified against the sandbox Firefly Video Generation Postman collection rather than
// exposed as block fields, since Adobe hasn't published the full enum list for them yet.
async function submitFireflyVideoJob(prompt, uploadId, size, env) {
  const token = await getFireflyToken(env);
  const [width, height] = size.split('x').map(Number);

  const res = await fetch('https://firefly-api.adobe.io/v3/videos/generate', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Accept: 'application/json',
      Authorization: `Bearer ${token}`,
      'x-api-key': env.FIREFLY_CLIENT_ID,
      'x-model-version': FIREFLY_VIDEO_MODEL_VERSION,
    },
    body: JSON.stringify({
      prompt,
      image: {
        conditions: [{ source: { uploadId }, placement: { position: 0 } }],
      },
      sizes: [{ width, height }],
      videoSettings: {
        cameraMotion: 'camera zoom in',
        shotSize: 'medium shot',
        shotAngle: 'eye_level shot',
        promptStyle: 'cinematic',
      },
    }),
  });

  if (res.status !== 202) {
    throw new Error(`Firefly video generate failed: ${res.status}`);
  }

  const { statusUrl } = await res.json();
  if (!statusUrl) {
    throw new Error('Firefly video response missing statusUrl');
  }

  // Video output lands under result.outputs[0].video.url rather than .image.url —
  // pollFireflyJob checks both so it can stay shared between the image and video flows.
  return pollFireflyJob(
    statusUrl,
    token,
    env,
    FIREFLY_VIDEO_JOB_POLL_INTERVAL_MS,
    FIREFLY_VIDEO_JOB_POLL_TIMEOUT_MS,
  );
}

async function handleFireflyGenerateVariantVideo(request, env, cors) {
  let form;
  try {
    form = await request.formData();
  } catch {
    return jsonError('Invalid form data', 400, cors);
  }

  const prompt = form.get('prompt')?.toString().trim();
  if (!prompt) return jsonError('Missing prompt', 400, cors);

  const sizeRaw = form.get('size')?.toString();
  const size = FIREFLY_VIDEO_VALID_SIZES.includes(sizeRaw) ? sizeRaw : FIREFLY_VIDEO_VALID_SIZES[0];

  const image = form.get('image');
  if (!(image instanceof File) || image.size === 0) {
    return jsonError('Missing image', 400, cors);
  }

  let url;
  try {
    const bytes = await image.arrayBuffer();
    const uploadId = await uploadImageToFirefly(bytes, image.type || 'image/jpeg', env);
    url = await submitFireflyVideoJob(prompt, uploadId, size, env);
  } catch (e) {
    return jsonError(e.message, 502, cors);
  }

  const videoRes = await fetch(url);
  if (!videoRes.ok) {
    return jsonError(`Failed to download generated video: ${videoRes.status}`, 502, cors);
  }

  return new Response(videoRes.body, {
    status: 200,
    headers: {
      'Content-Type': videoRes.headers.get('Content-Type') || 'video/mp4',
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

    if (pathname === '/api/firefly/generate-variant-video') {
      if (request.method !== 'POST') return new Response('Method Not Allowed', { status: 405 });
      return handleFireflyGenerateVariantVideo(request, env, cors);
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
