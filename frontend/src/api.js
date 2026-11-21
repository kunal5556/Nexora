const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || "http://localhost:8000").replace(/\/$/, "");

function readValidationMessage(data) {
  const detail = data?.detail;
  if (Array.isArray(detail) && detail.length > 0) {
    return detail[0].msg.replace(/^Value error, /, "");
  }
  if (typeof detail === "string") {
    return detail;
  }
  return "the request was invalid.";
}

function getErrorMessage(status, data) {
  if (status === 422) {
    return `Your message could not be sent: ${readValidationMessage(data)}`;
  }
  if (status === 503) {
    return "All AI providers are unavailable right now. Please try again in a moment.";
  }
  return "Something went wrong on the server. Please try again.";
}

export async function checkBackendHealth() {
  try {
    const response = await fetch(`${API_BASE_URL}/health`);
    return response.ok;
  } catch {
    return false;
  }
}

export async function sendChatMessage({ sessionId, message, systemPrompt, simulateFailure }) {
  const body = { session_id: sessionId, message };
  if (systemPrompt.trim()) {
    body.system_prompt = systemPrompt.trim();
  }

  const headers = { "Content-Type": "application/json" };
  if (simulateFailure) {
    headers["X-Simulate-Failure"] = simulateFailure;
  }

  let response;
  try {
    response = await fetch(`${API_BASE_URL}/chat`, {
      method: "POST",
      headers,
      body: JSON.stringify(body),
    });
  } catch {
    throw new Error("Could not reach the server. Please check your connection and try again.");
  }

  const data = await response.json().catch(() => null);
  if (!response.ok) {
    throw new Error(getErrorMessage(response.status, data));
  }
  return data;
}
