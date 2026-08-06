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
  const prompt = block.querySelector('div:first-child p, div:first-child div')?.textContent?.trim()
    || block.dataset.prompt
    || '';

  const aspectRatio = block.querySelector('div:nth-child(2) p, div:nth-child(2) div')?.textContent?.trim()
    || block.dataset.aspectRatio
    || '1024x1024';

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
