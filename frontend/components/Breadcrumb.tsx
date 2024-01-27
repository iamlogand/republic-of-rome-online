import Link from "next/link"
import MuiLink from "@mui/material/Link"
import { useRouter } from "next/router"

// A custom item is an override of the default value of a Breadcrumb item.
// Breadcrumb assumes that custom items will not be links.
export interface CustomItem {
  index: number
  text: string
}

const Breadcrumb = ({ customItems }: { customItems?: CustomItem[] }) => {
  const router = useRouter()

  const path: string = router.asPath.split("?")[0]
  const pathName: string = router.pathname
  const routes = ["home"]
  if (path != "/") {
    const splitPath = path.split("/")
    const splitPathName = pathName.split("/")

    for (let i = 1; i < splitPath.length; i++) {
      const routeFromPath = splitPath[i]
      const routeFromPathName = splitPathName[i]
      if (routeFromPath.startsWith("[") && routeFromPath.endsWith("]")) {
        routes.push(routeFromPathName)
      } else {
        routes.push(routeFromPath)
      }
    }
  }

  return (
    <nav className="flex flex-wrap my-4">
      {routes.map((route, index) => {
        const matchingCustomItem = customItems?.find(
          (item) => item.index == index
        )

        if (index == routes.length - 1) {
          if (matchingCustomItem) {
            return (
              <div key={index}>
                <span>{matchingCustomItem.text}</span>
              </div>
            )
          } else {
            return (
              <div key={index}>
                <span style={{ textTransform: "capitalize" }}>{route}</span>
              </div>
            )
          }
        } else {
          const targetRoutes = routes.slice(1).slice(0, index)
          const targetPath = "/" + targetRoutes.join("/")
          if (matchingCustomItem) {
            return (
              <div key={index}>
                <MuiLink component={Link} href={targetPath}>
                  {matchingCustomItem.text}
                </MuiLink>
                <span className="mx-2 user-select-none">/</span>
              </div>
            )
          } else {
            return (
              <div key={index}>
                <MuiLink
                  component={Link}
                  href={targetPath}
                  style={{ textTransform: "capitalize" }}
                >
                  {route}
                </MuiLink>
                <span className="mx-2 user-select-none">/</span>
              </div>
            )
          }
        }
      })}
    </nav>
  )
}

export default Breadcrumb
