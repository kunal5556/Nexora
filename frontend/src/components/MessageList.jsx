import MessageBubble from "./MessageBubble";

function MessageList({ messages }) {
  return (
    <section className="min-h-0 flex-1 space-y-4 overflow-y-auto rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
      {messages.length === 0 && (
        <p className="mt-8 text-center text-sm text-slate-400">Send a message to start the conversation.</p>
      )}
      {messages.map((message) => (
        <MessageBubble key={message.id} message={message} />
      ))}
    </section>
  );
}

export default MessageList;
