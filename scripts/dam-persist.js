// Site's DAM convention mirrors its content root (/content/myeds-xwalk/ per paths.json).
const DAM_FOLDER = '/content/dam/myeds-xwalk/generated';

export async function getCsrfToken() {
  const res = await fetch('/libs/granite/csrf/token.json', { credentials: 'include' });
  if (!res.ok) throw new Error(`CSRF token request failed: ${res.status}`);
  const { token } = await res.json();
  return token;
}

async function createDamFolder(csrfToken) {
  const apiPath = DAM_FOLDER.replace('/content/dam', '/api/assets');
  await fetch(apiPath, {
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json', 'CSRF-Token': csrfToken },
    body: JSON.stringify({ class: 'assetFolder', properties: { title: 'Generated' } }),
  });
}

// AEMaaCS direct binary upload: initiateUpload -> PUT bytes to blob storage -> completeUpload.
export async function uploadToDam(blob, mimeType, csrfToken, filePrefix) {
  const ext = mimeType === 'image/jpeg' ? 'jpg' : 'png';
  const fileName = `${filePrefix}-${Date.now()}.${ext}`;

  const initiate = () => fetch(`${DAM_FOLDER}.initiateUpload.json`, {
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded', 'CSRF-Token': csrfToken },
    body: new URLSearchParams({ fileName, fileSize: String(blob.size) }),
  });

  let initRes = await initiate();
  if (initRes.status === 404) {
    await createDamFolder(csrfToken);
    initRes = await initiate();
  }
  if (!initRes.ok) throw new Error(`initiateUpload failed: ${initRes.status}`);

  const initData = await initRes.json();
  const file = initData.files?.[0];
  if (!file?.uploadURIs?.[0]) throw new Error('initiateUpload response missing upload URI');

  const putRes = await fetch(file.uploadURIs[0], { method: 'PUT', body: blob });
  if (!putRes.ok) throw new Error(`Blob upload failed: ${putRes.status}`);

  const completeURI = file.completeURI || initData.completeURI;
  const completeRes = await fetch(completeURI, {
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded', 'CSRF-Token': csrfToken },
    body: new URLSearchParams({ fileName, mimeType, uploadToken: file.uploadToken }),
  });
  if (!completeRes.ok) throw new Error(`completeUpload failed: ${completeRes.status}`);

  return `${DAM_FOLDER}/${fileName}`;
}

export async function patchBlockImage(resourcePath, fieldName, assetPath, csrfToken) {
  const res = await fetch(resourcePath, {
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded', 'CSRF-Token': csrfToken },
    body: new URLSearchParams({ [fieldName]: assetPath }),
  });
  if (!res.ok) throw new Error(`Failed to update block content: ${res.status}`);
}
