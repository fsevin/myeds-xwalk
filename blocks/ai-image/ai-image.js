import { createOptimizedPicture } from '../../scripts/aem.js';
import { getCsrfToken, uploadToDam, patchBlockImage } from '../../scripts/dam-persist.js';

const EDGE_ORIGIN = window.location.hostname === 'localhost' ? 'http://localhost:8787' : 'https://myeds-xwalk-api.fsevin.workers.dev';

async function generateAndPersist(preview, prompt, size, resource) {
  const res = await fetch(`${EDGE_ORIGIN}/api/firefly/generate-image`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ prompt, size }),
  });
  if (!res.ok) throw new Error(`Image generation failed: ${res.status}`);

  const mimeType = res.headers.get('Content-Type') || 'image/png';
  const blob = await res.blob();

  preview.src = URL.createObjectURL(blob);
  preview.hidden = false;

  const csrfToken = await getCsrfToken();
  const assetPath = await uploadToDam(blob, mimeType, csrfToken, 'firefly');

  // data-aue-resource looks like urn:aemconnection:/content/myeds-xwalk/.../firefly
  const resourcePath = resource.replace('urn:aemconnection:', '');
  await patchBlockImage(resourcePath, 'image', assetPath, csrfToken);
}

// Keyed by resource path — survives across the repeated decorate() calls Universal Editor
// triggers as the author edits fields, so we can debounce and avoid overlapping generations.
const pendingTimers = new Map();
const inFlight = new Set();
const DEBOUNCE_MS = 1200;

export default async function decorate(block) {
  const picture = block.querySelector('picture');
  const resource = block.getAttribute('data-aue-resource');

  const prompt = block.querySelector('div:first-child p, div:first-child div')?.textContent?.trim() || '';
  const aspectRatio = block.querySelector('div:nth-child(2) p, div:nth-child(2) div')?.textContent?.trim() || '1024x1024';

  block.replaceChildren();

  if (picture) {
    const img = picture.querySelector('img');
    block.append(createOptimizedPicture(img.src, img.alt, false, [{ width: '1200' }]));
    return;
  }

  // No data-aue-resource means this is a normal published/preview page, not the Universal
  // Editor canvas — never call Firefly there, only ever render an already-persisted image.
  if (!resource) return;

  if (pendingTimers.has(resource)) {
    clearTimeout(pendingTimers.get(resource));
    pendingTimers.delete(resource);
  }

  const status = document.createElement('p');
  status.className = 'ai-image-status';
  const preview = document.createElement('img');
  preview.className = 'ai-image-preview';
  preview.alt = prompt;
  preview.hidden = true;
  block.append(status, preview);

  if (!prompt) {
    status.textContent = 'Add a prompt to generate an image.';
    return;
  }

  if (inFlight.has(resource)) return;

  status.textContent = 'Waiting to generate…';
  const timerId = setTimeout(async () => {
    pendingTimers.delete(resource);
    inFlight.add(resource);
    status.textContent = 'Generating image…';
    try {
      await generateAndPersist(preview, prompt, aspectRatio, resource);
      status.textContent = 'Image saved — reloading…';
      window.location.reload();
    } catch (e) {
      inFlight.delete(resource);
      console.error('ai-image generation failed', e);
      status.textContent = `Something went wrong: ${e.message}`;
    }
  }, DEBOUNCE_MS);
  pendingTimers.set(resource, timerId);
}
