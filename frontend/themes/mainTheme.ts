import { createTheme } from "@mui/material/styles"
import { merge } from "lodash"

import rootTheme from "./rootTheme"
import "./rootTheme"

const topBarTheme = createTheme(
  merge({}, rootTheme, {
    components: {
      MuiLink: {
        defaultProps: {
          color: "primary.dark",
        },
      },
    },
    helperText: {
      "&.Mui-error": {
        fontSize: "20px",
      },
    },
  })
)

export default topBarTheme
