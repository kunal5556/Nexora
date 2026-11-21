import { useEffect, useRef } from "react";
import Avatar from "./Avatar";
import MessageBubble from "./MessageBubble";

const EXAMPLE_PROMPTS = [
  "What is the capital of France?",
  "Explain response caching in one sentence.",
  "What does an API key do? Answer in two sentences.",
];

function MessageList({ messages, isSending, onPickExample }) {
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isSending]);

  return (
    <section
      aria-live="polite"
      className="min-h-0 flex-1 overflow-y-auto rounded-2xl border border-slate-200 bg-white p-4 shadow-sm sm:p-5"
    >
      {messages.length === 0 ? (
        <div className="flex min-h-full flex-col items-center justify-center py-4 text-center">
          <h2 className="text-base font-semibold text-slate-800">Start a conversation</h2>
          <p className="mt-1 max-w-sm text-sm text-slate-500">
            Every reply shows whether it came from the cache, which model and key answered, and the tokens used for that request.
          </p>
          <div className="mt-5 flex flex-wrap justify-center gap-2">
            {EXAMPLE_PROMPTS.map((prompt) => (
              <button
                key={prompt}
                type="button"
                onClick={() => onPickExample(prompt)}
                className="rounded-full border border-slate-200 bg-white px-3 py-1.5 text-xs text-slate-600 hover:border-indigo-300 hover:text-indigo-700"
              >
                {prompt}
              </button>
            ))}
          </div>
        </div>
      ) : (
        <div className="space-y-5">
          {messages.map((message) => (
            <MessageBubble key={message.id} message={message} />
          ))}
          {isSending && (
            <div className="flex items-start gap-3">
              <Avatar />
              <div
                data-testid="loading-indicator"
                className="flex items-center gap-1.5 rounded-2xl rounded-tl-md border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-500"
              >
                <span>Thinking</span>
                {[0, 1, 2].map((dot) => (
                  <span
                    key={dot}
                    style={{ animationDelay: `${dot * 150}ms` }}
                    className="h-1.5 w-1.5 animate-bounce rounded-full bg-slate-400"
                  />
                ))}
              </div>
            </div>
          )}
          <div ref={bottomRef} />
        </div>
      )}
    </section>
  );
}

export default MessageList;
