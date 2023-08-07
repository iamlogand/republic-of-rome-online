import Image, { StaticImageData }  from 'next/image'
import chroma from "chroma-js";
import { useState } from 'react';

import FamilySenator from '@/classes/FamilySenator'
import Faction from '@/classes/Faction'
import styles from "./SenatorPortrait.module.css"

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
  faction: Faction
  clickable?: boolean
}

const SenatorPortrait = (props: SenatorPortraitProps) => {

  const [hover, setHover] = useState<boolean>(false)
  
  const getImageContainerStyle = () => {
    return {
      border: '2px solid' + props.faction.getColor(),
      height: 72, width: 72
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
    // Get size
    const size = 74

    // Get base background color
    let bgColor = ""
    if (hover) {
      bgColor = props.faction.getColor("bgHover")
    } else {
      bgColor = props.faction.getColor("bg")
    }

    // Manipulate color to make gradient background
    let innerBgColor = chroma(bgColor).brighten().hex()
    let outerBgColor = chroma(bgColor).darken().hex()
    
    // Return background style
    return {
      background: "radial-gradient(" + innerBgColor + ", " + outerBgColor + ")",
      height: size, width: size
    }
  }

  const handleMouseOver = () => {
    setHover(true)
  }

  const handleMouseLeave = () => {
    setHover(false)
  }

  return (
    <div className={styles.senatorPortrait} title={props.senator.name} onMouseOver={handleMouseOver} onMouseLeave={handleMouseLeave}>
      <figure style={{height: 80, width: 80}}>
        <div className={styles.imageContainer} style={getImageContainerStyle()}>
          <Image className={styles.picture} width={106} height={106} src={getPicture()} alt={"Portrait of " + props.senator.name} />
        </div>
        <div className={styles.bg} style={getBgStyle()}></div>
      </figure>
    </div>
  )
}

export default SenatorPortrait;