function Avatar({ isError = false }) {
  const colors = isError ? "bg-red-100 text-red-600" : "bg-indigo-600 text-white";

  return (
    <div
      aria-hidden="true"
      className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-xs font-semibold ${colors}`}
    >
      {isError ? "!" : "N"}
    </div>
  );
}

export default Avatar;
