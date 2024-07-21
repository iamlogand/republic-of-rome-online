import TermLink from "@/components/TermLink"

interface TalentsAmountProps {
  amount: number
  sign?: "+" | "-"
  size?: "small" | "medium" | "large"
}

const TalentsAmount = ({ amount, sign, size }: TalentsAmountProps) => (
  <span className="text-nowrap font-bold">
    {sign && sign}
    {amount}{" "}
    <TermLink
      name="Talent"
      plural={amount !== 1}
      size={size}
      includeIcon
      hideText
    />
  </span>
)

export default TalentsAmount
