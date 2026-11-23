const PALETTE = [
  { fill: "oklch(70.4% 0.191 22.216)", hover: "oklch(80.8% 0.114 19.571)" }, // red
  { fill: "oklch(75% 0.183 55.934)", hover: "oklch(83.7% 0.128 66.29)" }, // orange
  { fill: "oklch(85.2% 0.199 91.936)", hover: "oklch(90.5% 0.182 98.111)" }, // yellow
  { fill: "oklch(79.2% 0.209 151.711)", hover: "oklch(87.1% 0.15 154.449)" }, // green
  { fill: "oklch(70.7% 0.165 254.624)", hover: "oklch(80.9% 0.105 251.813)" }, // blue
  { fill: "oklch(71.4% 0.203 305.504)", hover: "oklch(82.7% 0.119 306.383)" }, // purple
]

export const FILL_COLORS: string[] = PALETTE.map((c) => c.fill)

export const HOVER_COLORS = new Map(PALETTE.map((c) => [c.fill, c.hover]))

export const COLOR_VALUES: (string | null)[] = [null, ...FILL_COLORS]
