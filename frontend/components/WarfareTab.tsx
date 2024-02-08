import { useGameContext } from "@/contexts/GameContext"
import { capitalize } from "@mui/material/utils"

const WarfareTab = () => {
  const { wars } = useGameContext()

  return (
    <div className="m-4">
      <h2>Wars</h2>
      <ul>
        {wars.asArray.map((war) => (
          <li key={war.id}>
            <div>
              <p>{war.getName()} ({capitalize(war.status)})</p>
            </div>
          </li>
        ))}
      </ul>
    </div>
  )
}

export default WarfareTab
