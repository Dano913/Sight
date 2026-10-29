import { Search } from "lucide-react";

interface IndicatorSearchProps {
  value: string;
  onChange: (value: string) => void;
}

export default function IndicatorSearch({
  value,
  onChange,
}: IndicatorSearchProps) {
  return (
    <div className="relative w-full max-w-lg">
      <Search
        size={18}
        className="absolute left-3 top-1/2 -translate-y-1/2 text-neutral-400"
      />

      <input
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder="Search indicators..."
        className="
          w-full
          rounded-lg
          border
          border-neutral-700
          bg-neutral-900
          py-2
          pl-10
          pr-4
          text-sm
          outline-none
          transition
          focus:border-blue-500
        "
      />
    </div>
  );
}