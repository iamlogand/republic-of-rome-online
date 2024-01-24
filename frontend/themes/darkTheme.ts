import { createTheme } from "@mui/material/styles"
import rootTheme from "@/themes/rootTheme"
import {
  Stone100,
  Stone200,
  Stone300,
  Stone400,
  Stone500,
  Stone550,
  Stone700,
  Stone750,
  Stone800,
  Tyrian100,
  Tyrian200,
  Tyrian300,
} from "./themeColors"

let darkTheme
if (typeof window !== "undefined") {
  darkTheme = createTheme({
    ...rootTheme,
    palette: {
      primary: {
        light: Tyrian100,
        main: Tyrian200,
        dark: Tyrian300,
      },
      secondary: {
        light: Stone100,
        main: Stone200,
        dark: Stone300,
      },
    },
    components: {
      ...rootTheme.components,
      MuiTab: {
        styleOverrides: {
          root: {
            color: "#d6d3d1", // Tailwind CSS Stone 300
          },
        },
      },
      MuiAlert: {
        styleOverrides: {
          root: {
            ...(rootTheme.components?.MuiAlert?.styleOverrides?.root as object),
            // Tailwind CSS Stone
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
            "&:disabled": { color: Stone550 }, // Tailwind CSS Stone 550
          },
        },
      },
      MuiButton: {
        styleOverrides: {
          root: {
            "&:disabled": { color: Stone550 }, // Tailwind CSS Stone 550
          },
        },
      },
      MuiAvatar: {
        styleOverrides: {
          root: {
            backgroundColor: Stone750, // Tailwind CSS Stone 750
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
            color: Stone100, // Tailwind CSS Stone 100
          },
        },
      },
      MuiOutlinedInput: {
        styleOverrides: {
          root: {
            "&:hover:not(.Mui-focused) .MuiOutlinedInput-notchedOutline": {
              borderColor: Stone100, // Tailwind CSS Stone 100
            },
          },
          notchedOutline: {
            borderColor: Stone400, // Tailwind CSS Stone 400
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
} else {
  darkTheme = createTheme()
}

export default darkTheme
