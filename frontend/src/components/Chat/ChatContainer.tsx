"use client";

import { useEffect, useRef, useState } from "react";
import { useChat } from "@/hooks/useChat";
import ChatMessage from "./ChatMessage";
import ChatInput from "./ChatInput";
import CoffeeIcon from "@/components/ui/CoffeeIcon";

export default function ChatContainer() {
  const { messages, isLoading, error, sendMessage, clearChat } = useChat();
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [showSuggestions, setShowSuggestions] = useState(true);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSuggestionClick = (text: string) => {
    if (!isLoading) {
      sendMessage(text);
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-180px)] bg-white/50 backdrop-blur-sm rounded-3xl shadow-xl border border-coffee-senary/20 overflow-hidden">
      {/* Header with Clear Chat button */}
      {messages.length > 0 && (
        <div className="flex justify-end px-4 py-2 border-b border-coffee-senary/20">
          <button
            onClick={clearChat}
            disabled={isLoading}
            className="text-xs text-coffee-primary/70 hover:text-coffee-primary disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-1 transition-colors"
          >
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="w-4 h-4">
              <path fillRule="evenodd" d="M8.75 1A2.75 2.75 0 006 3.75v.443c-.795.077-1.584.176-2.365.298a.75.75 0 10.23 1.482l.149-.022.841 10.518A2.75 2.75 0 007.596 19h4.807a2.75 2.75 0 002.742-2.53l.841-10.519.149.023a.75.75 0 00.23-1.482A41.03 41.03 0 0014 3.193V3.75A2.75 2.75 0 0011.25 1h-2.5zM10 4c.84 0 1.673.025 2.5.075V3.75c0-.69-.56-1.25-1.25-1.25h-2.5c-.69 0-1.25.56-1.25 1.25v.325C8.327 4.025 9.16 4 10 4zM8.58 7.72a.75.75 0 00-1.5.06l.3 7.5a.75.75 0 101.5-.06l-.3-7.5zm4.34.06a.75.75 0 10-1.5-.06l-.3 7.5a.75.75 0 101.5.06l.3-7.5z" clipRule="evenodd" />
            </svg>
            Clear Chat
          </button>
        </div>
      )}

      {/* Messages area */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center text-gray-500">
            <CoffeeIcon size={64} className="text-coffee-primary mb-4" animated />
            <h2 className="text-xl font-semibold text-coffee-primary mb-2">
              Welcome to Brazilian Coffee Chatbot!
            </h2>
            <p className="max-w-md text-sm">
              Ask me anything about Brazilian coffee - from its rich history to
              brewing methods, from plantation techniques to finding the best
              coffee shops near you.
            </p>
          </div>
        ) : (
          messages.map((message, index) => (
            <ChatMessage
              key={index}
              role={message.role}
              content={message.content}
              isStreaming={isLoading && index === messages.length - 1 && message.role === "assistant"}
            />
          ))
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Error message */}
      {error && (
        <div className="px-6 py-3">
          <div className="bg-red-50 border border-red-200 text-red-700 text-sm rounded-lg px-4 py-3 flex items-start gap-2">
            <span className="text-lg">⚠️</span>
            <div className="flex-1">
              <strong className="font-semibold">Error:</strong> {error}
            </div>
            <button
              onClick={() => window.location.reload()}
              className="text-red-600 hover:text-red-800 underline text-xs"
            >
              Retry
            </button>
          </div>
        </div>
      )}

      {/* Sticky Suggestions */}
      <div className="px-4 py-2 border-t border-coffee-senary/10">
        <div className="flex items-center justify-between mb-2">
          <button
            onClick={() => setShowSuggestions(!showSuggestions)}
            className="text-xs text-coffee-primary/60 hover:text-coffee-primary flex items-center gap-1 transition-colors"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 20 20"
              fill="currentColor"
              className={`w-4 h-4 transition-transform ${showSuggestions ? "rotate-180" : ""}`}
            >
              <path fillRule="evenodd" d="M5.23 7.21a.75.75 0 011.06.02L10 11.168l3.71-3.938a.75.75 0 111.08 1.04l-4.25 4.5a.75.75 0 01-1.08 0l-4.25-4.5a.75.75 0 01.02-1.06z" clipRule="evenodd" />
            </svg>
            Quick suggestions
          </button>
        </div>
        {showSuggestions && (
          <div className="flex flex-wrap gap-2 text-xs">
            <SuggestionChip onClick={() => handleSuggestionClick("What is the history of coffee in Brazil?")} disabled={isLoading}>
              ☕ History
            </SuggestionChip>
            <SuggestionChip onClick={() => handleSuggestionClick("How is coffee classified by quality levels?")} disabled={isLoading}>
              ⭐ Quality
            </SuggestionChip>
            <SuggestionChip onClick={() => handleSuggestionClick("What are the best brewing methods?")} disabled={isLoading}>
              🫖 Brewing
            </SuggestionChip>
            <SuggestionChip onClick={() => handleSuggestionClick("Where are the main coffee regions in Brazil?")} disabled={isLoading}>
              🗺️ Regions
            </SuggestionChip>
          </div>
        )}
      </div>

      {/* Input area */}
      <div className="p-4 border-t border-coffee-senary/20">
        <ChatInput onSend={sendMessage} disabled={isLoading} />
      </div>
    </div>
  );
}

function SuggestionChip({
  children,
  onClick,
  disabled,
}: {
  children: React.ReactNode;
  onClick: () => void;
  disabled?: boolean;
}) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className="px-3 py-1.5 bg-coffee-senary/30 hover:bg-coffee-senary/50 text-coffee-primary rounded-full transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
    >
      {children}
    </button>
  );
}
