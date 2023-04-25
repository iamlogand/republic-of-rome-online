import Link from "next/link";
import { useRouter } from "next/router";
import styles from "./Breadcrumb.module.css";
import linkStyles from "@/styles/link.module.css"
import { useRef } from "react";

const Breadcrumb = () => {
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

        if (index == routes.length - 1) {
          return (
            <div key={index}>
              <span className={`${styles.thisPage} ${styles.item}`}>{route}</span>
            </div>
          )
        } else {
          const targetRoutes = routes.slice(1).slice(0, index);
          const targetPath =  "/" + targetRoutes.join('/');

          return (
            <div key={index}>
              <Link href={targetPath} className={`${linkStyles.link} ${styles.item}`}>{route}</Link>
              <span className={styles.slash}>/</span>
            </div>
          )
        }
      })}
    </nav>
  ) 
}

export default Breadcrumb;