import { ReactNode } from "react"
import Link from "@mui/material/Link"
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome"
import { faExternalLink } from "@fortawesome/free-solid-svg-icons"

interface LinkProps {
  href: string
  children: ReactNode
  attributes?: React.HTMLAttributes<HTMLElement>
}

/**
 * For rendering external links.
 */
const ExternalLink = (props: LinkProps) => {
  return (
    <Link
      {...props.attributes}
      href={props.href}
      target="_blank"
      rel="noopener"
    >
      {props.children}
      <FontAwesomeIcon
        icon={faExternalLink}
        style={{ marginLeft: "4px", marginRight: "2px" }}
        width={14}
        height={14}
      />
    </Link>
  )
}

export default ExternalLink
