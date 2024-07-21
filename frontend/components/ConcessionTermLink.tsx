import TermLink from "@/components/TermLink"

interface ConcessionTermLinkProps {
  name: string
  includeIcon?: boolean
  hiddenUnderline?: boolean
  size?: "small" | "medium" | "large"
}

const ConcessionTermLink = ({
  name,
  includeIcon,
  hiddenUnderline,
  size,
}: ConcessionTermLinkProps) => {
  if (name.endsWith("Tax Farmer")) {
    return (
      <TermLink
        name="Tax Farmer"
        displayName={name}
        includeIcon={includeIcon}
        hiddenUnderline={hiddenUnderline}
        size={size}
      />
    )
  }
  if (name.endsWith("Grain")) {
    return (
      <TermLink
        name="Grain"
        displayName={name}
        includeIcon={includeIcon}
        hiddenUnderline={hiddenUnderline}
        size={size}
      />
    )
  }
  return (
    <TermLink
      name={name}
      hiddenUnderline={hiddenUnderline}
      includeIcon={includeIcon}
      size={size}
    />
  )
}

export default ConcessionTermLink
