import Stack from "@mui/material/Stack"

interface KeyValueStackProps {
  fields: {name: string, value: string}[]
}

const KeyValueStack = (props: KeyValueStackProps) => {
  return (
    <section>
      <Stack padding={2} gap={3}>
        {props.fields.map((field, index) => (
          <Stack key={index} direction={{ xs: "column", sm: "row"}} gap={{ xs: 1, sm: 3 }}>
            <div style={{minWidth: "130px"}}><b>{field.name}</b></div>
            <div>{field.value}</div>
          </Stack>
        ))}
      </Stack>
    </section>
  )
}

export default KeyValueStack;
