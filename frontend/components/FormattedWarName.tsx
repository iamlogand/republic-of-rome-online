import War from "@/classes/War"
import getNumberSuffix from "@/functions/numberSuffix"

interface FormattedWarNameProps {
  war: War
}

// Display the formatted name of a war with its index superscripted
const FormattedWarName = ({ war }: FormattedWarNameProps) => (
  <span>
    {war.index > 0 && (
      <span>
        {war.index}
        <sup>{getNumberSuffix(war.index)}</sup>{" "}
      </span>
    )}
    {war.name} War
  </span>
)

export default FormattedWarName
