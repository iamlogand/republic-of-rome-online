import ListItem from "@mui/material/ListItem";
import List from "@mui/material/List";
import Stack from "@mui/material/Stack";

interface KeyValueListProps {
  pairs: {key: string, value: string}[];
  divider?: boolean;
  margin?: number;
}

const KeyValueList = (props: KeyValueListProps) => {
  return (
    <section>
      <List style={{ padding: 0 }}>
        {props.pairs.map((item, index) => (
          <ListItem key={index}>
            <Stack spacing={1}>
              <div style={{ minWidth: "130px" }}><b>{item.key}</b></div>
              <div>{item.value ? item.value : "-"}</div>
            </Stack>
          </ListItem>
        ))}
      </List>
    </section>
  )
}

export default KeyValueList;
