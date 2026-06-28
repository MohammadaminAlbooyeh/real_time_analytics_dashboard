export function isValidEmail(email) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

export function isValidMetricKey(key) {
  return /^[a-z0-9_]+(\.[a-z0-9_]+)*$/.test(key);
}

export function isValidUrl(str) {
  try {
    new URL(str);
    return true;
  } catch {
    return false;
  }
}
