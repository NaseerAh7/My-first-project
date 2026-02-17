export function readJson(key, fallback) {
  try {
    const raw = window.localStorage.getItem(key);
    if (!raw) return fallback;
    return JSON.parse(raw);
  } catch {
    return fallback;
  }
}

export function writeJson(key, value) {
  window.localStorage.setItem(key, JSON.stringify(value));
}

export function appendToArray(key, item, { max = 50 } = {}) {
  const arr = readJson(key, []);
  const next = [item, ...arr].slice(0, max);
  writeJson(key, next);
  return next;
}
