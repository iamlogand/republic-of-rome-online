import { useRef } from 'react'

import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faXmark } from '@fortawesome/free-solid-svg-icons'
import Button from '@mui/material/Button'

import styles from "./DetailSection.module.css"
import SenatorDetailSection from '@/components/detailSections/DetailSection_Senator'
import FactionDetailSection from '@/components/detailSections/DetailSection_Faction'
import { useGameContext } from '@/contexts/GameContext'
import HraoTerm from '@/components/terms/Term_Hrao'
import RomeConsulTerm from '@/components/terms/Term_RomeConsul'

// Section showing details about selected entities
const DetailSection = () => {
  const { selectedDetail, setSelectedDetail } = useGameContext()
  const detailSectionRef = useRef<HTMLDivElement>(null);
  
  if (!selectedDetail) return <div className={styles.nothing}><div>Nothing selected</div></div>

  // Get the component for the selected term
  const getTermDetails = () => {
    switch (selectedDetail.name) {
      case "HRAO": return <HraoTerm />
      case "Rome Consul": return <RomeConsulTerm />
    }
  }

  return (
    <div className={styles.detailSection}>
      <div className={styles.header}>
        <h3>Selected {selectedDetail.id ? selectedDetail.type : 'Term'}</h3>
        <Button onClick={() => setSelectedDetail(null)}>
          <FontAwesomeIcon icon={faXmark} fontSize={16} style={{marginRight: 8}} />Clear
        </Button>
      </div>
      <div ref={detailSectionRef} className={styles.detailSectionInner}>
        { selectedDetail.type === "Senator" &&
          <SenatorDetailSection detailSectionRef={detailSectionRef} />
        }
        { selectedDetail.type === "Faction" &&
          <FactionDetailSection />
        }
        { selectedDetail.type === "Term" &&
          getTermDetails()
        }
      </div>
    </div>
  )
}

export default DetailSection
