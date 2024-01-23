import { createTheme } from "@mui/material/styles"
import rootTheme from "@/themes/rootTheme"

const darkTheme = createTheme({
  ...rootTheme,
  palette: {
    primary: {
      // Custom Tyrian
      light: "hsl(313, 100%, 93%)", // 100
      main: "hsl(316, 80%, 85%)", // 200
      dark: "hsl(319, 60%, 75%)", // 300
    },
    secondary: {
      // Tailwind CSS Stone
      light: "white", // 100
      main: "#fafaf9", // 200
      dark: "#f5f5f4", // 300
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
          ...(rootTheme.components!.MuiAlert!.styleOverrides!.root as object),
          // Tailwind CSS Stone
          backgroundColor: "#44403c", // 700
          borderColor: "#353331", // 750
        },
      },
    },
    MuiIconButton: {
      styleOverrides: {
        root: {
          ...(rootTheme.components!.MuiIconButton!.styleOverrides!
            .root as object),
          "&:disabled": { color: "#67625d" }, // Tailwind CSS Stone 550
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          // ...(rootTheme.components!.MuiButton!.styleOverrides!.root as object),
          "&:disabled": { color: "#67625d" }, // Tailwind CSS Stone 500
        },
      },
    },
    MuiAvatar: {
      styleOverrides: {
        root: {
          backgroundColor: "#353331", // Tailwind CSS Stone 750
        },
      },
    },
  },
})

export default darkTheme
