const MAX_MESSAGE_LENGTH = 4000;

function ChatInput({ inputRef, value, onChange, onSend, isSending }) {
  const characterCount = value.trim().length;
  const isTooLong = characterCount > MAX_MESSAGE_LENGTH;

  function handleKeyDown(event) {
    if (event.key === "Enter" && !event.shiftKey && !event.nativeEvent.isComposing) {
      event.preventDefault();
      onSend();
    }
  }

  return (
    <div>
      <div className="flex items-end gap-2 rounded-2xl border border-slate-300 bg-white p-2 shadow-sm focus-within:border-indigo-500 focus-within:ring-2 focus-within:ring-indigo-100">
        <textarea
          ref={inputRef}
          data-testid="chat-input"
          aria-label="Message"
          rows={2}
          value={value}
          onChange={(event) => onChange(event.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Type your message..."
          className="flex-1 resize-none bg-transparent px-2 py-1.5 text-sm text-slate-800 placeholder:text-slate-400 focus:outline-none"
        />
        <button
          type="button"
          data-testid="send-button"
          onClick={onSend}
          disabled={isSending || value === ""}
          className="rounded-xl bg-indigo-600 px-4 py-2 text-sm font-semibold text-white hover:bg-indigo-700 disabled:cursor-not-allowed disabled:bg-slate-300"
        >
          Send
        </button>
      </div>
      <div className="mt-1.5 flex justify-between gap-3 px-1 text-xs text-slate-500">
        <span>Enter to send, Shift+Enter for a new line</span>
        <span className={isTooLong ? "font-medium text-red-600" : ""}>
          {characterCount} / {MAX_MESSAGE_LENGTH}
        </span>
      </div>
    </div>
  );
}

export default ChatInput;
