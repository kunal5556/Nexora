function ChatHeader({ sessionId, onNewChat, isSending }) {
  return (
    <header className="flex flex-wrap items-center justify-between gap-3">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">LLM Chatbot</h1>
        <p className="text-sm text-slate-500">Key failover and response caching</p>
      </div>
      <div className="flex items-center gap-3">
        <span className="break-all text-xs text-slate-500">Session: {sessionId}</span>
        <button
          type="button"
          data-testid="new-chat-button"
          onClick={onNewChat}
          disabled={isSending}
          className="shrink-0 rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-sm font-medium text-slate-700 hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50"
        >
          New chat
        </button>
      </div>
    </header>
  );
}

export default ChatHeader;
