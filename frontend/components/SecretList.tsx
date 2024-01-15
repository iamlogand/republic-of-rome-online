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
    <div className="flex flex-col gap-2">
      {secrets.map((secret: Secret) => (
        <p>
          <b>{capitalize(secret.type as string)}</b>: {secret.name}
        </p>
      ))}
    </div>
  )
}

export default SecretList
