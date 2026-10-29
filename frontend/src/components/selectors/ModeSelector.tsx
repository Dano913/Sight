import type { Mode } from "../../pages/indicators/types";

interface ModeSelectorProps {
  mode: Mode;
  onChange: (mode: Mode) => void;
}

const TABS: { key: Mode; label: string }[] = [
  { key: "timeline", label: "Timeline" },
  { key: "compare", label: "Compare" },
];

export default function ModeSelector({ mode, onChange }: ModeSelectorProps) {
  return (
    <div className="inline-flex gap-1 rounded-lg border border-[#32485f] bg-[#1b2a39] p-1">
      {TABS.map((tab) => (
        <button
          key={tab.key}
          onClick={() => onChange(tab.key)}
          className={`rounded-md px-4 py-2 text-sm font-medium transition ${
            mode === tab.key
              ? "bg-blue-500 text-white"
              : "text-slate-400 hover:text-white"
          }`}
        >
          {tab.label}
        </button>
      ))}
    </div>
  );
}