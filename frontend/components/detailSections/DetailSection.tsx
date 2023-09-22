import { useRef } from 'react'

import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faXmark } from '@fortawesome/free-solid-svg-icons'
import Button from '@mui/material/Button'

import styles from "./DetailSection.module.css"
import SenatorDetailSection from '@/components/detailSections/DetailSection_Senator'
import FactionDetailSection from '@/components/detailSections/DetailSection_Faction'
import { useGameContext } from '@/contexts/GameContext'

// Section showing details about selected entities
const DetailSection = () => {
  const { selectedEntity, setSelectedEntity } = useGameContext()
  const detailSectionRef = useRef<HTMLDivElement>(null);
  
  if (!selectedEntity) return <div className={styles.nothing}><div>Nothing selected</div></div>

  return (
    <div className={styles.detailSection}>
      <div className={styles.header}>
        <h3>Selected {selectedEntity?.className}</h3>
        <Button onClick={() => setSelectedEntity(null)}>
          <FontAwesomeIcon icon={faXmark} fontSize={16} style={{marginRight: 8}} />Clear
        </Button>
      </div>
      <div ref={detailSectionRef} className={styles.detailSectionInner}>
        { selectedEntity.className === "Senator" &&
          <SenatorDetailSection detailSectionRef={detailSectionRef} />
        }
        { selectedEntity.className === "Faction" &&
          <FactionDetailSection />
        }
      </div>
    </div>
  )
}

export default DetailSection
