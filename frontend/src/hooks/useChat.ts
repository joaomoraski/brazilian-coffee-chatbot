"use client";

import { useState, useCallback, useEffect } from "react";
import {
  Message,
  streamMessage,
  getSessionId,
  loadSessionMessages,
} from "@/lib/api";

interface UseChatReturn {
  messages: Message[];
  isLoading: boolean;
  error: string | null;
  sendMessage: (content: string) => Promise<void>;
}

export function useChat(): UseChatReturn {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isInitialized, setIsInitialized] = useState(false);

  // Load chat history on mount
  useEffect(() => {
    const loadHistory = async () => {
      try {
        const sessionId = getSessionId();
        console.log("Loading history for session:", sessionId);
        const history = await loadSessionMessages(sessionId);
        console.log("Loaded history:", history);
        if (history && history.length > 0) {
          setMessages(history);
        }
      } catch (err) {
        console.error("Failed to load history:", err);
        // Don't clear session - it will be created on first message
      } finally {
        setIsInitialized(true);
      }
    };

    loadHistory();
  }, []);

  const sendMessage = useCallback(
    async (content: string) => {
      if (!isInitialized) return;

      setError(null);
      setIsLoading(true);

      // Add user message
      const userMessage: Message = { role: "user", content };
      setMessages((prev) => [...prev, userMessage]);

      // Add empty assistant message for streaming
      const assistantMessage: Message = { role: "assistant", content: "" };
      setMessages((prev) => [...prev, assistantMessage]);

      try {
        let fullContent = "";
        let hasContent = false;

        for await (const chunk of streamMessage(content)) {
          fullContent += chunk;
          hasContent = true;
          setMessages((prev) => {
            const newMessages = [...prev];
            const lastMessage = newMessages[newMessages.length - 1];
            if (lastMessage.role === "assistant") {
              lastMessage.content = fullContent;
            }
            return newMessages;
          });
        }

        // If no content was streamed, there was likely an error
        if (!hasContent) {
          throw new Error("No response received from server");
        }
      } catch (err) {
        console.error("Chat error:", err);
        const errorMessage = err instanceof Error ? err.message : "Failed to get response from server";
        setError(errorMessage);
        
        // Remove both user and assistant messages on error
        setMessages((prev) => prev.slice(0, -2));
      } finally {
        setIsLoading(false);
      }
    },
    [isInitialized]
  );

  return {
    messages,
    isLoading,
    error,
    sendMessage,
  };
}
