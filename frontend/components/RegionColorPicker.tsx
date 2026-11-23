import { useEffect, useRef, useState } from "react"

import { COLOR_VALUES } from "../data/colors"

interface RegionColorPickerProps {
  color: string | null
  onChange: (color: string | null) => void
}

export default function RegionColorPicker({
  color,
  onChange,
}: RegionColorPickerProps) {
  const [open, setOpen] = useState(false)
  const ref = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!open) return
    const handleClick = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setOpen(false)
      }
    }
    document.addEventListener("mousedown", handleClick)
    return () => document.removeEventListener("mousedown", handleClick)
  }, [open])

  return (
    <div ref={ref} style={{ position: "relative" }}>
      <div
        onClick={() => setOpen(!open)}
        style={{
          width: 12,
          height: 12,
          background: color ?? "#000",
          border: "1px solid rgba(255,255,255,0.5)",
          borderRadius: 2,
          cursor: "pointer",
          flexShrink: 0,
        }}
      />
      {open && (
        <div
          style={{
            position: "absolute",
            top: -1,
            left: 18,
            display: "flex",
            gap: 3,
            background: "rgba(0,0,0,0.8)",
            padding: 3,
            borderRadius: 3,
            zIndex: 1,
          }}
        >
          {COLOR_VALUES.map((c, i) => (
            <div
              key={i}
              onClick={() => {
                onChange(c)
                setOpen(false)
              }}
              style={{
                width: 14,
                height: 14,
                background: c ?? "#000",
                border:
                  c === color
                    ? "2px solid #fff"
                    : "1px solid rgba(255,255,255,0.3)",
                borderRadius: 2,
                cursor: "pointer",
              }}
            />
          ))}
        </div>
      )}
    </div>
  )
}
