import { useEffect, useState } from 'react'
import Image, { StaticImageData }  from 'next/image'
import chroma from "chroma-js"

import FamilySenator from '@/classes/FamilySenator'
import Faction from '@/classes/Faction'
import styles from "./SenatorPortrait.module.css"
import Office from '@/classes/Office'
import OfficeIcon from '@/components/OfficeIcon'
import SelectedEntity from "@/types/selectedEntity"
import Colors from "@/data/colors.json"

import Cornelius from "@/images/portraits/cornelius.png"
import Fabius from "@/images/portraits/fabius.png"
import Valerius from "@/images/portraits/valerius.png"
import Julius from "@/images/portraits/julius.png"
import Claudius from "@/images/portraits/claudius.png"
import Manlius from "@/images/portraits/manlius.png"
import Fulvius from "@/images/portraits/fulvius.png"
import Furius from "@/images/portraits/furius.png"
import Aurelius from "@/images/portraits/aurelius.png"
import Junius from "@/images/portraits/junius.png"
import Papirius from "@/images/portraits/papirius.png"
import Acilius from "@/images/portraits/acilius.png"
import Flaminius from "@/images/portraits/flaminius.png"
import Aelius from "@/images/portraits/aelius.png"
import Sulpicius from "@/images/portraits/sulpicius.png"
import Calpurnius from "@/images/portraits/calpurnius.png"
import Plautius from "@/images/portraits/plautius.png"
import Quinctius from "@/images/portraits/quinctius.png"
import Aemilius from "@/images/portraits/aemilius.png"
import Terentius from "@/images/portraits/terentius.png"
import { useGameContext } from '@/contexts/GameContext'

const senatorImages: { [key: string]: StaticImageData } = {
  Cornelius: Cornelius,
  Fabius: Fabius,
  Valerius: Valerius,
  Julius: Julius,
  Claudius: Claudius,
  Manlius: Manlius,
  Fulvius: Fulvius,
  Furius: Furius,
  Aurelius: Aurelius,
  Junius: Junius,
  Papirius: Papirius,
  Acilius: Acilius,
  Flaminius: Flaminius,
  Aelius: Aelius,
  Sulpicius: Sulpicius,
  Calpurnius: Calpurnius,
  Plautius: Plautius,
  Quinctius: Quinctius,
  Aemilius: Aemilius,
  Terentius: Terentius,
};

interface SenatorPortraitProps {
  senator: FamilySenator
  size: number
  clickable?: boolean
}

const SenatorPortrait = (props: SenatorPortraitProps) => {
  const { allFactions, allOffices, setSelectedEntity } = useGameContext()

  // Faction that this senator is aligned to
  const [faction, setFaction] = useState<Faction | null>(null)
  useEffect(() => {
    setFaction(allFactions.asArray.find(f => f.id === props.senator.faction) ?? null)
  }, [allFactions, props.senator, setFaction])

  // Office held by this senator
  const [office, setOffice] = useState<Office | null>(null)
  useEffect(() => {
    setOffice(allOffices.asArray.find(o => o.senator === props.senator.id) ?? null)
  }, [allOffices, props.senator, setFaction])

  const [hover, setHover] = useState<boolean>(false)
  
  const getImageContainerStyle = () => {
    return {
      border: '2px solid' + (faction ? faction.getColor() : Colors.unaligned.primary),
      height: props.size - 8, width: props.size - 8
    }
  }

  // Use the name to get the correct image
  const getPicture = (): StaticImageData | string => {
    const senatorName = props.senator.name
    if (senatorImages.hasOwnProperty(senatorName)) {
      return senatorImages[senatorName]
    } else {
      return ""
    }
  }

  const getBgStyle = () => {
    // Get base background color

    let bgColor = ""
    if (faction) {
      if (hover) {
        bgColor = faction.getColor("bgHover")  // Background is brighter on mouse hover
      } else {
        bgColor = faction.getColor("bg")
      }
    } else {
      if (hover) {
        bgColor = Colors.unaligned.bgHover  // Background is brighter on mouse hover
      } else {
        bgColor = Colors.unaligned.bg
      }
    }

    // Manipulate color to make gradient background
    let innerBgColor = chroma(bgColor).brighten().hex()
    let outerBgColor = chroma(bgColor).darken().hex()
    
    // Return background style
    return {
      background: "radial-gradient(" + innerBgColor + ", " + outerBgColor + ")",
      height: props.size - 6, width: props.size - 6
    }
  }

  // Get number of pixels by which to increase image size, beyond container size
  const getZoom = () => {
    let zoom = 0
    if (props.size < 80) {
      zoom = 20
    } else if (props.size < 200) {
      zoom = (200 - props.size) / 4  // linear relationship
    }
    return zoom
  }

  // Get number of pixels by which to offset image downwards when zooming in, to focus on the face
  const getOffset = () => {
    let offset = 0
    if (props.size < 80) {
      offset = 10
    } else if (props.size < 200) {
      offset = (200 - props.size) / 12  // linear relationship
    }
    return offset
  }

  // Get the size of the office icon in pixels
  const getIconSize = () => {
    let size = 60
    if (props.size < 80) {
      size = 28
    } else if (props.size < 200) {
      size = (32 / 120) * (props.size - 80) + 28  // linear relationship
    }
    return size
  }

  const handleMouseOver = () => {
    if (props.clickable) setHover(true)
  }

  const handleMouseLeave = () => {
    setHover(false)
  }

  const handleClick = () => {
    if (props.clickable) setSelectedEntity({className: "FamilySenator", id: props.senator.id} as SelectedEntity)
  }

  return (
    <div className={styles.senatorPortrait} title={props.senator.name} onMouseOver={handleMouseOver} onMouseLeave={handleMouseLeave} onClick={handleClick}>
      <figure style={{height: props.size, width: props.size}}>
        <div className={styles.imageContainer} style={getImageContainerStyle()}>
          <Image className={styles.picture} width={props.size + getZoom()} height={props.size + getZoom()} src={getPicture()} alt={"Portrait of " + props.senator.name} style={{transform: `translate(-50%, -${50 - getOffset()}%)`}} />
        </div>
        <div className={styles.bg} style={getBgStyle()}></div>
        {office && <OfficeIcon office={office} size={getIconSize()} />}
      </figure>
    </div>
  )
}

export default SenatorPortrait;