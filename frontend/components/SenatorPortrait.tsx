import { useState } from "react"
import Image, { StaticImageData } from "next/image"
import { Tooltip } from "@mui/material"

import Senator from "@/classes/Senator"
import Faction from "@/classes/Faction"
import Title from "@/classes/Title"
import TitleIcon from "@/components/TitleIcon"
import SelectedDetail from "@/types/SelectedDetail"
import factionColors from "@/data/factionColors.json"
import FactionLeaderPattern from "@/images/patterns/factionLeader.svg"
import DeadIcon from "@/images/icons/dead.svg"
import { useGameContext } from "@/contexts/GameContext"
import Collection from "@/classes/Collection"
import SenatorSummary from "@/components/entitySummaries/SenatorSummary"

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

// Map of senator names to images
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
}

interface SenatorPortraitProps {
  senator: Senator
  size: number
  selectable?: boolean
  summary?: boolean
  blurryPlaceholder?: boolean
  round?: boolean
}

// The senator portrait is a visual representation of the senator,
// containing an image of their face, faction color background, and other status icons
const SenatorPortrait = ({
  senator,
  size,
  selectable,
  summary,
  blurryPlaceholder,
  round,
}: SenatorPortraitProps) => {
  const {
    allFactions,
    allTitles,
    selectedDetail,
    setSelectedDetail,
    setDialog,
  } = useGameContext()

  // Get senator-specific data
  const faction: Faction | null = senator.faction
    ? allFactions.byId[senator.faction] ?? null
    : null
  const titles: Collection<Title> = new Collection<Title>(
    allTitles.asArray.filter((t) => t.senator === senator.id)
  )
  const majorOffice: Title | null =
    titles.asArray.find((t) => t.major_office === true) ?? null
  const factionLeader: boolean = titles.asArray.some(
    (t) => t.name === "Faction Leader"
  )

  // Used to track whether the mouse is hovering over the portrait
  const [hover, setHover] = useState<boolean>(false)

  // Get style for the image container
  const getImageContainerStyle = () => {
    let bgColor = factionColors.none[500]
    if (faction) {
      bgColor = faction.getColor(400)
    } else if (senator.alive) {
      bgColor = factionColors.none[100]
    }

    return {
      border: "2px solid " + bgColor,
      height: size - 8,
      width: size - 8,
      borderRadius: round ? "50%" : "2px",
    }
  }

  // Use the name to get the correct image
  const getImageSource = (): StaticImageData | string => {
    const senatorName = senator.name
    if (senatorImages.hasOwnProperty(senatorName)) {
      return senatorImages[senatorName]
    } else {
      return ""
    }
  }

  // Get style for the background square
  const getBgStyle = () => {
    // Get background colors
    let innerBgColor = ""
    let outerBgColor = ""
    if (faction && senator.alive) {
      if (hover) {
        innerBgColor = faction.getColor(100)
        outerBgColor = faction.getColor(500)
      } else {
        innerBgColor = faction.getColor(300)
        outerBgColor = faction.getColor(600)
      }
    } else if (senator.alive) {
      if (hover) {
        innerBgColor = factionColors.none[50]
        outerBgColor = factionColors.none[300]
      } else {
        innerBgColor = factionColors.none[200]
        outerBgColor = factionColors.none[400]
      }
    } else {
      if (hover) {
        innerBgColor = factionColors.none[300]
        outerBgColor = factionColors.none[600]
      } else {
        innerBgColor = factionColors.none[400]
        outerBgColor = factionColors.none[700]
      }
    }

    // Return background style
    return {
      background: "radial-gradient(" + innerBgColor + ", " + outerBgColor + ")",
      height: size - 6,
      width: size - 6,
      borderRadius: round ? "50%" : 4,
    }
  }

  // Get number of pixels by which to increase image size, beyond container size
  const getZoom = () => {
    let zoom = 0
    if (size < 80) {
      zoom = 20
    } else if (size < 200) {
      zoom = (200 - size) / 4 // linear relationship
    }
    return zoom
  }

  // Get number of pixels by which to offset image downwards when zooming in, to focus on the face
  const getOffset = () => {
    let offset = 0
    if (size < 80) {
      offset = 10
    } else if (size < 200) {
      offset = (200 - size) / 12 // linear relationship
    }
    return offset
  }

  // Get the size of the title icon in pixels
  const getIconSize = () => {
    let iconSize = 60
    if (size < 80) {
      iconSize = 28
    } else if (size < 200) {
      iconSize = (32 / 120) * (size - 80) + 28 // linear relationship
    }
    return iconSize
  }

  // Handle mouse interactions
  const handleMouseOver = () => {
    if (selectable) setHover(true)
  }
  const handleMouseLeave = () => {
    setHover(false)
  }
  const handleClick = () => {
    if (selectable) {
      setSelectedDetail({ type: "Senator", id: senator.id } as SelectedDetail)
    }
    setDialog(null)
  }

  const showIcons = size > 70

  const renderButton = () =>
    selectable ? (
      <button
        className="absolute top-0 left-0 h-full w-full z-50 cursor-pointer select-none border-none p-0 bg-transparent"
        style={{
          borderRadius: round ? "50%" : 4,
        }}
        onMouseOver={handleMouseOver}
        onMouseLeave={handleMouseLeave}
        onClick={handleClick}
      />
    ) : (
      <div className="absolute top-0 left-0 h-full w-full z-50"></div>
    )

  return (
    <div>
      <figure
        style={{
          height: size,
          width: size,
          borderRadius: round ? "50%" : 4,
        }}
        className="relative flex justify-center items-center box-border bg-neutral-700 dark:bg-black"
      >
        <div
          className="absolute z-10 overflow-hidden left-1/2 top-1/2 translate-x-[-50%] translate-y-[-50%]"
          style={getImageContainerStyle()}
        >
          {selectable &&
            selectedDetail?.type === "Senator" &&
            selectedDetail?.id === senator.id && (
              <div
                className={`absolute w-full h-full z-30 shadow-[inset_0_0_6px_4px_white]`}
                style={{ borderRadius: round ? "50%" : 0 }}
              ></div>
            )}
          {factionLeader && (
            <Image
              src={FactionLeaderPattern}
              className="absolute h-auto w-full top-0 left-0"
              alt="Faction Leader pattern"
            />
          )}
          <Image
            className={`absolute z-10 left-1/2 top-1/2 ${
              senator.alive ? "" : "grayscale-[80%]"
            }`}
            width={size + getZoom()}
            height={size + getZoom()}
            src={getImageSource()}
            alt={"Portrait of " + senator.displayName}
            style={{ transform: `translate(-50%, -${50 - getOffset()}%)` }}
            placeholder={blurryPlaceholder ? "blur" : "empty"}
            unoptimized
          />
        </div>
        <div className="absolute" style={getBgStyle()}></div>
        {majorOffice && showIcons && (
          <TitleIcon
            title={majorOffice}
            size={getIconSize()}
            dead={!senator.alive}
            round={round}
          />
        )}
        {!round && (
          <>
            {senator.alive === false && showIcons && (
              <Image
                src={DeadIcon}
                alt="Skull and crossbones icon"
                height={getIconSize()}
                width={getIconSize()}
                className="absolute right-[3px] bottom-[3px] z-20 box-border"
              />
            )}
            {size > 120 && (
              <Tooltip title="Senator ID" arrow>
                <div className="absolute z-40 bottom-1 px-[6px] py-0.5 text-sm text-white bg-[rgba(0,_0,_0,_0.4)] user-none">
                  # {senator.code}
                </div>
              </Tooltip>
            )}
          </>
        )}
        {summary ? (
          <SenatorSummary senator={senator}>
            <div style={{ height: size, width: size }}>{renderButton()}</div>
          </SenatorSummary>
        ) : (
          renderButton()
        )}
      </figure>
    </div>
  )
}

export default SenatorPortrait
