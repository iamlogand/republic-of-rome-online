import styles from "./Skill.module.css"
import skillsJSON from "@/data/skills.json"

interface SkillProps {
  name: "military" | "oratory" | "loyalty"
  value: number
}

// Colored box containing skill
const Skill = (props: SkillProps) => {
  console.log(props.name)
  console.log(skillsJSON.colors.number[props.name])
  return (
    <div className={styles.skill} style={{
      backgroundColor: skillsJSON.colors.number[props.name],
      boxShadow: `0px 0px 2px 2px ${skillsJSON.colors.number[props.name]}`
    }}>
      {props.value}
    </div>
  )
}

export default Skill
