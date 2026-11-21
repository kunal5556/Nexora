function SessionSettings({ systemPrompt, onSystemPromptChange }) {
  return (
    <section className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
      <label htmlFor="system-prompt" className="mb-1 block text-sm font-medium text-slate-700">
        System prompt (optional)
      </label>
      <textarea
        id="system-prompt"
        data-testid="system-prompt-input"
        rows={2}
        value={systemPrompt}
        onChange={(event) => onSystemPromptChange(event.target.value)}
        placeholder="e.g. You are a friendly tutor who answers in short sentences."
        className="w-full resize-none rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-sky-500 focus:outline-none"
      />
    </section>
  );
}

export default SessionSettings;
