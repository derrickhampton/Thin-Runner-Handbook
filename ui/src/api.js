export async function fetchJson(path, options = {}) {
  const response = await fetch(path, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  });

  if (!response.ok) {
    const maybeJson = await response.text();
    throw new Error(maybeJson || `Request failed: ${response.status}`);
  }

  return response.json();
}
