import MessageMetadata from "./MessageMetadata";

function MessageBubble({ message }) {
  if (message.role === "user") {
    return (
      <div className="flex justify-end">
        <div
          data-testid="user-message"
          className="max-w-[85%] whitespace-pre-wrap break-words rounded-2xl rounded-br-sm bg-sky-600 px-4 py-2 text-sm text-white"
        >
          {message.content}
        </div>
      </div>
    );
  }

  if (message.role === "error") {
    return (
      <div
        data-testid="error-message"
        role="alert"
        className="w-fit max-w-[85%] rounded-2xl rounded-bl-sm border border-red-200 bg-red-50 px-4 py-2 text-sm text-red-700"
      >
        {message.content}
      </div>
    );
  }

  return (
    <div
      data-testid="assistant-message"
      className="w-fit max-w-[85%] rounded-2xl rounded-bl-sm border border-slate-200 bg-slate-50 px-4 py-3"
    >
      <p className="whitespace-pre-wrap break-words text-sm text-slate-800">{message.content}</p>
      <MessageMetadata metadata={message.metadata} />
    </div>
  );
}

export default MessageBubble;
