import { RefObject, useEffect, useState } from "react"

import Collection from "@/classes/Collection"
import SenatorPortrait from "./senators/SenatorPortrait"
import FamilySenator from "@/classes/FamilySenator"
import GameParticipant from "@/classes/GameParticipant"
import Faction from "@/classes/Faction"

interface DetailSectionProps {
  senators: Collection<FamilySenator>
  factions: Collection<Faction>
  gameParticipants: Collection<GameParticipant>
  selectedEntity: SelectedEntity | null
  detailSectionRef: RefObject<HTMLDivElement>
}

// Detail section content for a senator
const SenatorDetailSection = (props: DetailSectionProps) => {
  const [senator, setSenator] = useState<FamilySenator | null>(null)
  const [faction, setFaction] = useState<Faction | null>(null)
  const [gameParticipant, setGameParticipant] = useState<GameParticipant | null>(null)
  
  // Get senator related data
  useEffect(() => {
    if (props.selectedEntity && props.selectedEntity.className === "FamilySenator") {
      setSenator(props.senators.asArray.find(s => s.id === props.selectedEntity?.id) ?? null)
      setFaction(props.factions.asArray.find(f => f.id === senator?.faction) ?? null)
      setGameParticipant(props.gameParticipants.asArray.find(p => p.id === faction?.player) ?? null)
    } else {
      setSenator(null)
      setFaction(null)
      setGameParticipant(null)
    }
  }, [props.selectedEntity, props.senators, props.factions, props.gameParticipants, faction?.player, senator?.faction])

  // Calculate senator portrait size.
  // Senator portrait size is determined by JavaScript rather than direct CSS,
  // so it necessary to do something like this to make the portrait responsive.
  const getPortraitSize = () => {
    const detailDivWidth = props.detailSectionRef.current?.offsetWidth
    if (detailDivWidth && detailDivWidth < 416) {
      return (detailDivWidth - 20) / 2
    } else {
      return 200
    }
  }
  
  if (faction && senator && gameParticipant) {
    const factionNameAndUser = `${faction.getName()} Faction (${gameParticipant.user?.username})`
    return (
      <>
        <SenatorPortrait senator={senator} faction={faction} size={getPortraitSize()}/>
        <div>
          <div><b>{senator!.name}</b></div>
          <div>{factionNameAndUser ? `Aligned to the ${factionNameAndUser}` : 'Unaligned'}</div>
        </div>
      </>
    )
  } else {
    return null
  }
}

export default SenatorDetailSection
