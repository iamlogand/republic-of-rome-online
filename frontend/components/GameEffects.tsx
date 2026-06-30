type EffectFormatter = {
  label: (level: number) => string
  annotation?: (level: number) => string
}

const EFFECT_FORMATTERS: Record<string, EffectFormatter> = {
  "evil omens": {
    label: (level) => (level === 1 ? "Evil omens" : `Evil omens ×${level}`),
    annotation: (level) => "Harder military campaigns, easier persuasions",
  },
  "allied enthusiasm": {
    label: (level) =>
      level === 1 ? "Allied enthusiasm" : "Extreme allied enthusiasm",
    annotation: (level) => `+${level === 1 ? 50 : 75}T at revenue`,
  },
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
  drought: {
    label: (level) => (level === 1 ? "Drought" : "Severe drought"),
    annotation: (level) => `famine severity +${level}`,
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
    <ul className="flex flex-col gap-2">
      {effects.map((effect, index) => {
        const { label, annotation } = formatEffect(effect)
        return (
          <li key={index}>
            <div>{label}</div>
            {annotation && (
              <span className="text-sm text-neutral-600">{annotation}</span>
            )}
          </li>
        )
      })}
    </ul>
  )
}

export default GameEffects
