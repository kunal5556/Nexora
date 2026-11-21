function MetadataItem({ label, value, testId }) {
  return (
    <span className="rounded-md bg-white px-2 py-0.5 text-slate-500 ring-1 ring-inset ring-slate-200">
      {label}{" "}
      <span data-testid={testId} className="font-medium text-slate-700">
        {value}
      </span>
    </span>
  );
}

function MessageMetadata({ metadata }) {
  if (!metadata) {
    return null;
  }

  const isCached = metadata.resolution_source === "LLM_CACHE";
  const sourceColors = isCached
    ? "bg-emerald-50 text-emerald-700 ring-emerald-200"
    : "bg-indigo-50 text-indigo-700 ring-indigo-200";

  return (
    <div className="mt-3 flex flex-wrap items-center gap-1.5 border-t border-slate-200 pt-2.5 text-xs">
      <span
        data-testid="meta-source"
        className={`rounded-md px-2 py-0.5 font-semibold ring-1 ring-inset ${sourceColors}`}
      >
        {metadata.resolution_source}
      </span>
      <MetadataItem label="Model" value={metadata.model} testId="meta-model" />
      <MetadataItem label="Latency" value={`${metadata.latency_ms} ms`} testId="meta-latency" />
      <MetadataItem label="Input tokens" value={metadata.input_tokens} testId="meta-input-tokens" />
      <MetadataItem label="Output tokens" value={metadata.output_tokens} testId="meta-output-tokens" />
      <MetadataItem label="Key" value={metadata.key_id ?? "none (cache)"} />
      <MetadataItem label="Fallbacks" value={metadata.fallback_attempts} />
    </div>
  );
}

export default MessageMetadata;
