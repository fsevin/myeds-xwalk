import { createOptimizedPicture } from '../../scripts/aem.js';
import { getCsrfToken, uploadToDam, patchBlockImage } from '../../scripts/dam-persist.js';

const EDGE_ORIGIN = window.location.hostname === 'localhost' ? 'http://localhost:8787' : 'https://myeds-xwalk-api.fsevin.workers.dev';

// Field order mirrors _product-variant.json: productImage, prompt, aspectRatio,
// resultImage — each field is a direct child div of the block.
function fieldText(block, index) {
  return block.querySelector(`:scope > div:nth-child(${index}) p, :scope > div:nth-child(${index}) div`)?.textContent?.trim() || '';
}

function fieldPicture(block, index) {
  return block.querySelector(`:scope > div:nth-child(${index}) picture`);
}

async function generateAndPersist(preview, sourceImg, prompt, size, resource) {
  const sourceRes = await fetch(sourceImg.src, { credentials: 'include' });
  if (!sourceRes.ok) throw new Error(`Failed to read product image: ${sourceRes.status}`);
  const sourceBlob = await sourceRes.blob();

  const form = new FormData();
  form.append('image', sourceBlob, 'product.jpg');
  form.append('prompt', prompt);
  form.append('size', size);

  const res = await fetch(`${EDGE_ORIGIN}/api/firefly/generate-variant`, { method: 'POST', body: form });
  if (!res.ok) throw new Error(`Variant generation failed: ${res.status}`);

  const mimeType = res.headers.get('Content-Type') || 'image/png';
  const blob = await res.blob();

  preview.src = URL.createObjectURL(blob);
  preview.hidden = false;

  const csrfToken = await getCsrfToken();
  const assetPath = await uploadToDam(blob, mimeType, csrfToken, 'product-variant');

  // data-aue-resource looks like urn:aemconnection:/content/myeds-xwalk/.../product-variant
  const resourcePath = resource.replace('urn:aemconnection:', '');
  await patchBlockImage(resourcePath, 'resultImage', assetPath, csrfToken);
}

// Keyed by resource path — survives across the repeated decorate() calls Universal Editor
// triggers as the author edits fields, so we can debounce and avoid overlapping generations.
const pendingTimers = new Map();
const inFlight = new Set();
const DEBOUNCE_MS = 1200;

export default async function decorate(block) {
  const resource = block.getAttribute('data-aue-resource');

  const sourcePicture = fieldPicture(block, 1);
  const prompt = fieldText(block, 2);
  const aspectRatio = fieldText(block, 3) || '1024x1024';
  const resultPicture = fieldPicture(block, 4);

  block.replaceChildren();

  if (resultPicture) {
    const img = resultPicture.querySelector('img');
    block.append(createOptimizedPicture(img.src, img.alt, false, [{ width: '1200' }]));
    return;
  }

  // Nothing to work from yet — the product image field is required, but may be empty
  // for a moment while the author is still filling in the block.
  if (!sourcePicture) return;

  const sourceImg = sourcePicture.querySelector('img');

  // No data-aue-resource means this is a normal published/preview page, not the Universal
  // Editor canvas — never call Firefly there, only ever render an already-persisted variant
  // or, failing that, the original product photo.
  if (!resource) {
    block.append(createOptimizedPicture(sourceImg.src, sourceImg.alt, false, [{ width: '1200' }]));
    return;
  }

  if (pendingTimers.has(resource)) {
    clearTimeout(pendingTimers.get(resource));
    pendingTimers.delete(resource);
  }

  const preview = document.createElement('img');
  preview.className = 'product-variant-preview';
  preview.hidden = true;
  const status = document.createElement('p');
  status.className = 'product-variant-status';

  block.append(createOptimizedPicture(sourceImg.src, sourceImg.alt, false, [{ width: '600' }]), status, preview);

  if (!prompt) {
    status.textContent = 'Add a prompt to generate a variant.';
    return;
  }

  if (inFlight.has(resource)) return;

  preview.alt = prompt;

  status.textContent = 'Waiting to generate…';
  const timerId = setTimeout(async () => {
    pendingTimers.delete(resource);
    inFlight.add(resource);
    status.textContent = 'Generating variant…';
    try {
      await generateAndPersist(preview, sourceImg, prompt, aspectRatio, resource);
      status.textContent = 'Variant saved — reloading…';
      window.location.reload();
    } catch (e) {
      inFlight.delete(resource);
      console.error('product-variant generation failed', e);
      status.textContent = `Something went wrong: ${e.message}`;
    }
  }, DEBOUNCE_MS);
  pendingTimers.set(resource, timerId);
}
