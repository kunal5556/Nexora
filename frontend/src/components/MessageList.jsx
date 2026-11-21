import { useEffect, useRef } from "react";
import MessageBubble from "./MessageBubble";

function MessageList({ messages, isSending }) {
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isSending]);

  return (
    <section
      aria-live="polite"
      className="min-h-0 flex-1 space-y-4 overflow-y-auto rounded-xl border border-slate-200 bg-white p-4 shadow-sm"
    >
      {messages.length === 0 && (
        <p className="mt-8 text-center text-sm text-slate-400">Send a message to start the conversation.</p>
      )}
      {messages.map((message) => (
        <MessageBubble key={message.id} message={message} />
      ))}
      {isSending && (
        <div
          data-testid="loading-indicator"
          className="w-fit animate-pulse rounded-2xl rounded-bl-sm bg-slate-100 px-4 py-2 text-sm text-slate-500"
        >
          Thinking…
        </div>
      )}
      <div ref={bottomRef} />
    </section>
  );
}

export default MessageList;
