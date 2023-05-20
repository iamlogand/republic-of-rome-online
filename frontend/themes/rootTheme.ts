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
        root?: {
          color: string;
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
    MuiTablePagination: {
      styleOverrides: {
        root: {
          color: 'inherit'
        }
      }
    },
    MuiDataGrid: {
      styleOverrides: {
        root: {
          color: 'inherit'
        }
      }
    }
  }
});

export default rootTheme;
