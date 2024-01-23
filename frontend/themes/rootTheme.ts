import { createTheme } from "@mui/material/styles"
import "@mui/material/styles"

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
    MuiDataGrid?: {
      styleOverrides?: {
        root?: {
          color: string
        }
      }
    }
  }
}

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
      light: "hsl(322, 50%, 65%)", // 400
      main: "hsl(325, 40%, 50%)", // 500
      dark: "hsl(328, 50%, 40%)", // 600
    },
    secondary: {
      // Tailwind CSS Stone
      light: "#a8a29e", // 400
      main: "#78716c", // 500
      dark: "#57534e", // 600
    },
  },
  components: {
    MuiLink: {
      defaultProps: {
        color: "primary.dark",
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
        },
      },
    },
    MuiAlert: {
      styleOverrides: {
        root: {
          borderWidth: "1px",
          borderStyle: "solid",
          color: "inherit",
          // Tailwind CSS Stone
          backgroundColor: "#f5f5f4", // 100
          borderColor: "#d6d3d1", // 300
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
  },
})

export default rootTheme
