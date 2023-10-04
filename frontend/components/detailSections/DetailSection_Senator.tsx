import Image from "next/image"
import { RefObject, useCallback, useEffect, useRef, useState } from "react"

import SenatorPortrait from "@/components/SenatorPortrait"
import Senator from "@/classes/Senator"
import Player from "@/classes/Player"
import Faction from "@/classes/Faction"
import styles from "./DetailSection_Senator.module.css"
import { useGameContext } from "@/contexts/GameContext"
import skillsJSON from "@/data/skills.json"
import MilitaryIcon from "@/images/icons/military.svg"
import OratoryIcon from "@/images/icons/oratory.svg"
import LoyaltyIcon from "@/images/icons/loyalty.svg"
import InfluenceIcon from "@/images/icons/influence.svg"
import TalentsIcon from "@/images/icons/talents.svg"
import PopularityIcon from "@/images/icons/popularity.svg"
import KnightsIcon from "@/images/icons/knights.svg"
import VotesIcon from "@/images/icons/votes.svg"
import FactionLink from "@/components/FactionLink"
import Title from "@/classes/Title"
import { Box, Tab, Tabs } from "@mui/material"
import ActionLog from "@/classes/ActionLog"
import request from "@/functions/request"
import { useAuthContext } from "@/contexts/AuthContext"
import { deserializeToInstances } from "@/functions/serialize"
import Collection from "@/classes/Collection"
import SenatorActionLog from "@/classes/SenatorActionLog"
import ActionLogContainer from "@/components/actionLogs/ActionLog"
import TermLink from "@/components/TermLink"

type FixedAttribute = {
  name: "military" | "oratory" | "loyalty"
  value: number
  maxValue?: number
  image: string
  description: string
}

type VariableAttribute = {
  name: "influence" | "talents" | "popularity" | "knights" | "votes"
  value: number
  image: string
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
  } = useAuthContext()
  const {
    allPlayers,
    allFactions,
    allSenators,
    setAllSenators,
    allTitles,
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
  const faction: Faction | null = senator?.faction
    ? allFactions.byId[senator.faction] ?? null
    : null
  const player: Player | null = faction?.player
    ? allPlayers.byId[faction.player] ?? null
    : null
  const majorOffice: Title | null = senator
    ? allTitles.asArray.find(
        (t) => t.senator === senator.id && t.major_office == true
      ) ?? null
    : null
  const factionLeader: boolean = senator
    ? allTitles.asArray.some(
        (t) => t.senator === senator.id && t.name == "Faction Leader"
      )
    : false
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
    if (detailDivWidth && detailDivWidth < 416) {
      let width = (detailDivWidth - 20) / 2

      // Round down to a multiple of 12 so that we get a nice size value
      // to reduce imperfections on lower resolution displays.
      return Math.floor(width / 12) * 12
    } else {
      return 200
    }
  }

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
          }`,
        },
      ]
    : []

  // Variable attribute data
  const variableAttributeItems: VariableAttribute[] = senator
    ? [
        { name: "influence", value: senator.influence, image: InfluenceIcon },
        { name: "talents", value: senator.talents, image: TalentsIcon },
        {
          name: "popularity",
          value: senator.popularity,
          image: PopularityIcon,
        },
        { name: "knights", value: senator.knights, image: KnightsIcon },
        { name: "votes", value: senator.votes, image: VotesIcon },
      ]
    : []

  // Get JSX for a fixed attribute item
  const getFixedAttributeRow = (item: FixedAttribute) => {
    const titleCaseName = item.name[0].toUpperCase() + item.name.slice(1)
    return (
      <div key={item.name} className={styles.attribute}>
        <div className={styles.attributeNameAndValue}>
          <div>{titleCaseName}</div>
          <Image
            src={item.image}
            height={34}
            width={34}
            alt={`${titleCaseName} icon`}
            style={{ userSelect: "none" }}
          />
          <div>
            <i>{item.description}</i>
          </div>
          <div
            className={styles.skill}
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
        <progress
          id="file"
          value={item.value}
          max={item.maxValue ?? 10}
          className={styles.attributeBar}
          style={{
            accentColor:
              skillsJSON.colors.bar[
                item.name as "military" | "oratory" | "loyalty"
              ],
          }}
        />
      </div>
    )
  }

  // Get JSX for a variable attribute item
  const getVariableAttributeRow = (item: VariableAttribute) => {
    const titleCaseName = item.name[0].toUpperCase() + item.name.slice(1)
    return (
      <div key={item.name}>
        <div>{titleCaseName}</div>
        <Image
          src={item.image}
          height={34}
          width={34}
          alt={`${titleCaseName} icon`}
          style={{ userSelect: "none" }}
        />
        <div className={styles.attributeValue}>{item.value}</div>
      </div>
    )
  }

  // If there is no senator selected, render nothing
  if (!senator) return null

  return (
    <div className={styles.senatorDetailSection}>
      <div className={styles.primaryArea}>
        <div className={styles.portraitContainer}>
          <SenatorPortrait senator={senator} size={getPortraitSize()} />
        </div>
        <div className={styles.textContainer}>
          <h4>
            <b>{senator.displayName}</b>
          </h4>
          <p>
            {faction ? (
              <span>
                <FactionLink faction={faction} includeIcon />
                {factionLeader ? " Leader" : null}
                {player ? <span> ({player.user?.username})</span> : null}
              </span>
            ) : senator.alive ? (
              "Unaligned"
            ) : (
              "Dead"
            )}
          </p>
          {majorOffice && (
            <p>
              Serving as{" "}
              <TermLink
                name={
                  majorOffice.name == "Temporary Rome Consul"
                    ? "Rome Consul"
                    : majorOffice.name
                }
                displayName={majorOffice.name}
                includeIcon
              />
            </p>
          )}
        </div>
      </div>
      <Box sx={{ borderBottom: 1, borderColor: "divider" }}>
        <Tabs
          value={senatorDetailTab}
          onChange={handleTabChange}
          className={styles.tabs}
        >
          <Tab label="Attributes" />
          <Tab label="History" />
        </Tabs>
      </Box>
      <div className={styles.tabContent}>
        {senatorDetailTab === 0 && (
          <div className={styles.attributeArea}>
            <div className={styles.fixedAttributeContainer}>
              {fixedAttributeItems.map((item) => getFixedAttributeRow(item))}
            </div>
            <div className={styles.variableAttributeContainer}>
              {variableAttributeItems.map((item) =>
                getVariableAttributeRow(item)
              )}
            </div>
          </div>
        )}
        {senatorDetailTab === 1 && (
          <div ref={scrollableAreaRef} className={styles.logList}>
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
                <div className={styles.noHistory}>
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
