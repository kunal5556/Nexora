function MetadataItem({ label, value, testId }) {
  return (
    <span>
      <span className="text-slate-400">{label}</span>{" "}
      <span data-testid={testId} className="font-medium text-slate-600">
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
  const sourceColors = isCached ? "bg-emerald-100 text-emerald-700" : "bg-sky-100 text-sky-700";

  return (
    <div className="mt-2 flex flex-wrap items-center gap-x-4 gap-y-1 text-xs">
      <span data-testid="meta-source" className={`rounded-full px-2 py-0.5 font-semibold ${sourceColors}`}>
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
