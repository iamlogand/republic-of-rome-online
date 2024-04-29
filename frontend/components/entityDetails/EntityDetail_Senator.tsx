import Image from "next/image"
import { RefObject, useCallback, useEffect, useRef } from "react"

import SenatorPortrait from "@/components/SenatorPortrait"
import Senator from "@/classes/Senator"
import { useGameContext } from "@/contexts/GameContext"
import skillsJSON from "@/data/skills.json"
import MilitaryIcon from "@/images/icons/military.svg"
import OratoryIcon from "@/images/icons/oratory.svg"
import LoyaltyIcon from "@/images/icons/loyalty.svg"
import InfluenceIcon from "@/images/icons/influence.svg"
import PersonalTreasuryIcon from "@/images/icons/personalTreasury.svg"
import PopularityIcon from "@/images/icons/popularity.svg"
import KnightsIcon from "@/images/icons/knights.svg"
import VotesIcon from "@/images/icons/votes.svg"
import { Tab, Tabs } from "@mui/material"
import ActionLog from "@/classes/ActionLog"
import request from "@/functions/request"
import { useCookieContext } from "@/contexts/CookieContext"
import { deserializeToInstances } from "@/functions/serialize"
import Collection from "@/classes/Collection"
import SenatorActionLog from "@/classes/SenatorActionLog"
import ActionLogContainer from "@/components/ActionLog"
import AttributeGrid, { Attribute } from "@/components/AttributeGrid"
import SenatorFactionInfo from "@/components/SenatorFactionInfo"
import SenatorFactList from "@/components/SenatorFactList"
import TermLink from "@/components/TermLink"

type FixedAttribute = {
  name: "military" | "oratory" | "loyalty"
  value: number
  maxValue?: number
  image: string
  description: string
}

type NormalSkillValue = 1 | 2 | 3 | 4 | 5 | 6
type LoyaltySkillValue = 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10

interface SenatorDetailsProps {
  detailSectionRef: RefObject<HTMLDivElement>
}

