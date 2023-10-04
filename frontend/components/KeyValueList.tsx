import ListItem from "@mui/material/ListItem"
import List from "@mui/material/List"
import Stack from "@mui/material/Stack"
import Skeleton from "@mui/material/Skeleton"

interface KeyValueListProps {
  pairs: { key: string; value: string }[]
  divider?: boolean
  margin?: number
  skeletonItems?: number
}

// Skeleton for representing items that haven't loaded yet
const SkeletonItem = () => (
  <ListItem>
    <Stack spacing={1}>
      <Skeleton variant="rounded" sx={{ height: "22px", width: "80px" }} />
      <Skeleton variant="rounded" sx={{ height: "22px", width: "100px" }} />
    </Stack>
  </ListItem>
)

const KeyValueList = (props: KeyValueListProps) => {
  return (
    <section>
      <List style={{ padding: 0 }}>
        {props.pairs.map((item, index) => (
          <ListItem key={index}>
            <Stack spacing={1}>
              <div style={{ minWidth: "130px" }}>
                <b>{item.key}</b>
              </div>
              <div>{item.value ? item.value : "-"}</div>
            </Stack>
          </ListItem>
        ))}
        {Array.from({ length: props.skeletonItems ?? 0 }, (_, i) => (
          <SkeletonItem key={i} />
        ))}
      </List>
    </section>
  )
}

export default KeyValueList
