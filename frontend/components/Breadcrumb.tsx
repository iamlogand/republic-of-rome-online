import Link from 'next/link';
import MuiLink from "@mui/material/Link";
import { useRouter } from "next/router";
import styles from "./Breadcrumb.module.css";

// A custom item is an override of the default value of a Breadcrumb item.
// Breadcrumb assumes that custom items will not be links.
export interface CustomItem {
  index: number;
  text: string;
}

const Breadcrumb = ({customItems}: {customItems?: CustomItem[]}) => {
  const router = useRouter();
  
  const path: string = router.asPath;
  let routes = ['']
  if (path != '/') {
    routes = path.split('/')
  }
  routes[0] = ('home');
  
  return (
    <nav className={styles.breadcrumb}>
      {routes.map((route, index) => {

        const matchingCustomItem = customItems?.find((item) => item.index == index)


        if (index == routes.length - 1) {

          // Remove URL parameters
          const hashPosition = route.indexOf("#");
          if (hashPosition !== -1) {

            // It's important that URL parameters are removed because:
            // 1. They look bad and have no place in the breadcrumb
            // 2. They can cause SSR/CSR hydration issues, for some reason
            route = route.substring(0, hashPosition);
          }
          if (matchingCustomItem) {
            return (
              <div key={index}>
                <span>{matchingCustomItem.text}</span>
              </div>
            )
          } else {
            return (
              <div key={index}>
                <span style={{textTransform: "capitalize"}}>{route}</span>
              </div>
            )
          }

        } else {
          const targetRoutes = routes.slice(1).slice(0, index);
          const targetPath =  "/" + targetRoutes.join('/');
          if (matchingCustomItem) {
            return (
              <div key={index}>
                <MuiLink component={Link} href={targetPath}>{matchingCustomItem.text}</MuiLink>
                <span style={{marginLeft: "10px", marginRight: "10px", userSelect: "none"}}>/</span>
              </div>
            )
          } else { 
            return (
              <div key={index}>
                <MuiLink component={Link} href={targetPath} style={{textTransform: "capitalize"}}>{route}</MuiLink>
                <span style={{marginLeft: "10px", marginRight: "10px", userSelect: "none"}}>/</span>
              </div>
            )
          }
        }
      })}
    </nav>
  ) 
}

export default Breadcrumb;