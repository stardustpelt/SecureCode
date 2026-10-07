const API_BASE_URL = (
  process.env.REACT_APP_API_BASE_URL || 'https://secure-code-5m4t.onrender.com'
).replace(/\/+$/, '');

const API_ROOT = `${API_BASE_URL}/api`;

async function requestJson(path, options) {
  let response;
  try {
    response = await fetch(`${API_ROOT}${path}`, options);
  } catch (error) {
    throw new Error(`Could not reach the analysis API: ${error.message}`);
  }

  const responseText = await response.text();
  let result = null;
  try {
    result = responseText ? JSON.parse(responseText) : null;
  } catch {}

  if (!response.ok) {
    const message = result?.error || result?.detail || result?.message;
    throw new Error(message || `Analysis request failed (${response.status}).`);
  }

  if (!result || typeof result !== 'object') {
    throw new Error('The analysis API returned an invalid response.');
  }

  return result;
}

export function scanCode(payload) {
  return requestJson('/analyze/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
}

export function scanFile(file) {
  const formData = new FormData();
  formData.append('file', file);

  return requestJson('/analyze/', {
    method: 'POST',
    body: formData,
  });
}

export function getReportDownloadUrl(reportId) {
  return `${API_ROOT}/report/${encodeURIComponent(reportId)}/?download=true`;
}
