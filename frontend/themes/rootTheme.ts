import { createTheme } from '@mui/material/styles';
import '@mui/material/styles';

declare module '@mui/material/styles' {
  interface Theme {
    status: {
      danger: string;
    };
  }
  interface ThemeOptions {
    status?: {
      danger?: string;
    };
  }
}

const rootTheme = createTheme({
  typography: {
    fontFamily: 'inherit',
    button: {
      textTransform: 'none',
      fontSize: 'inherit'
    }
  }
});

export default rootTheme;
