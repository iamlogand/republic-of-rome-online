import Image from 'next/image'

import RomeConsulIcon from '@/images/icons/romeConsul.svg'
import styles from "./Term.module.css"

// Information about the game term: Rome Consul
const RomeConsulTerm = () => {
  return (
    <div className={styles.termDetail}>
      <div className={styles.iconAndTitle}>
        <Image src={RomeConsulIcon} height={70} width={70} alt={`HRAO Icon`} />
        <h4><b>Rome Consul</b></h4>
      </div>
      <div className={styles.textContainer}>
        <p>
          The Rome Consulship is the second highest ranking office, after the Dictator (if there is one).
        </p>
        <p>
          After being elected, the Rome Consul will become the Presiding Magistrate in the Senate. This makes the Rome Consulship one of the most powerful offices.
        </p>
      </div>
    </div>
  )
}

export default RomeConsulTerm
