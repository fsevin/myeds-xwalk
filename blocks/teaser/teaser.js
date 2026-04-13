export default function decorate(block) {
  const picture = block.querySelector('picture');
  const imageAlt = block.dataset.imageAlt || '';

  const title = block.querySelector('h2, h3, h4');
  const description = block.querySelector('p');
  const cta = block.querySelector('a');

  const wrapper = document.createElement('div');
  wrapper.className = 'teaser';

  if (picture) {
    const media = document.createElement('div');
    media.className = 'teaser-media';
    media.appendChild(picture);
    wrapper.appendChild(media);
  }

  const content = document.createElement('div');
  content.className = 'teaser-content';

  if (title) {
    const h = document.createElement('h2');
    h.textContent = title.textContent.trim();
    content.appendChild(h);
  }

  if (description) {
    const p = document.createElement('p');
    p.innerHTML = description.innerHTML;
    content.appendChild(p);
  }

  if (cta) {
    const link = document.createElement('a');
    link.href = cta.href;
    link.textContent = cta.textContent.trim();
    content.appendChild(link);
  }

  if (imageAlt) {
    const img = block.querySelector('img');
    if (img) img.alt = imageAlt;
  }

  wrapper.appendChild(content);
  block.replaceChildren(wrapper);
}
