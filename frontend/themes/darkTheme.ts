import { createTheme } from "@mui/material/styles"
import rootTheme from "@/themes/rootTheme"
import {
  Red400,
  Red500,
  Red600,
  Green400,
  Green500,
  Green600,
  Stone100,
  Stone50,
  Stone400,
  Stone500,
  Stone550,
  Stone600,
  Stone700,
  Stone750,
  Stone800,
  Tyrian100,
  Tyrian200,
  Tyrian300,
} from "./colors"

const darkTheme = createTheme({
  ...rootTheme,
  palette: {
    primary: {
      light: Tyrian100,
      main: Tyrian200,
      dark: Tyrian300,
    },
    secondary: {
      light: "white",
      main: Stone50,
      dark: Stone100,
    },
    success: {
      light: Green400,
      main: Green500,
      dark: Green600,
    },
    error: {
      light: Red400,
      main: Red500,
      dark: Red600,
    },
  },
  components: {
    ...rootTheme.components,
    MuiTab: {
      styleOverrides: {
        root: {
          color: "#d6d3d1",
        },
      },
    },
    MuiAlert: {
      styleOverrides: {
        root: {
          ...(rootTheme.components?.MuiAlert?.styleOverrides?.root as object),
          backgroundColor: Stone700,
          borderColor: Stone800,
        },
      },
    },
    MuiIconButton: {
      styleOverrides: {
        root: {
          ...(rootTheme.components?.MuiIconButton?.styleOverrides
            ?.root as object),
          "&:disabled": { color: Stone550 },
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          "&:disabled": { color: Stone550 },
        },
      },
    },
    MuiAvatar: {
      styleOverrides: {
        root: {
          backgroundColor: Stone750,
        },
      },
    },
    MuiLink: {
      defaultProps: {
        color: "primary.main",
      },
    },
    MuiInputLabel: {
      styleOverrides: {
        root: {
          color: Stone100,
        },
      },
    },
    MuiOutlinedInput: {
      styleOverrides: {
        root: {
          "&:hover:not(.Mui-focused) .MuiOutlinedInput-notchedOutline": {
            borderColor: Stone100,
          },
        },
        notchedOutline: {
          borderColor: Stone400,
        },
      },
    },
    MuiPopover: {
      styleOverrides: {
        paper: {
          backgroundColor: Stone600,
        },
      },
    },
    MuiDialog: {
      styleOverrides: {
        paper: {
          backgroundColor: Stone600,
        },
      },
    },
    MuiDataGrid: {
      styleOverrides: {
        ...rootTheme.components?.MuiDataGrid?.styleOverrides,
        root: {
          ...rootTheme.components?.MuiDataGrid?.styleOverrides?.root,
          "& .MuiDataGrid-withBorderColor": {
            borderColor: Stone500,
          },
        },
      },
    },
  },
})

export default darkTheme
