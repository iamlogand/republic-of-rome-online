import Image from "next/image"
import { capitalize } from "@mui/material/utils"
import Faction from "@/classes/Faction"
import Secret from "@/classes/Secret"
import { useGameContext } from "@/contexts/GameContext"
import SecretsIcon from "@/images/icons/secrets.svg"
import TermLink from "@/components/TermLink"
import ConcessionTermLink from "@/components/ConcessionTermLink"

const SecretList = ({ faction }: { faction: Faction }) => {
  const { allSecrets } = useGameContext()

  const secrets = allSecrets.asArray.filter(
    (secret: Secret) => secret.faction === faction.id
  )

  const secretRenderer = (secret: Secret) => {
    if (!secret.name || !secret.type) return null

    const renderSecretType = (secret: Secret) => {
      if (secret.type === "concession") {
        return <TermLink name={capitalize(secret.type)} hiddenUnderline />
      }
      return capitalize(secret.type as string)
    }

    const renderSecretName = (secret: Secret) => {
      if (secret.type === "concession" && secret.name) {
        return (
          <ConcessionTermLink
            name={secret.name}
            size="large"
            includeIcon
            hiddenUnderline
          />
        )
      }
      return secret.name
    }

    return (
      <li
        key={secret.id}
        className="list-none border-2 border-solid border-purple-500 rounded p-4 px-5 bg-neutral-50 dark:bg-neutral-600 shadow-[inset_0_0_10px_2px_hsla(286,72%,60%,0.6)]"
      >
        <div className="flex flex-wrap justify-between gap-x-4 gap-y-2 text-sm">
          <div>{renderSecretType(secret)}</div>
          <div className="flex justify-end items-center gap-1 text-purple-600 dark:text-purple-300 my-[-6px]">
            <Image src={SecretsIcon} alt={"g"} width={26} height={26} />
            <i>Hidden from others</i>
          </div>
        </div>
        <div className="flex items-center text-lg mt-2">
          <b>{renderSecretName(secret)}</b>
        </div>
      </li>
    )
  }

  return (
    <ul className="flex flex-col gap-3 p-0 m-0 pb-4 box-border">
      {secrets.map((secret: Secret) => secretRenderer(secret))}
    </ul>
  )
}

export default SecretList
