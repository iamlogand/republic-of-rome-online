import { createTheme } from '@mui/material/styles';
import { merge } from 'lodash';

import rootTheme from "./rootTheme";
import './rootTheme';

const topBarTheme = createTheme(merge({}, rootTheme, {
  palette: {
    primary: {
      light: "#a3678a",  // Extra light
      main: "#843462",   // Light
      dark: "#66023C"    // Tyrian purple
    },
    info: {
      main: "#007185",   // Amazon link blue
    }
  },
  components: {
    MuiLink: {
      defaultProps: {
        color: "info.main",
      },
    }
  },
  helperText: {
    '&.Mui-error': {
      fontSize: "20px",
    },
  },
}));

export default topBarTheme;
