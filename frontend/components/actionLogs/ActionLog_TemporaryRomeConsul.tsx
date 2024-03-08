import Image from "next/image"
import Cookies from "js-cookie"
import { Alert } from "@mui/material"
import ActionLog from "@/classes/ActionLog"
import SenatorLink from "@/components/SenatorLink"
import FactionLink from "@/components/FactionLink"
import RomeConsulIcon from "@/images/icons/romeConsul.svg"
import Faction from "@/classes/Faction"
import Senator from "@/classes/Senator"
import { useGameContext } from "@/contexts/GameContext"
import TermLink from "@/components/TermLink"
import { useCookieContext } from "@/contexts/CookieContext"
import formatDate from "@/functions/date"

interface NotificationProps {
  notification: ActionLog
  senatorDetails?: boolean
}

const TemporaryRomeConsulNotification = ({
  notification,
  senatorDetails,
}: NotificationProps) => {
  const { darkMode } = useCookieContext()
  const { allFactions, allSenators } = useGameContext()
  const timezone = Cookies.get("timezone")

  // Get notification-specific data
  const faction: Faction | null = notification.faction
    ? allFactions.byId[notification.faction] ?? null
    : null
  const senator: Senator | null = notification.data.senator
    ? allSenators.byId[notification.data.senator] ?? null
    : null

  const getIcon = () => (
    <div className="h-[18px] w-[24px] flex justify-center">
      <Image
        src={RomeConsulIcon}
        alt="rome consul icon"
        width={30}
        height={30}
      />
    </div>
  )

  // Get the text for the notification (tense sensitive)
  const getText = () => {
    if (!faction || !senator) return null

    if (senatorDetails) {
      return (
        <p>
          <SenatorLink senator={senator} /> became{" "}
          <TermLink name="Rome Consul" displayName="Temporary Rome Consul" />.
        </p>
      )
    } else {
      return (
        <p>
          <SenatorLink senator={senator} /> of the{" "}
          <FactionLink faction={faction} /> now holds the office of{" "}
          <TermLink name="Rome Consul" displayName="Temporary Rome Consul" />,
          making him the <TermLink name="HRAO" />.
        </p>
      )
    }
  }

  if (!faction || !senator) return null

  return (
    <Alert
      icon={getIcon()}
      style={{
        backgroundColor: darkMode
          ? faction.getColor(900)
          : faction.getColor(100),
        border: `solid 1px ${
          darkMode ? faction.getColor(950) : faction.getColor(300)
        }`,
        position: "relative",
      }}
    >
      {timezone && (
        <div className="absolute right-1 top-0.5 text-xs opacity-50">
          {formatDate(notification.creation_date, timezone)}
        </div>
      )}
      <b>Temporary Rome Consul</b>
      {getText()}
    </Alert>
  )
}

export default TemporaryRomeConsulNotification
