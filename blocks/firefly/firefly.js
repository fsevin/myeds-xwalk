const EDGE_ORIGIN = window.location.hostname === 'localhost' ? 'http://localhost:8787' : 'https://myeds-xwalk-api.fsevin.workers.dev';

async function generateImage(prompt, size) {
  const res = await fetch(`${EDGE_ORIGIN}/api/firefly/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ prompt, size }),
  });
  if (!res.ok) throw new Error(`Request failed: ${res.status}`);
  return res.json();
}

export default async function decorate(block) {
  // Model fields render as one top-level row per field, in field order (prompt, aspectRatio) —
  // index directly rather than using nth-child descendant selectors, which Universal Editor's
  // canvas can break by wrapping rich-text paragraphs in extra elements.
  const [promptRow, aspectRatioRow] = block.children;
  const prompt = promptRow?.textContent?.trim() || block.dataset.prompt || '';
  const aspectRatio = aspectRatioRow?.textContent?.trim() || block.dataset.aspectRatio || '1024x1024';

  if (!prompt) {
    block.innerHTML = '<p class="firefly-error">Add a prompt to generate an image.</p>';
    return;
  }

  block.innerHTML = '<div class="firefly-loading">Generating image…</div>';

  try {
    const { url } = await generateImage(prompt, aspectRatio);

    const img = document.createElement('img');
    img.src = url;
    img.alt = prompt;
    img.loading = 'lazy';
    img.className = 'firefly-image';

    block.innerHTML = '';
    block.append(img);
  } catch (e) {
    block.innerHTML = '<p class="firefly-error">Unable to generate image right now.</p>';
  }
}
