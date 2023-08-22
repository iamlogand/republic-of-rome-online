import { useEffect, useState } from "react"
import styles from "./Skill.module.css"

interface SkillProps {
  name: "Military" | "Oratory" | "Loyalty"
  value: number
}

// Colored box containing skill
const Skill = (props: SkillProps) => {
  const [color, setColor] = useState<string>("")

  useEffect(() => {
    switch (props.name) {
      case "Military":
        setColor("#ff4c4c")
        break
      case "Oratory":
        setColor("#4cc44c")
        break
      case "Loyalty":
        setColor("#4c98ff")
        break
    }
  }, [props.name])

  return (
    <div className={styles.skill} style={{
      backgroundColor: color,
      boxShadow: `0px 0px 2px 2px ${color}`
    }}>
      {props.value}
    </div>
  )
}

export default Skill
