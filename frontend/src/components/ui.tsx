import React from "react";

export function Card({
  title,
  right,
  children
}: {
  title?: string;
  right?: React.ReactNode;
  children: React.ReactNode;
}) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white shadow-sm">
      {(title || right) && (
        <div className="flex items-center justify-between border-b border-slate-100 px-4 py-3">
          <div className="text-sm font-semibold text-slate-800">{title}</div>
          <div>{right}</div>
        </div>
      )}
      <div className="p-4">{children}</div>
    </div>
  );
}

export function Button({
  children,
  onClick,
  type = "button",
  variant = "primary",
  disabled
}: {
  children: React.ReactNode;
  onClick?: () => void;
  type?: "button" | "submit";
  variant?: "primary" | "secondary" | "danger";
  disabled?: boolean;
}) {
  const base =
    "inline-flex items-center justify-center rounded-lg px-3 py-2 text-sm font-semibold transition disabled:opacity-50";
  const styles =
    variant === "danger"
      ? "bg-rose-600 text-white hover:bg-rose-700"
      : variant === "secondary"
        ? "bg-slate-100 text-slate-900 hover:bg-slate-200"
        : "bg-indigo-600 text-white hover:bg-indigo-700";
  return (
    <button type={type} onClick={onClick} disabled={disabled} className={`${base} ${styles}`}>
      {children}
    </button>
  );
}

export function Input({
  label,
  value,
  onChange,
  placeholder,
  type = "text",
  required
}: {
  label?: string;
  value: string;
  onChange: (v: string) => void;
  placeholder?: string;
  type?: string;
  required?: boolean;
}) {
  return (
    <label className="block">
      {label && <div className="mb-1 text-xs font-semibold text-slate-700">{label}</div>}
      <input
        required={required}
        type={type}
        value={value}
        placeholder={placeholder}
        onChange={(e) => onChange(e.target.value)}
        className="w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm outline-none focus:border-indigo-400"
      />
    </label>
  );
}

export function TextArea({
  label,
  value,
  onChange,
  placeholder
}: {
  label?: string;
  value: string;
  onChange: (v: string) => void;
  placeholder?: string;
}) {
  return (
    <label className="block">
      {label && <div className="mb-1 text-xs font-semibold text-slate-700">{label}</div>}
      <textarea
        value={value}
        placeholder={placeholder}
        onChange={(e) => onChange(e.target.value)}
        className="min-h-[80px] w-full resize-y rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm outline-none focus:border-indigo-400"
      />
    </label>
  );
}

export function Select({
  label,
  value,
  onChange,
  options
}: {
  label?: string;
  value: string;
  onChange: (v: string) => void;
  options: { value: string; label: string }[];
}) {
  return (
    <label className="block">
      {label && <div className="mb-1 text-xs font-semibold text-slate-700">{label}</div>}
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm outline-none focus:border-indigo-400"
      >
        {options.map((o) => (
          <option key={o.value} value={o.value}>
            {o.label}
          </option>
        ))}
      </select>
    </label>
  );
}

export function formatINR(amount: number) {
  try {
    return new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR" }).format(amount);
  } catch {
    return `₹${amount.toFixed(2)}`;
  }
}

