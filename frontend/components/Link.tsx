import { ReactNode } from "react";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faExternalLink } from '@fortawesome/free-solid-svg-icons'
import linkStyles from "./Link.module.css";
import NextLink from "next/link";

interface LinkProps {
  href: string;
  children: ReactNode;
  className?: string;
  inheritStyle?: boolean;
  [key: string]: any;
}

/**
 * For rendering internal and external links.
 */
const Link = (props: LinkProps) => {

  const { href, children, className, inheritStyle, ...rest } = props;

  const attributes: {[key: string]: any} = {};

  attributes.className = linkStyles.link;
  if (className) {
    attributes.className += ' ' + className;
  } else if (inheritStyle) {
    attributes.className = linkStyles.inheritStyle;
  }

  if (href.startsWith("https")) {
    return (
      <a href={href} target="_blank" {...attributes}>
        {children}
        <FontAwesomeIcon icon={faExternalLink} style={{ marginLeft: "4px", marginRight: "2px"}} width={14} height={14} />
      </a>
    )
  } else {
    return (
      <NextLink href={href} {...attributes} {...rest}>
        {children}
      </NextLink>
    )
  }
}

export default Link;
