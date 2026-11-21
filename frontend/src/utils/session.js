export function createSessionId() {
  const randomPart = Math.random().toString(36).slice(2, 10);
  return `s-${Date.now().toString(36)}-${randomPart}`;
}
