const CHECKMARK_SVG = "url('/checkmark.svg')"

interface CheckboxProps {
  checked: boolean
  onChange: (checked: boolean) => void
  disabled?: boolean
  children: React.ReactNode
}

const Checkbox = ({ checked, onChange, disabled, children }: CheckboxProps) => (
  <label className="flex items-start gap-2">
    <input
      type="checkbox"
      className="mt-0.5 size-5 shrink-0 cursor-pointer appearance-none rounded-sm border border-gray-400 checked:border-blue-600 checked:bg-blue-600 checked:bg-no-repeat disabled:cursor-not-allowed disabled:border-neutral-300"
      style={{ backgroundImage: checked ? CHECKMARK_SVG : undefined }}
      checked={checked}
      disabled={disabled}
      onChange={(e) => onChange(e.target.checked)}
    />
    <span className={`select-none ${disabled ? "text-neutral-400" : ""}`}>{children}</span>
  </label>
)

export default Checkbox
