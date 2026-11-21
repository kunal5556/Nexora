const FAILURE_OPTIONS = ["key_1=429", "key_1=500", "key_1=429,key_2=500", "*=429"];

function SessionSettings({ sessionId, systemPrompt, onSystemPromptChange, isLocked, simulateFailure, onSimulateFailureChange }) {
  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-3 shadow-sm sm:p-4">
      <div className="mb-3 flex items-center justify-between gap-3">
        <h2 className="shrink-0 text-sm font-semibold text-slate-800">Session settings</h2>
        <span className="min-w-0 truncate text-xs text-slate-500">
          Session <span className="font-mono text-slate-600">{sessionId}</span>
        </span>
      </div>
      <div className="grid gap-3 sm:grid-cols-[2fr_1fr] sm:gap-4">
        <div>
          <label htmlFor="system-prompt" className="mb-1 block text-xs font-medium text-slate-600">
            System prompt (optional)
          </label>
          <textarea
            id="system-prompt"
            data-testid="system-prompt-input"
            rows={2}
            value={systemPrompt}
            onChange={(event) => onSystemPromptChange(event.target.value)}
            disabled={isLocked}
            placeholder="e.g. You are a friendly tutor who answers in short sentences."
            className="w-full resize-none rounded-lg border border-slate-300 px-3 py-2 text-sm placeholder:text-slate-400 focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-100 disabled:bg-slate-50 disabled:text-slate-500"
          />
          {isLocked && (
            <p className="mt-1 text-xs text-slate-500">Locked – start a new chat to change it.</p>
          )}
        </div>
        <div>
          <label htmlFor="simulate-failure" className="mb-1 block text-xs font-medium text-slate-600">
            Simulate key failure (demo)
          </label>
          <select
            id="simulate-failure"
            data-testid="simulate-failure-select"
            value={simulateFailure}
            onChange={(event) => onSimulateFailureChange(event.target.value)}
            className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-100"
          >
            <option value="">None</option>
            {FAILURE_OPTIONS.map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
          <p className="mt-1 hidden text-xs text-slate-500 sm:block">
            Sends the X-Simulate-Failure header with the next message only.
          </p>
        </div>
      </div>
    </section>
  );
}

export default SessionSettings;
