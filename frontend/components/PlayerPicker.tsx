"use client"

import { useEffect, useMemo, useState } from "react"

import { usePathname } from "next/navigation"

import Faction from "@/classes/Faction"
import { useAppContext } from "@/contexts/AppContext"

/**
 * Fallback roster, so a game can be set up from nothing: sign in as the first,
 * create a game, then switch and join as each of the others. Only used outside
 * a live game — the players of an actual game are the real roster. The test
 * login endpoint creates these on demand, so they need no prior existence.
 */
const STARTER_ACCOUNTS = ["player1", "player2", "player3"]

interface Entry {
  username: string
  faction: string | null
  position: number | null
}

interface Props {
  /** Factions of the game being viewed, when there is one. */
  factions?: Faction[]
  /** "bar" matches the in-game GameBar cells, "nav" the NavBar links. */
  variant?: "bar" | "nav"
}

/**
 * Dev-only control for playing every faction from one window: one button per
 * player, so switching is a single click.
 *
 * Hidden the same way the debug panel is: it probes an endpoint that only
 * exists when TEST_ENDPOINTS_ENABLED is set, so the backend flag decides
 * whether it appears and a production build can never show it.
 */
const PlayerPicker = ({ factions, variant = "bar" }: Props) => {
  const { user } = useAppContext()
  const pathname = usePathname()
  const [enabled, setEnabled] = useState(false)
  const [switchingTo, setSwitchingTo] = useState<string | null>(null)

  useEffect(() => {
    fetch(`${process.env.NEXT_PUBLIC_BACKEND_ORIGIN}/api/test/presets/`, {
      credentials: "include",
    })
      .then((response) => {
        if (response.ok) setEnabled(true)
      })
      .catch(() => {})
  }, [])

  const entries = useMemo<Entry[]>(() => {
    const byUsername = new Map<string, Entry>()

    // A game's own players are the roster that matters — whichever accounts
    // they happen to be. In the game bar they are the whole list, so a game
    // played by one set of accounts never offers buttons for another.
    for (const faction of factions ?? []) {
      byUsername.set(faction.player.username, {
        username: faction.player.username,
        faction: faction.displayName,
        position: faction.position,
      })
    }

    // Outside the game bar, offer the starter accounts as well: seats still
    // need filling in the lobby, and signing in needs somewhere to begin.
    if (variant !== "bar") {
      for (const username of STARTER_ACCOUNTS) {
        if (!byUsername.has(username))
          byUsername.set(username, { username, faction: null, position: null })
      }
    }

    // Whoever is signed in is always listed, even when they are a stranger to
    // this game. Otherwise no button is marked current and there is no way back
    // to the account you arrived as.
    if (user && !byUsername.has(user.username)) {
      byUsername.set(user.username, {
        username: user.username,
        faction: null,
        position: null,
      })
    }

    return [...byUsername.values()].sort((a, b) => {
      if (a.position !== null && b.position !== null)
        return a.position - b.position
      if (a.position !== null) return -1
      if (b.position !== null) return 1
      return a.username.localeCompare(b.username)
    })
  }, [factions, user, variant])

  const switchTo = async (username: string) => {
    setSwitchingTo(username)
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_BACKEND_ORIGIN}/api/test/login/`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          credentials: "include",
          body: JSON.stringify({ username }),
        },
      )
      if (!response.ok)
        throw new Error(`test login returned ${response.status}`)
      // The session cookie is httpOnly and shared by the whole browser profile,
      // so identity cannot be swapped in place — everything has to be rebuilt.
      // Staying on the sign-in page after signing in would be a dead end.
      if (pathname?.startsWith("/auth")) {
        window.location.assign("/games")
      } else {
        window.location.reload()
      }
    } catch {
      setSwitchingTo(null)
    }
  }

  if (!enabled) return null

  if (variant === "nav") {
    return (
      <div className="flex items-baseline gap-2">
        <span className="text-neutral-500">Play as:</span>
        {entries.map((entry) => {
          const isCurrent = entry.username === user?.username
          return (
            <button
              key={entry.username}
              type="button"
              title={entry.faction ?? undefined}
              disabled={isCurrent || switchingTo !== null}
              onClick={() => switchTo(entry.username)}
              className={`rounded border px-2 text-sm disabled:opacity-60 ${
                isCurrent
                  ? "cursor-default border-[#630330] bg-[#630330] text-white"
                  : "border-neutral-400 hover:bg-neutral-100"
              }`}
            >
              {entry.username}
            </button>
          )
        })}
      </div>
    )
  }

  // Supplies its own cell wrapper rather than being placed in one, so that when
  // it renders nothing the game bar's divide-x leaves no stray divider behind.
  return (
    <div className="flex h-full items-center">
      {entries.map((entry) => {
        const isCurrent = entry.username === user?.username
        return (
          <button
            key={entry.username}
            type="button"
            disabled={isCurrent || switchingTo !== null}
            onClick={() => switchTo(entry.username)}
            className={`flex h-full flex-col justify-center px-4 text-sm disabled:opacity-100 ${
              isCurrent ? "cursor-default bg-neutral-100" : "hover:bg-blue-50"
            }`}
          >
            <span className={isCurrent ? "font-semibold" : undefined}>
              {entry.faction ?? entry.username}
            </span>
            <span className="text-neutral-500">
              {switchingTo === entry.username ? "switching…" : entry.username}
            </span>
          </button>
        )
      })}
    </div>
  )
}

export default PlayerPicker
