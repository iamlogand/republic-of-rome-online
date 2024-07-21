import TermLink from "@/components/TermLink"

interface ConcessionTermLinkProps {
  name: string
  hiddenUnderline?: boolean
}

const ConcessionTermLink = ({
  name,
  hiddenUnderline,
}: ConcessionTermLinkProps) => {
  if (name.endsWith("Tax Farmer")) {
    return (
      <TermLink
        name="Tax Farmer"
        displayName={name}
        hiddenUnderline={hiddenUnderline}
      />
    )
  }
  if (name.endsWith("Grain")) {
    return (
      <TermLink
        name="Grain"
        displayName={name}
        hiddenUnderline={hiddenUnderline}
      />
    )
  }
  return <TermLink name={name} hiddenUnderline={hiddenUnderline} />
}

export default ConcessionTermLink
