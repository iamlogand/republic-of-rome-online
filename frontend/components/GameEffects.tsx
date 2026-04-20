type EffectFormatter = {
  label: (level: number) => string
  annotation?: (level: number) => string
}

const EFFECT_FORMATTERS: Record<string, EffectFormatter> = {
  "manpower shortage": {
    label: (level) =>
      level === 1 ? "Manpower shortage" : "Increased manpower shortage",
    annotation: (level) => `+${level * 10}T legion/fleet cost`,
  },
  "land bill I": {
    label: () => "Type I land bill",
    annotation: () => "20T due at revenue",
  },
  "land bill II": {
    label: (level) =>
      level === 1 ? "Type II land bill" : `Type II land bill ×${level} `,
    annotation: (level) => `costs ${level * 5}T/turn`,
  },
  "land bill III": {
    label: (level) =>
      level === 1 ? "Type III land bill" : `Type III land bill ×${level}`,
    annotation: (level) => `costs ${level * 10}T/turn`,
  },
}

const parseEffect = (
  effectString: string,
): { baseName: string; level: number } => {
  const colonIndex = effectString.indexOf(":")
  return {
    baseName:
      colonIndex >= 0 ? effectString.slice(0, colonIndex) : effectString,
    level:
      colonIndex >= 0 ? parseInt(effectString.slice(colonIndex + 1), 10) : 1,
  }
}

const formatEffect = (
  effectString: string,
): { label: string; annotation?: string } => {
  const { baseName, level } = parseEffect(effectString)
  const formatter = EFFECT_FORMATTERS[baseName]
  if (formatter) {
    return {
      label: formatter.label(level),
      annotation: formatter.annotation?.(level),
    }
  }
  return { label: baseName.charAt(0).toUpperCase() + baseName.slice(1) }
}

interface GameEffectsProps {
  effects: string[]
}

const GameEffects = ({ effects }: GameEffectsProps) => {
  if (effects.length === 0) return null

  return (
    <div>
      Effects:
      <ul>
        {effects.map((effect, index) => {
          const { label, annotation } = formatEffect(effect)
          return (
            <li key={index} className="ml-10 list-disc">
              {label}
              {annotation && (
                <span className="text-neutral-600"> ({annotation})</span>
              )}
            </li>
          )
        })}
      </ul>
    </div>
  )
}

export default GameEffects
