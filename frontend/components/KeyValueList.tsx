import ListItem from "@mui/material/ListItem";
import List from "@mui/material/List";
import Stack from "@mui/material/Stack";

interface KeyValueListProps {
  fields: {name: string, value: string}[];
  divider?: boolean;
  margin?: number;
}

const KeyValueList = (props: KeyValueListProps) => {
  return (
    <section>
      <List style={{ padding: 0 }}>
        {props.fields.map((field, index) => (
          <ListItem key={index}>
            <Stack spacing={1}>
              <div style={{ minWidth: "130px" }}><b>{field.name}</b></div>
              <div>{field.value ? field.value : "-"}</div>
            </Stack>
          </ListItem>
        ))}
      </List>
    </section>
  )
}

export default KeyValueList;
