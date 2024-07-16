import Collection from "@/classes/Collection"
import Senator from "@/classes/Senator"
import {
  FormControl,
  InputLabel,
  MenuItem,
  Select,
  SelectChangeEvent,
} from "@mui/material"

interface SenatorSelectorProps {
  senators: Collection<Senator>
  selectedSenator: Senator | null
  setSelectedSenator: (senator: Senator | null) => void
}

const SenatorSelector = ({
  senators,
  selectedSenator,
  setSelectedSenator,
}: SenatorSelectorProps) => {
  const handleChange = (event: SelectChangeEvent) => {
    const selectedSenator =
      senators.asArray.find(
        (senator) => senator.id === Number(event.target.value)
      ) ?? null
    setSelectedSenator(selectedSenator)
  }

  const sortedSenators = senators.asArray.sort((a, b) => a.displayName.localeCompare(b.displayName))

  return (
    <FormControl fullWidth>
      <InputLabel id={`select-senator-input-label`}>Assigned Senator</InputLabel>
      <Select
        labelId={`select-senator-input-label`}
        value={String(selectedSenator?.id ?? "None")}
        label="Assigned Senator"
        onChange={handleChange}
      >
        <MenuItem value="None">None</MenuItem>
        {sortedSenators.map((senator, index) => (
          <MenuItem key={index} value={senator.id}>
            {senator.displayName}
          </MenuItem>
        ))}
      </Select>
    </FormControl>
  )
}

export default SenatorSelector
