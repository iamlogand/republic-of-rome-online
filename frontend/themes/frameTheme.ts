import { createTheme } from "@mui/material/styles"
import { merge } from "lodash"
import {} from "@mui/material/colors"

import rootTheme from "./rootTheme"
import "./rootTheme"

// Theme for top bar and footer
const frameTheme = createTheme(
  merge({}, rootTheme, {
    palette: {
      
    },
  })
)

export default frameTheme
