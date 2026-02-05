"use client";

import ReactMarkdown from "react-markdown";
import CoffeeIcon from "@/components/ui/CoffeeIcon";

interface ChatMessageProps {
  role: "user" | "assistant";
  content: string;
  isStreaming?: boolean;
}

export default function ChatMessage({ role, content, isStreaming }: ChatMessageProps) {
  const isUser = role === "user";

  return (
    <div
      className={`message-enter flex gap-3 ${
        isUser ? "flex-row-reverse" : "flex-row"
      }`}
    >
      {/* Avatar */}
      <div
        className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center ${
          isUser
            ? "bg-coffee-tertiary text-white"
            : "bg-coffee-primary text-coffee-secondary"
        }`}
      >
        {isUser ? (
          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24"
            fill="currentColor"
            className="w-6 h-6"
          >
            <path
              fillRule="evenodd"
              d="M7.5 6a4.5 4.5 0 119 0 4.5 4.5 0 01-9 0zM3.751 20.105a8.25 8.25 0 0116.498 0 .75.75 0 01-.437.695A18.683 18.683 0 0112 22.5c-2.786 0-5.433-.608-7.812-1.7a.75.75 0 01-.437-.695z"
              clipRule="evenodd"
            />
          </svg>
        ) : (
          <CoffeeIcon size={24} animated={isStreaming} />
        )}
      </div>

      {/* Message bubble */}
      <div
        className={`max-w-[80%] rounded-2xl px-4 py-3 ${
          isUser
            ? "bg-coffee-primary text-white rounded-tr-sm"
            : "bg-white text-gray-800 shadow-md border border-coffee-senary/30 rounded-tl-sm"
        }`}
      >
        {isUser ? (
          <p className="whitespace-pre-wrap">{content}</p>
        ) : (
          <div className="prose prose-sm max-w-none prose-headings:text-coffee-primary prose-a:text-coffee-tertiary prose-strong:text-coffee-primary">
            <ReactMarkdown>{content}</ReactMarkdown>
            {isStreaming && (
              <span className="inline-flex gap-1 ml-1">
                <span className="typing-dot w-1.5 h-1.5 bg-coffee-primary rounded-full" />
                <span className="typing-dot w-1.5 h-1.5 bg-coffee-primary rounded-full" />
                <span className="typing-dot w-1.5 h-1.5 bg-coffee-primary rounded-full" />
              </span>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
