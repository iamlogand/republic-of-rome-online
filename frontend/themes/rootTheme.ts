import { createTheme } from '@mui/material/styles';
import '@mui/material/styles';

// Custom '@mui/material/styles' module declaration
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
  interface Components {
    MuiDataGrid?: {
      styleOverrides?: {
        menu?: {
          fontFamily: string;
        };
      };
    };
  }
}

const rootTheme = createTheme({
  typography: {
    fontFamily: 'var(--font-open-sans)',
    button: {
      textTransform: 'none',
      fontSize: 'inherit'
    }
  },
  components: {
    MuiPaper: {
      styleOverrides: {
        root: {
          color: 'inherit'
        }
      }
    },
    MuiInputBase: {
      styleOverrides: {
        root: {
          color: 'inherit'
        }
      }
    },
    MuiPopover: {
      styleOverrides: {
        root: {
          fontFamily: '"Open Sans", sans-serif'
        }
      }
    },
    MuiDataGrid: {
      styleOverrides: {
        menu: {
          fontFamily: '"Open Sans", sans-serif'
        }
      }
    },
    MuiTooltip: {
      styleOverrides: {
        tooltip: {
          fontFamily: '"Open Sans", sans-serif'
        }
      }
    }
  }
});

export default rootTheme;
