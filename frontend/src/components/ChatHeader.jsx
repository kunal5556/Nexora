const STATUS_STYLES = {
  connecting: { label: "Connecting…", dotColor: "bg-amber-400" },
  online: { label: "Online", dotColor: "bg-emerald-500" },
  offline: { label: "Offline", dotColor: "bg-red-500" },
};

function ChatHeader({ backendStatus, onNewChat, isSending }) {
  const status = STATUS_STYLES[backendStatus];

  return (
    <header className="flex items-center justify-between gap-3">
      <div className="flex items-center gap-3">
        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-indigo-600 text-lg font-bold text-white">
          N
        </div>
        <div>
          <h1 className="text-lg font-semibold leading-tight text-slate-900">Nexora</h1>
          <p className="hidden text-xs text-slate-500 sm:block">LLM chat with key failover and response caching</p>
        </div>
      </div>
      <div className="flex items-center gap-2">
        <span
          title="Backend status"
          className="inline-flex items-center gap-1.5 rounded-full border border-slate-200 bg-white px-2.5 py-1 text-xs text-slate-600"
        >
          <span className={`h-2 w-2 rounded-full ${status.dotColor}`} />
          {status.label}
        </span>
        <button
          type="button"
          data-testid="new-chat-button"
          onClick={onNewChat}
          disabled={isSending}
          className="rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-sm font-medium text-slate-700 hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50"
        >
          New chat
        </button>
      </div>
    </header>
  );
}

export default ChatHeader;
