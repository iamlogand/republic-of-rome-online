import Image from "next/image"
import { capitalize } from "@mui/material/utils"
import Faction from "@/classes/Faction"
import Secret from "@/classes/Secret"
import { useGameContext } from "@/contexts/GameContext"
import SecretsIcon from "@/images/icons/secrets.svg"
import TermLink from "./TermLink"

const SecretList = ({ faction }: { faction: Faction }) => {
  const { allSecrets } = useGameContext()

  const secrets = allSecrets.asArray.filter(
    (secret: Secret) => secret.faction === faction.id
  )

  const secretRenderer = (secret: Secret) => {
    if (!secret.name || !secret.type) return null

    const renderSecret = () => {
      if (!secret.name) return null
      if (secret.type === "concession") {
        if (secret.name.endsWith("Tax Farmer")) {
          return (
            <TermLink
              name="Tax Farmer"
              displayName={secret.name}
              hiddenUnderline
            />
          )
        }
        if (secret.name.endsWith("Grain")) {
          return (
            <TermLink name="Grain" displayName={secret.name} hiddenUnderline />
          )
        }
        return <TermLink name={secret.name} hiddenUnderline />
      }
      return secret.name
    }

    const secretTypeTermLink = (secret: Secret) => {
      if (secret.type === "concession") {
        return <TermLink name={capitalize(secret.type)} hiddenUnderline />
      }
      return capitalize(secret.type as string)
    }

    return (
      <li
        key={secret.id}
        className="list-none border-2 border-solid border-purple-500 rounded p-4 px-5 bg-neutral-50 dark:bg-neutral-600 shadow-[inset_0_0_10px_2px_hsla(286,72%,60%,0.6)]"
      >
        <div className="flex flex-wrap justify-between gap-x-4 gap-y-2 text-sm">
          <div>{secretTypeTermLink(secret)}</div>
          <div className="flex justify-end items-center gap-1 text-purple-600 dark:text-purple-300 my-[-6px]">
            <Image src={SecretsIcon} alt={"g"} width={26} height={26} />
            <i>Hidden from others</i>
          </div>
        </div>
        <div className="flex items-center text-lg mt-2">
          <b>{renderSecret()}</b>
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
