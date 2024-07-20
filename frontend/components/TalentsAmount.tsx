import TermLink from "@/components/TermLink"

interface TalentsAmountProps {
  amount: number
  sign?: "+" | "-"
}

const TalentsAmount = ({ amount, sign }: TalentsAmountProps) => (
  <span className="text-nowrap font-bold">
    {sign && sign}
    {amount}{" "}
    <TermLink name="Talent" plural={amount !== 1} includeIcon hideText />
  </span>
)

export default TalentsAmount
