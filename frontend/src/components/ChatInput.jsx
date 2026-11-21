function ChatInput({ value, onChange, onSend, isSending }) {
  function handleKeyDown(event) {
    if (event.key === "Enter" && !event.shiftKey && !event.nativeEvent.isComposing) {
      event.preventDefault();
      onSend();
    }
  }

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-3 shadow-sm">
      <div className="flex items-end gap-2">
        <textarea
          data-testid="chat-input"
          aria-label="Message"
          rows={2}
          value={value}
          onChange={(event) => onChange(event.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Type your message..."
          className="flex-1 resize-none rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-sky-500 focus:outline-none"
        />
        <button
          type="button"
          data-testid="send-button"
          onClick={onSend}
          disabled={isSending || value === ""}
          className="rounded-lg bg-sky-600 px-4 py-2 text-sm font-semibold text-white hover:bg-sky-700 disabled:cursor-not-allowed disabled:opacity-50"
        >
          Send
        </button>
      </div>
      <p className="mt-1 text-xs text-slate-400">Enter to send, Shift+Enter for a new line</p>
    </div>
  );
}

export default ChatInput;
