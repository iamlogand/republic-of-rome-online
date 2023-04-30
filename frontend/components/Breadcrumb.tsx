import Link from "@/components/Link";
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
        if (matchingCustomItem)
        {
          return (
            <div key={index}>
              <span className={styles.noLink}>{matchingCustomItem.text}</span>
            </div>
          )

        } else if (index == routes.length - 1) {

          // Remove URL parameters
          const hashPosition = route.indexOf("#");
          if (hashPosition !== -1) {

            // It's important that URL parameters are removed because:
            // 1. They look bad and have no place in the breadcrumb
            // 2. They can cause SSR/CSR hydration issues, for some reason
            route = route.substring(0, hashPosition);
          }

          return (
            <div key={index}>
              <span className={`${styles.noLink} ${styles.titleCase}`}>{route}</span>
            </div>
          )

        } else {
          const targetRoutes = routes.slice(1).slice(0, index);
          const targetPath =  "/" + targetRoutes.join('/');

          return (
            <div key={index}>
              <Link href={targetPath} className={styles.titleCase}>{route}</Link>
              <span className={styles.slash}>/</span>
            </div>
          )
        }
      })}
    </nav>
  ) 
}

export default Breadcrumb;