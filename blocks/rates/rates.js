const EDGE_ORIGIN = window.location.hostname === 'localhost' ? 'http://localhost:8787' : '';

function createCard({ mainRate, bankRate }) {
  return `
    <div class="rates-card">
      <h2 class="rates-card-title">Current Rates</h2>
      <div class="rates-card-grid">
        <div class="rates-card-item">
          <span class="rates-card-label">Main Rate</span>
          <strong class="rates-card-value">${mainRate}%</strong>
        </div>
        <div class="rates-card-item">
          <span class="rates-card-label">Bank Rate</span>
          <strong class="rates-card-value">${bankRate}%</strong>
        </div>
      </div>
    </div>
  `;
}

export default async function decorate(block) {
  block.innerHTML = '<div class="rates-loading">Loading rates…</div>';

  try {
    const res = await fetch(`${EDGE_ORIGIN}/api/rates`);
    if (!res.ok) throw new Error(`Request failed: ${res.status}`);
    const { mainRate, bankRate } = await res.json();
    block.innerHTML = createCard({ mainRate, bankRate });
  } catch {
    block.innerHTML = '<p class="rates-error">Unable to load rates right now.</p>';
  }
}
