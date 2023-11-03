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
    error: {
      // Tailwind CSS Red
      light: "#ef4444", // 500
      main: "#dc2626", // 600
      dark: "#b91c1c", // 700
    },
    warning: {
      // Tailwind CSS Orange
      light: "#f97316", // 500
      main: "#ea580c", // 600
      dark: "#c2410c", // 700
    },
    info: {
      // Tailwind CSS Teal
      light: "#14b8a6", // 500
      main: "#0d9488", // 600
      dark: "#0f766e", // 700
    },
    success: {
      // Tailwind CSS Green
      light: "#22c55e", // 500
      main: "#16a34a", // 600
      dark: "#15803d", // 700
    },
  },
  components: {
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
          color: "inherit",
        },
      },
    },
  },
})

export default rootTheme
