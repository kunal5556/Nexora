function ChatInput({ value, onChange, onSend, isSending }) {
  return (
    <div className="flex items-end gap-2 rounded-xl border border-slate-200 bg-white p-3 shadow-sm">
      <textarea
        data-testid="chat-input"
        aria-label="Message"
        rows={2}
        value={value}
        onChange={(event) => onChange(event.target.value)}
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
  );
}

export default ChatInput;