// Detail section content for a senator
const SenatorDetails = (props: SenatorDetailsProps) => {
  const {
    accessToken,
    refreshToken,
    setAccessToken,
    setRefreshToken,
    setUser,
    darkMode,
  } = useCookieContext()
  const {
    allSenators,
    setAllSenators,
    selectedDetail,
    actionLogs,
    setActionLogs,
    senatorActionLogs,
    setSenatorActionLogs,
    senatorDetailTab,
    setSenatorDetailTab,
  } = useGameContext()

  const scrollableAreaRef = useRef<HTMLDivElement | null>(null)

  // Get senator-specific data
  const senator: Senator | null = selectedDetail?.id
    ? allSenators.byId[selectedDetail.id] ?? null
    : null
  const matchingSenatorActionLogs = senator
    ? senatorActionLogs.asArray.filter((l) => l.senator === senator.id)
    : null
  const matchingActionLogs = matchingSenatorActionLogs
    ? actionLogs.asArray.filter((a) =>
        matchingSenatorActionLogs.some((b) => b.action_log === a.id)
      )
    : null

  // Fetch action logs for this senator
  const fetchActionLogs = useCallback(async () => {
    if (!senator) return

    const response = await request(
      "GET",
      `action-logs/?senator=${senator.id}`,
      accessToken,
      refreshToken,
      setAccessToken,
      setRefreshToken,
      setUser
    )
    if (response.status === 200) {
      const deserializedInstances = deserializeToInstances<ActionLog>(
        ActionLog,
        response.data
      )
      setActionLogs(
        (instances: Collection<ActionLog>) =>
          // Loop over each instance in deserializedInstances and add it to the collection if it's not already there
          new Collection<ActionLog>(
            instances.asArray.concat(
              deserializedInstances.filter(
                (i) => !instances.asArray.some((j) => j.id === i.id)
              )
            )
          )
      )
    } else {
      setActionLogs(new Collection<ActionLog>())
    }
  }, [
    senator,
    accessToken,
    refreshToken,
    setAccessToken,
    setRefreshToken,
    setUser,
    setActionLogs,
  ])

  // Fetch senator action logs for this senator
  const fetchSenatorActionLogs = useCallback(async () => {
    if (!senator) return

    const response = await request(
      "GET",
      `senator-action-logs/?senator=${senator.id}`,
      accessToken,
      refreshToken,
      setAccessToken,
      setRefreshToken,
      setUser
    )
    if (response.status === 200) {
      const deserializedInstances = deserializeToInstances<SenatorActionLog>(
        SenatorActionLog,
        response.data
      )
      setSenatorActionLogs(
        (instances: Collection<SenatorActionLog>) =>
          // Loop over each instance in deserializedInstances and add it to the collection if it's not already there
          new Collection<SenatorActionLog>(
            instances.asArray.concat(
              deserializedInstances.filter(
                (i) => !instances.asArray.some((j) => j.id === i.id)
              )
            )
          )
      )
    } else {
      setSenatorActionLogs(new Collection<SenatorActionLog>())
    }
  }, [
    senator,
    accessToken,
    refreshToken,
    setAccessToken,
    setRefreshToken,
    setUser,
    setSenatorActionLogs,
  ])

  // Fetch logs
  const fetchLogs = useCallback(async () => {
    if (!senator) return

    await Promise.all([fetchActionLogs(), fetchSenatorActionLogs()])

    senator.logsFetched = true
    setAllSenators(
      (senators: Collection<Senator>) =>
        new Collection<Senator>(
          senators.asArray.map((s) => (s.id === senator.id ? senator : s))
        )
    )
  }, [senator, fetchActionLogs, fetchSenatorActionLogs, setAllSenators])

  // Fetch logs once component mounts, but only if they haven't been fetched yet
  useEffect(() => {
    if (!senator || senator?.logsFetched) return

    // Fetch action logs and senator action logs
    fetchLogs()
  }, [senator, fetchLogs])

  // Initially scroll to bottom if history tab is selected
  useEffect(() => {
    if (scrollableAreaRef.current) {
      scrollableAreaRef.current.scrollTop =
        scrollableAreaRef.current.scrollHeight
    }
  }, [senatorDetailTab, senator, senatorActionLogs])

  // Change selected tab
  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setSenatorDetailTab(newValue)
  }

  // Calculate senator portrait size.
  // Image size must be defined in JavaScript rather than in CSS
  const getPortraitSize = () => {
    const detailDivWidth = props.detailSectionRef.current?.offsetWidth
    if (!detailDivWidth) return null

    if (detailDivWidth < 416) {
      let width = (detailDivWidth - 32) / 2

      // Round down to a multiple of 12 so that we get a nice size value
      // to reduce imperfections on lower resolution displays.
      return Math.floor(width / 12) * 12
    } else {
      return 200
    }
  }
  const portraitSize = getPortraitSize()

  // Fixed attribute data
  const fixedAttributeItems: FixedAttribute[] = senator
    ? [
        {
          name: "military",
          value: senator.military,
          maxValue: 6,
          image: MilitaryIcon,
          description: `${
            skillsJSON.descriptions.default[
              senator.military as NormalSkillValue
            ]
          } Commander`,
        },
        {
          name: "oratory",
          value: senator.oratory,
          maxValue: 6,
          image: OratoryIcon,
          description: `${
            skillsJSON.descriptions.default[senator.oratory as NormalSkillValue]
          } Orator`,
        },
        {
          name: "loyalty",
          value: senator.loyalty,
          image: LoyaltyIcon,
          description: `${
            skillsJSON.descriptions.loyalty[
              senator.loyalty as LoyaltySkillValue
            ]
          } Loyalty`,
        },
      ]
    : []

  // Variable attribute data
  const variableAttributeItems: Attribute[] = senator
    ? [
        { name: "Influence", value: senator.influence, icon: InfluenceIcon },
        {
          name: "Personal Treasury",
          value: senator.personalTreasury,
          icon: PersonalTreasuryIcon,
          fontSize: 14,
        },
        {
          name: "Popularity",
          value: senator.popularity,
          icon: PopularityIcon,
        },
        { name: "Knights", value: senator.knights, icon: KnightsIcon },
        { name: "Votes", value: senator.votes, icon: VotesIcon },
      ]
    : []

  // Get JSX for a fixed attribute item
  const getFixedAttributeRow = (item: FixedAttribute) => {
    const titleCaseName = item.name[0].toUpperCase() + item.name.slice(1)
    return (
      <div key={item.name} className="flex flex-col items-stretch">
        <div className="w-full grid grid-cols-[35px_60px_1fr_35px] items-center gap-1 pr-1 box-border">
          <Image
            src={item.image}
            height={34}
            width={34}
            alt={`${titleCaseName} icon`}
            style={{ userSelect: "none" }}
          />
          <TermLink name={titleCaseName} />
          <div className="text-center text-sm text-neutral-500 dark:text-neutral-300">
            {item.description}
          </div>
          <div className="flex justify-center">
            <div
              className="w-full text-white text-center font-semibold rounded-sm text-lg leading-5"
              style={{
                backgroundColor: skillsJSON.colors.number[item.name],
                boxShadow: `0px 0px 2px 2px ${
                  skillsJSON.colors.number[item.name]
                }`,
                userSelect: "none",
              }}
            >
              {item.value}
            </div>
          </div>
        </div>
        <progress
          id="file"
          value={item.value}
          max={item.maxValue ?? 10}
          className="w-full"
          style={{
            accentColor:
              skillsJSON.colors.bar[darkMode ? "dark" : "light"][
                item.name as "military" | "oratory" | "loyalty"
              ],
          }}
        />
      </div>
    )
  }

  // If there is no senator selected, render nothing
  if (!senator || !portraitSize) return null

  return (
    <div className="h-full box-border flex flex-col overflow-y-auto">
      <div className="flex gap-4 m-4">
        <SenatorPortrait senator={senator} size={portraitSize} />
        <div className="flex flex-col gap-2">
          <h4 className="text-lg">
            <b>{senator.displayName}</b>
          </h4>
          <div className="flex flex-col gap-3">
            <SenatorFactionInfo senator={senator} selectable />
            <SenatorFactList senator={senator} selectable />
          </div>
        </div>
      </div>
      <div className="border-0 border-b border-solid border-neutral-200 dark:border-neutral-750">
        <Tabs
          value={senatorDetailTab}
          onChange={handleTabChange}
          className="px-4"
        >
          <Tab label="Attributes" />
          <Tab label="History" />
        </Tabs>
      </div>
      <div className="flex-1 overflow-y-auto p-4 bg-neutral-50 dark:bg-neutral-650 shadow-inner">
        {senatorDetailTab === 0 && (
          <div className="grid grid-cols-[repeat(auto-fit,minmax(250px,1fr))] gap-6 overflow-y-auto">
            <div className="flex flex-col gap-4 p-2">
              {fixedAttributeItems.map((item) => getFixedAttributeRow(item))}
            </div>
            <AttributeGrid attributes={variableAttributeItems} />
          </div>
        )}
        {senatorDetailTab === 1 && (
          <div
            ref={scrollableAreaRef}
            className="h-fill box-border flex flex-col gap-2 overflow-y-auto"
          >
            {matchingActionLogs &&
              matchingActionLogs
                .sort((a, b) => a.index - b.index)
                .map((notification) => (
                  <ActionLogContainer
                    key={notification.id}
                    notification={notification}
                    senatorDetails
                  />
                ))}

            {matchingActionLogs &&
              matchingActionLogs.length === 0 &&
              senator.logsFetched && (
                <div className="flex justify-center text-neutral-500 dark:text-neutral-300 text-sm">
                  {senator.displayName} has not yet made his name
                </div>
              )}
          </div>
        )}
      </div>
    </div>
  )
}

export default SenatorDetails
