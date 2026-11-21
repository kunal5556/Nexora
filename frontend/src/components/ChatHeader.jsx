function ChatHeader({ sessionId }) {
  return (
    <header className="flex flex-wrap items-center justify-between gap-3">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">LLM Chatbot</h1>
        <p className="text-sm text-slate-500">Key failover and response caching</p>
      </div>
      <span className="break-all text-xs text-slate-500">Session: {sessionId}</span>
    </header>
  );
}

export default ChatHeader;
