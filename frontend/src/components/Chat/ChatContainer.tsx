"use client";

import { useEffect, useRef } from "react";
import { useChat } from "@/hooks/useChat";
import ChatMessage from "./ChatMessage";
import ChatInput from "./ChatInput";
import CoffeeIcon from "@/components/ui/CoffeeIcon";

export default function ChatContainer() {
  const { messages, isLoading, error, sendMessage } = useChat();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div className="flex flex-col h-[calc(100vh-180px)] bg-white/50 backdrop-blur-sm rounded-3xl shadow-xl border border-coffee-senary/20 overflow-hidden">
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
            <div className="mt-6 grid grid-cols-2 gap-2 text-xs">
              <SuggestionChip onClick={() => sendMessage("What is the history of coffee in Brazil?")}>
                ☕ History of Brazilian coffee
              </SuggestionChip>
              <SuggestionChip onClick={() => sendMessage("How is coffee classified by quality levels?")}>
                ⭐ Coffee quality classification
              </SuggestionChip>
              <SuggestionChip onClick={() => sendMessage("What are the best brewing methods?")}>
                🫖 Brewing methods
              </SuggestionChip>
              <SuggestionChip onClick={() => sendMessage("Where are the main coffee regions in Brazil?")}>
                🗺️ Coffee regions in Brazil
              </SuggestionChip>
            </div>
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
        <div className="px-6 py-2">
          <div className="bg-coffee-quaternary/10 text-coffee-quaternary text-sm rounded-lg px-4 py-2">
            {error}
          </div>
        </div>
      )}

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
}: {
  children: React.ReactNode;
  onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      className="px-3 py-2 bg-coffee-senary/30 hover:bg-coffee-senary/50 text-coffee-primary rounded-lg transition-colors text-left"
    >
      {children}
    </button>
  );
}
