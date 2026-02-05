const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const SESSION_KEY = "coffee_chat_session_id";

export interface Message {
  role: "user" | "assistant";
  content: string;
}

export function getSessionId(): string {
  if (typeof window === "undefined") return generateSessionId();
  
  let sessionId = localStorage.getItem(SESSION_KEY);
  if (!sessionId) {
    sessionId = generateSessionId();
    localStorage.setItem(SESSION_KEY, sessionId);
  }
  return sessionId;
}

function generateSessionId(): string {
  // Generate a UUID v4
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    const r = Math.random() * 16 | 0;
    const v = c === 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
}

export function setSessionId(sessionId: string): void {
  if (typeof window === "undefined") return;
  localStorage.setItem(SESSION_KEY, sessionId);
}

export function clearSession(): void {
  if (typeof window === "undefined") return;
  localStorage.removeItem(SESSION_KEY);
}

export async function loadSessionMessages(
  sessionId: string
): Promise<Message[]> {
  try {
    const response = await fetch(`${API_URL}/sessions/${sessionId}/messages`);

    if (!response.ok) {
      // For any error, just return empty messages (session probably doesn't exist yet)
      console.log("Session not found yet, will be created on first message");
      return [];
    }

    const data = await response.json();
    console.log("API returned messages:", data.messages);
    return data.messages || [];
  } catch (error) {
    console.error("Error loading session messages:", error);
    // Don't clear session on error - it will be created on first message
    return [];
  }
}

export async function sendMessage(message: string): Promise<string> {
  const sessionId = getSessionId();

  const response = await fetch(`${API_URL}/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      message,
      session_id: sessionId,
    }),
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.statusText}`);
  }

  const data = await response.json();
  return data.response;
}

export async function* streamMessage(
  message: string
): AsyncGenerator<string, void, unknown> {
  const sessionId = getSessionId();

  const response = await fetch(`${API_URL}/chat/stream`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      message,
      session_id: sessionId,
    }),
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.statusText}`);
  }

  const reader = response.body?.getReader();
  if (!reader) {
    throw new Error("No response body");
  }

  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });

    // Normalize newlines to \n and split by double newline (end of event)
    // SSE events are separated by two newlines
    const parts = buffer.replace(/\r\n/g, "\n").split("\n\n");

    // Keep the last part in the buffer as it might be incomplete
    buffer = parts.pop() || "";

    for (const part of parts) {
      const lines = part.split("\n");
      let eventData = "";
      let isDone = false;

      for (const line of lines) {
        if (line.startsWith("event: done")) {
          isDone = true;
        } else if (line.startsWith("data:")) {
          // Remove "data:" prefix
          let content = line.slice(5);
          // Remove optional leading space (standard in SSE: "data: value")
          if (content.startsWith(" ")) {
            content = content.slice(1);
          }

          if (eventData) {
            eventData += "\n";
          }
          eventData += content;
        }
      }

      if (isDone) {
        return;
      }

      if (eventData) {
        yield eventData;
      }
    }
  }
}

export async function clearChatHistory(sessionId: string): Promise<void> {
  const response = await fetch(`${API_URL}/sessions/${sessionId}`, {
    method: "DELETE",
  });

  if (!response.ok) {
    throw new Error(`Failed to clear chat: ${response.statusText}`);
  }
}
