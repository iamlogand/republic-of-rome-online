import { createTheme } from "@mui/material/styles"
import "@mui/material/styles"
import {
  Stone100,
  Stone300,
  Stone400,
  Stone500,
  Stone600,
  Tyrian500,
  Tyrian600,
  Tyrian700,
} from "./themeColors"

// Custom '@mui/material/styles' module declaration
declare module "@mui/material/styles" {
  interface Theme {
    status: {
      danger: string
    }
  }
  interface ThemeOptions {
    status?: {
      danger?: string
    }
  }
  interface Components {
    MuiDataGrid?: any // MuiDataGrid is not typed in '@mui/material/styles'
  }
}

/* Frequently used colors */

const rootTheme = createTheme({
  typography: {
    fontFamily: "var(--font-open-sans)",
    button: {
      textTransform: "none",
      fontSize: "inherit",
    },
  },
  palette: {
    primary: {
      // Custom Tyrian
      light: Tyrian500,
      main: Tyrian600,
      dark: Tyrian700,
    },
    secondary: {
      // Tailwind CSS Stone
      light: Stone400,
      main: Stone500,
      dark: Stone600,
    },
  },
  components: {
    MuiLink: {
      defaultProps: {
        color: "primary",
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          color: "inherit",
        },
      },
    },
    MuiInputBase: {
      styleOverrides: {
        root: {
          color: "inherit",
        },
      },
    },
    MuiTablePagination: {
      styleOverrides: {
        root: {
          color: "inherit",
        },
      },
    },
    MuiDataGrid: {
      styleOverrides: {
        root: {
          color: "inherit",
          border: "none",
        },
      },
    },
    MuiAlert: {
      styleOverrides: {
        root: {
          borderWidth: "1px",
          borderStyle: "solid",
          color: "inherit",
          backgroundColor: Stone100,
          borderColor: Stone300,
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          color: "inherit",
        },
      },
    },
    MuiIconButton: {
      styleOverrides: {
        root: {
          color: "inherit",
        },
      },
    },
    MuiSvgIcon: {
      styleOverrides: {
        root: {
          color: "inherit",
        },
      },
    },
    MuiSelect: {
      styleOverrides: {
        icon: {
          color: "inherit",
        },
      },
    },
  },
})

export default rootTheme
