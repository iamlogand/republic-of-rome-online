import VisibilityOffIcon from "@mui/icons-material/VisibilityOff"
import Faction from "@/classes/Faction"
import Secret from "@/classes/Secret"
import { useGameContext } from "@/contexts/GameContext"
import { capitalize } from "@mui/material/utils"

const SecretList = ({ faction }: { faction: Faction }) => {
  const { allSecrets } = useGameContext()

  const secrets = allSecrets.asArray.filter(
    (secret: Secret) => secret.faction === faction.id
  )

  const secretRenderer = (secret: Secret) => {
    if (!secret.name || !secret.type) return null

    return (
      <li
        key={secret.id}
        className="list-none border-2 border-solid border-red-600 dark:border-red-500 rounded p-4 px-5 bg-neutral-50 dark:bg-neutral-600 shadow-[inset_0_0_10px_2px_hsla(0,72%,60%,0.6)]"
      >
        <div className="flex flex-wrap justify-between gap-x-4 gap-y-2 text-sm">
          <div>{capitalize(secret.type as string)}</div>
          <div className="flex justify-end items-center gap-1 text-red-600 dark:text-red-500">
            <VisibilityOffIcon fontSize="small" /> <i>Hidden from others</i>
          </div>
        </div>
        <div className="flex items-center text-lg mt-2">
          <b>{secret.name}</b>
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
