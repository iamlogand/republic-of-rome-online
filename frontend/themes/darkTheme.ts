import { createTheme } from "@mui/material/styles"
import rootTheme from "@/themes/rootTheme"
import {
  Red400,
  Red500,
  Red600,
  Green400,
  Green500,
  Green600,
  Neutral100,
  Neutral50,
  Neutral400,
  Neutral500,
  Neutral550,
  Neutral600,
  Neutral700,
  Neutral750,
  Neutral800,
  Tyrian100,
  Tyrian200,
  Tyrian300,
  Neutral900,
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
      light: "#ffffff",
      main: Neutral50,
      dark: Neutral100,
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
          backgroundColor: Neutral700,
          borderColor: Neutral800,
        },
      },
    },
    MuiIconButton: {
      styleOverrides: {
        root: {
          ...(rootTheme.components?.MuiIconButton?.styleOverrides
            ?.root as object),
          "&:disabled": { color: Neutral550 },
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          "&:disabled": { color: Neutral550 },
        },
      },
    },
    MuiAvatar: {
      styleOverrides: {
        root: {
          backgroundColor: Neutral700,
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
          color: Neutral100,
        },
      },
    },
    MuiOutlinedInput: {
      styleOverrides: {
        root: {
          "&:hover:not(.Mui-focused) .MuiOutlinedInput-notchedOutline": {
            borderColor: Neutral100,
          },
        },
        notchedOutline: {
          borderColor: Neutral400,
        },
      },
    },
    MuiPopover: {
      styleOverrides: {
        paper: {
          backgroundColor: Neutral600,
        },
      },
    },
    MuiDialog: {
      styleOverrides: {
        paper: {
          backgroundColor: Neutral700,
        },
      },
    },
    MuiDataGrid: {
      styleOverrides: {
        ...rootTheme.components?.MuiDataGrid?.styleOverrides,
        root: {
          ...rootTheme.components?.MuiDataGrid?.styleOverrides?.root,
          "& .MuiDataGrid-withBorderColor": {
            borderColor: Neutral500,
          },
        },
      },
    },
    MuiTooltip: {
      styleOverrides: {
        tooltip: {
          backgroundColor: Neutral900,
        },
        arrow: {
          color: Neutral900,
        },
      },
    },
    MuiListSubheader: {
      styleOverrides: {
        root: {
          ...(rootTheme.components?.MuiListSubheader?.styleOverrides
            ?.root as object),
          color: "inherit",
          backgroundColor: Neutral600,
        },
      },
    },
  },
})

export default darkTheme
