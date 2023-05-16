import { createTheme } from '@mui/material/styles';
import { merge } from 'lodash';
import {  } from '@mui/material/colors';

import rootTheme from "./rootTheme";
import './rootTheme';

const frameTheme = createTheme(merge({}, rootTheme, {
  palette: {
    primary: {
      main: "#FFFFFF" // white
    }
  },
}));

export default frameTheme;
