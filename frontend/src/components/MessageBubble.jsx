import Avatar from "./Avatar";
import MessageMetadata from "./MessageMetadata";

function MessageBubble({ message }) {
  if (message.role === "user") {
    return (
      <div className="flex justify-end">
        <div
          data-testid="user-message"
          className="min-w-0 max-w-[80%] whitespace-pre-wrap break-words rounded-2xl rounded-br-md bg-indigo-600 px-4 py-2.5 text-sm text-white shadow-sm"
        >
          {message.content}
        </div>
      </div>
    );
  }

  if (message.role === "error") {
    return (
      <div className="flex items-start gap-3">
        <Avatar isError />
        <div
          data-testid="error-message"
          role="alert"
          className="min-w-0 max-w-[80%] rounded-2xl rounded-tl-md border border-red-200 bg-red-50 px-4 py-2.5 text-sm text-red-700"
        >
          {message.content}
        </div>
      </div>
    );
  }

  return (
    <div className="flex items-start gap-3">
      <Avatar />
      <div
        data-testid="assistant-message"
        className="min-w-0 max-w-[80%] rounded-2xl rounded-tl-md border border-slate-200 bg-slate-50 px-4 py-3"
      >
        <p className="whitespace-pre-wrap break-words text-sm leading-relaxed text-slate-800">{message.content}</p>
        <MessageMetadata metadata={message.metadata} />
      </div>
    </div>
  );
}

export default MessageBubble;
