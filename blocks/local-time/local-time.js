function formatParts(date, timeZone, hour12) {
  const dateFormatter = new Intl.DateTimeFormat(undefined, {
    timeZone: timeZone || undefined,
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });

  const timeFormatter = new Intl.DateTimeFormat(undefined, {
    timeZone: timeZone || undefined,
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12,
  });

  return {
    date: dateFormatter.format(date),
    time: timeFormatter.format(date),
  };
}

export default function decorate(block) {
  const label = block.querySelector('div:nth-child(1) p, div:nth-child(1) div')?.textContent?.trim()
    || block.dataset.label
    || '';

  const timeZone = block.querySelector('div:nth-child(2) p, div:nth-child(2) div')?.textContent?.trim()
    || block.dataset.timeZone
    || '';

  const hour12 = (block.querySelector('div:nth-child(3) p, div:nth-child(3) div')?.textContent?.trim().toLowerCase()
    || block.dataset.hour12
    || '24-hour') === '12-hour';

  block.innerHTML = `
    <div class="local-time-card">
      ${label ? `<p class="local-time-label">${label}</p>` : ''}
      <div class="local-time-clock" aria-live="polite"></div>
      <p class="local-time-date"></p>
    </div>
  `;

  const clockEl = block.querySelector('.local-time-clock');
  const dateEl = block.querySelector('.local-time-date');

  function render() {
    let parts;
    try {
      parts = formatParts(new Date(), timeZone, hour12);
    } catch {
      parts = formatParts(new Date(), undefined, hour12);
    }
    clockEl.textContent = parts.time;
    dateEl.textContent = parts.date;
  }

  render();
  setInterval(render, 1000);
}
