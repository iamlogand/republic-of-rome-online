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

  return (
    <ul className="flex flex-col gap-3 p-0 m-0">
      {secrets.map((secret: Secret) => (
        <li
          key={secret.id}
          className="list-none border border-solid border-red-600 rounded p-4 px-5 bg-stone-50 shadow-[inset_0_0_10px_0px_hsla(0,72%,51%,0.5)]"
        >
          <div className="flex flex-wrap justify-between gap-x-4 gap-y-2 text-sm">
            <div>{capitalize(secret.type as string)} Secret</div>
            <div className="flex justify-end items-center gap-1 text-red-600">
              <VisibilityOffIcon fontSize="small" /> <i>Hidden from others</i>
            </div>
          </div>
          <div className="flex items-center text-lg mt-2">
            <b>{secret.name}</b>
          </div>
        </li>
      ))}
    </ul>
  )
}

export default SecretList
