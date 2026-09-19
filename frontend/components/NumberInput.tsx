interface NumberInputProps {
  label: string
  value: number
  onChange: (value: number) => void
  min?: number
  max?: number
  id?: string
  required?: boolean
  disabled?: boolean
  hideSlider?: boolean
}

const NumberInput = ({
  label,
  value,
  onChange,
  min,
  max,
  id,
  required,
  disabled,
  hideSlider,
}: NumberInputProps) => {
  const showSlider = !hideSlider && min !== undefined && max !== undefined && min < max

  const handleMinus = () => {
    if (max !== undefined && value > max) {
      onChange(max)
    } else {
      onChange(value - 1)
    }
  }

  const handlePlus = () => {
    if (min !== undefined && value < min) {
      onChange(min)
    } else {
      onChange(value + 1)
    }
  }

  return (
    <div className="flex w-[350px] flex-col gap-1">
      <label htmlFor={id} className="font-semibold">
        {label}
      </label>
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={handleMinus}
            disabled={disabled || (min !== undefined ? value <= min : false)}
            className="flex h-6 min-w-6 items-center justify-center select-none rounded-full border border-red-600 text-red-600 hover:bg-red-100 disabled:border-neutral-300 disabled:text-neutral-400 disabled:hover:bg-transparent"
          >
            &minus;
          </button>
          <input
            id={id}
            type="number"
            min={min}
            max={max}
            value={value}
            onChange={(e) => onChange(Number(e.target.value))}
            required={required}
            disabled={disabled}
            className="w-[80px] rounded-md border border-blue-600 p-1 px-1.5 disabled:cursor-not-allowed disabled:bg-neutral-100"
          />
          <button
            type="button"
            onClick={handlePlus}
            disabled={disabled || (max !== undefined ? value >= max : false)}
            className="flex h-6 min-w-6 items-center justify-center select-none rounded-full border border-green-600 text-green-600 hover:bg-green-100 disabled:border-neutral-300 disabled:text-neutral-400 disabled:hover:bg-transparent"
          >
            +
          </button>
        </div>
        {showSlider && (
          <div className="flex w-full items-center justify-center">
            <button
              type="button"
              className={`w-10 cursor-default px-2 text-sm ${value !== min && "text-neutral-400"}`}
              onClick={() => onChange(min)}
              disabled={disabled}
            >
              {min}
            </button>
            <input
              type="range"
              min={min}
              max={max}
              value={value}
              onChange={(e) => onChange(Number(e.target.value))}
              disabled={disabled}
              className="w-full disabled:cursor-not-allowed"
            />
            <button
              type="button"
              className={`w-10 cursor-default px-2 text-sm ${value !== max && "text-neutral-400"}`}
              onClick={() => onChange(max)}
              disabled={disabled}
            >
              {max}
            </button>
          </div>
        )}
      </div>
    </div>
  )
}

export default NumberInput
