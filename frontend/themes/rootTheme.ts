import { createTheme } from "@mui/material/styles"
import "@mui/material/styles"
import {
  Red500,
  Red600,
  Red700,
  Green500,
  Green600,
  Green700,
  Neutral100,
  Neutral300,
  Neutral400,
  Neutral500,
  Neutral600,
  Tyrian500,
  Tyrian600,
  Tyrian700,
} from "./colors"

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
      light: Tyrian500,
      main: Tyrian600,
      dark: Tyrian700,
    },
    secondary: {
      light: Neutral400,
      main: Neutral500,
      dark: Neutral600,
    },
    success: {
      light: Green500,
      main: Green600,
      dark: Green700,
    },
    error: {
      light: Red500,
      main: Red600,
      dark: Red700,
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
          backgroundColor: Neutral100,
          borderColor: Neutral300,
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
    MuiCheckbox: {
      styleOverrides: {
        root: {
          color: "inherit",
        },
      },
    },
    MuiList: {
      styleOverrides: {
        root: {
          padding: 0,
        },
      },
    },
    MuiListItem: {
      styleOverrides: {
        root: {
          padding: 0,
        },
      },
    },
    MuiListSubheader: {
      styleOverrides: {
        root: {
          padding: 0,
        },
      },
    },
  },
})

export default rootTheme
