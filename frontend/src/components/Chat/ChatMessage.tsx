"use client";

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import CoffeeIcon from "@/components/ui/CoffeeIcon";
import { Source } from "@/lib/api";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface ChatMessageProps {
  role: "user" | "assistant";
  content: string;
  isStreaming?: boolean;
  sources?: Source[];
}

function humanizeName(name: string): string {
  return name
    .replace(/\.pdf$/i, "")
    .replace(/-/g, " ")
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

function truncate(text: string, max = 40): string {
  return text.length > max ? text.slice(0, max - 1) + "…" : text;
}

export default function ChatMessage({ role, content, isStreaming, sources }: ChatMessageProps) {
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
            {/* Show "Thinking..." when streaming but no content yet */}
            {isStreaming && !content ? (
              <div className="flex items-center gap-2 text-coffee-primary/70">
                <span className="text-sm italic">Thinking...</span>
                <span className="inline-flex gap-1">
                  <span className="typing-dot w-1.5 h-1.5 bg-coffee-primary rounded-full" />
                  <span className="typing-dot w-1.5 h-1.5 bg-coffee-primary rounded-full" />
                  <span className="typing-dot w-1.5 h-1.5 bg-coffee-primary rounded-full" />
                </span>
              </div>
            ) : (
              <>
                <ReactMarkdown remarkPlugins={[remarkGfm]}>{content}</ReactMarkdown>
                {isStreaming && content && (
                  <span className="inline-flex gap-1 ml-1">
                    <span className="typing-dot w-1.5 h-1.5 bg-coffee-primary rounded-full" />
                    <span className="typing-dot w-1.5 h-1.5 bg-coffee-primary rounded-full" />
                    <span className="typing-dot w-1.5 h-1.5 bg-coffee-primary rounded-full" />
                  </span>
                )}
                {!isStreaming && sources && sources.length > 0 && (
                  <div className="border-t border-coffee-senary/30 mt-3 pt-2">
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="text-xs font-medium text-coffee-primary/70">Sources:</span>
                      {sources.map((source, i) => {
                        const isExternal = source.url.startsWith("http");
                        const href = isExternal ? source.url : `${API_URL}${source.url}`;
                        // For external links use the source name directly; for PDFs humanize the filename
                        const rawLabel = isExternal ? source.name : humanizeName(source.name);
                        const label = truncate(rawLabel);

                        return (
                          <a
                            key={i}
                            href={href}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-flex items-center gap-1 px-2 py-0.5 text-xs rounded-full bg-coffee-senary/20 text-coffee-primary hover:bg-coffee-senary/40 transition-colors"
                          >
                            {isExternal ? (
                              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" className="w-3 h-3">
                                <path fillRule="evenodd" d="M4.22 11.78a.75.75 0 0 1 0-1.06L9.44 5.5H5.75a.75.75 0 0 1 0-1.5h5.5a.75.75 0 0 1 .75.75v5.5a.75.75 0 0 1-1.5 0V6.56l-5.22 5.22a.75.75 0 0 1-1.06 0Z" clipRule="evenodd" />
                              </svg>
                            ) : (
                              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" className="w-3 h-3">
                                <path d="M3.5 2A1.5 1.5 0 0 0 2 3.5v9A1.5 1.5 0 0 0 3.5 14h9a1.5 1.5 0 0 0 1.5-1.5v-7A1.5 1.5 0 0 0 12.5 5h-4L7.44 3.44A1.5 1.5 0 0 0 6.38 3H3.5Z" />
                              </svg>
                            )}
                            {label}
                          </a>
                        );
                      })}
                    </div>
                  </div>
                )}
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
