import TermLink from "@/components/TermLink"

interface SenatorFactProps {
  name: string
  termName?: string
  selectable?: boolean
  compressed?: boolean
}

const SenatorFact = ({
  name,
  termName,
  selectable,
  compressed,
}: SenatorFactProps) => {
  // Dead Senator is a special case
  if (name === "Dead Senator") {
    return (
      <span>
        Dead <TermLink name="Senator" disabled={!selectable} />
      </span>
    )
  }

  // If there is no term name, just display the name
  if (!termName) {
    return <span>{name}</span>
  }

  return (
    <span>
      <TermLink
        name={termName}
        displayName={name}
        disabled={!selectable}
        hideText={compressed}
        includeIcon
      />
    </span>
  )
}

export default SenatorFact
