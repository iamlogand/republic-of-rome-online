"use client"

import React from "react"

import Link from "next/link"
import { useRouter } from "next/navigation"

import PrivateGameState from "@/classes/PrivateGameState"
import PublicGameState from "@/classes/PublicGameState"
import FactionCards from "@/components/FactionCards"
import GameEffects from "@/components/GameEffects"
import Popover from "@/components/Popover"
import { useAppContext } from "@/contexts/AppContext"
import { forceListToString } from "@/helpers/forceLists"

interface Props {
  publicGameState: PublicGameState
  privateGameState: PrivateGameState | undefined
  onCombatCalculatorOpen: () => void
}

const Cell = ({ children }: { children: React.ReactNode }) => (
  <div className="flex h-full items-center">{children}</div>
)

const GameBar = ({
  publicGameState,
  privateGameState,
  onCombatCalculatorOpen,
}: Props) => {
  const { user } = useAppContext()
  const router = useRouter()

  const game = publicGameState.game!

  const reserveLegions = publicGameState.legions.filter(
    (l) => !l.veteran && l.campaign == null,
  )
  const campaignLegions = publicGameState.legions.filter(
    (l) => !l.veteran && l.campaign != null,
  )
  const reserveVeterans = publicGameState.legions.filter(
    (l) => l.veteran && l.campaign == null,
  )
  const campaignVeterans = publicGameState.legions.filter(
    (l) => l.veteran && l.campaign != null,
  )
  const reserveFleets = publicGameState.fleets.filter((f) => f.campaign == null)
  const campaignFleets = publicGameState.fleets.filter(
    (f) => f.campaign != null,
  )

  const isHost = user?.id === game.host.id

  return (
    <div className="flex h-16 shrink-0 items-stretch divide-x divide-neutral-300">
      {/* Turn */}
      <Cell>
        <Popover
          className="h-full"
          triggerClassName="h-full flex flex-col items-center justify-center w-36"
          trigger={
            <>
              <span className="shrink-0 tabular-nums">Turn {game.turn}</span>
              <span className="text-sm first-letter:uppercase">
                {game.phase} phase
              </span>
            </>
          }
        >
          <div className="flex flex-col gap-2">
            {game.deckCount} card{game.deckCount !== 1 ? "s" : ""} in the deck
          </div>
        </Popover>
      </Cell>

      {/* State treasury */}
      <Cell>
        <span className="flex flex-col items-center px-4">
          <span className="text-nowrap text-sm">State treasury</span>
          <span className="tabular-nums">{game.stateTreasury}T</span>
        </span>
      </Cell>

      {/* Legions */}
      <Cell>
        <Popover
          className="h-full"
          triggerClassName="h-full flex flex-col items-center justify-center px-4"
          trigger={
            <>
              <span className="text-sm">Legions</span>
              <span className="tabular-nums">
                {reserveLegions.length}
                {campaignLegions.length > 0 && (
                  <span className="text-neutral-600">
                    {" "}
                    / {campaignLegions.length}
                  </span>
                )}
              </span>
            </>
          }
        >
          <div className="flex flex-col gap-2">
            {reserveLegions.length > 0 && (
              <div className="flex flex-col gap-1">
                <span>{reserveLegions.length} legions in reserve</span>
                <div className="text-sm text-neutral-600">
                  {forceListToString(reserveLegions)}
                </div>
              </div>
            )}
            {campaignLegions.length > 0 && (
              <div className="flex flex-col gap-1">
                <span>{campaignLegions.length} legions on campaign</span>
                <div className="text-sm text-neutral-600">
                  {forceListToString(campaignLegions)}
                </div>
              </div>
            )}
            {reserveLegions.length + campaignLegions.length === 0 && (
              <span className="text-neutral-600">No legions</span>
            )}
          </div>
        </Popover>
      </Cell>

      {/* Veterans */}
      <Cell>
        <Popover
          className="h-full"
          triggerClassName="h-full flex flex-col items-center justify-center px-4"
          trigger={
            <>
              <span className="text-sm">Veterans</span>
              <span className="tabular-nums">
                {reserveVeterans.length}
                {campaignVeterans.length > 0 && (
                  <span className="text-neutral-600">
                    {" "}
                    / {campaignVeterans.length}
                  </span>
                )}
              </span>
            </>
          }
        >
          <div className="flex flex-col gap-2">
            {reserveVeterans.length > 0 && (
              <div className="flex flex-col gap-1">
                <span>{reserveVeterans.length} veterans in reserve</span>
                <div className="text-sm text-neutral-600">
                  {forceListToString(reserveVeterans)}
                </div>
              </div>
            )}
            {campaignVeterans.length > 0 && (
              <div className="flex flex-col gap-1">
                <span>{campaignVeterans.length} veterans on campaign</span>
                <div className="text-sm text-neutral-600">
                  {forceListToString(campaignVeterans)}
                </div>
              </div>
            )}
            {reserveVeterans.length + campaignVeterans.length === 0 && (
              <span className="text-neutral-600">No veterans</span>
            )}
          </div>
        </Popover>
      </Cell>

      {/* Fleets */}
      <Cell>
        <Popover
          className="h-full"
          triggerClassName="h-full flex flex-col items-center justify-center px-4"
          trigger={
            <>
              <span className="text-sm">Fleets</span>
              <span className="tabular-nums">
                {reserveFleets.length}
                {campaignFleets.length > 0 && (
                  <span className="text-neutral-600">
                    {" "}
                    / {campaignFleets.length}
                  </span>
                )}
              </span>
            </>
          }
        >
          <div className="flex flex-col gap-2">
            {reserveFleets.length > 0 && (
              <div className="flex flex-col gap-1">
                <span>{reserveFleets.length} fleets in reserve</span>

                <div className="text-sm text-neutral-600">
                  {forceListToString(reserveFleets)}
                </div>
              </div>
            )}
            {campaignFleets.length > 0 && (
              <div className="flex flex-col gap-1">
                <span>{campaignFleets.length} fleets on campaign</span>
                <div className="text-sm text-neutral-600">
                  {forceListToString(campaignFleets)}
                </div>
              </div>
            )}
            {reserveFleets.length + campaignFleets.length === 0 && (
              <span className="text-neutral-600">No fleets</span>
            )}
          </div>
        </Popover>
      </Cell>

      {/* Unrest */}
      <Cell>
        <Popover
          className="h-full"
          triggerClassName="h-full flex flex-col items-center justify-center px-4"
          trigger={
            <>
              <span className="text-sm">Unrest</span>
              <span className="tabular-nums">{game.unrest}</span>
            </>
          }
        >
          <div className="flex flex-col gap-2">
            {game.famineSeverity === 0 && game.unprosecutedWars === 0 ? (
              <span className="text-neutral-600">No upcoming modifiers</span>
            ) : (
              <ul className="flex flex-col gap-1">
                {game.famineSeverity > 0 && (
                  <li>Famine severity: {game.famineSeverity}</li>
                )}
                {game.unprosecutedWars > 0 && (
                  <li>Unprosecuted wars: {game.unprosecutedWars}</li>
                )}
              </ul>
            )}
          </div>
        </Popover>
      </Cell>

      {/* Effects */}
      <Cell>
        <Popover
          className="h-full"
          triggerClassName="h-full flex flex-col items-center justify-center px-4"
          trigger={
            <>
              <span className="text-sm">Effects</span>
              <span>{game.effects.length}</span>
            </>
          }
        >
          <div className="flex flex-col gap-2">
            {game.effects.length > 0 ? (
              <GameEffects effects={game.effects} />
            ) : (
              <span className="text-neutral-600">No effects</span>
            )}
          </div>
        </Popover>
      </Cell>

      {/* Faction / Spectator */}
      <Cell>
        {privateGameState?.faction ? (
          <Popover
            className="h-full"
            triggerClassName="h-full flex items-center justify-center px-4 flex-col"
            trigger={
              <>
                <span>{privateGameState?.faction?.displayName}</span>
                <span className="text-sm">{user?.username}</span>
              </>
            }
          >
            <div className="flex w-96 flex-col gap-3">
              <div className="flex justify-between">
                <span>
                  {privateGameState.faction.cards.length}
                  <span className="text-neutral-600"> / 5 cards in hand</span>
                </span>
                <span>
                  {privateGameState.faction.treasury}T in faction treasury
                </span>
              </div>
              <hr className="-mx-4 border-neutral-300" />
              <FactionCards cards={privateGameState.faction.cards} />
            </div>
          </Popover>
        ) : (
          <span className="px-4">Spectating</span>
        )}
      </Cell>

      {/* Spacer */}
      <div className="flex-1" />

      {/* Combat Calculator */}
      <Cell>
        <button
          type="button"
          onClick={onCombatCalculatorOpen}
          className="flex h-full flex-col justify-center px-4 text-sm hover:bg-neutral-100"
        >
          <span>Combat</span>
          <span>Calculator</span>
        </button>
      </Cell>

      {/* Menu */}
      <Cell>
        <Popover
          align="right"
          className="h-full"
          triggerClassName="h-full w-16 flex items-center justify-center"
          trigger="☰"
        >
          <div className="flex min-w-64 flex-col gap-3">
            <div className="flex flex-col gap-1">
              <div className="text-lg font-medium">{game.name}</div>
              <div>Hosted by: {game.host.username}</div>
              {game.startedOn && (
                <div className="text-sm text-neutral-500">
                  Started: {new Date(game.startedOn).toLocaleString()}
                </div>
              )}
            </div>
            {isHost && (
              <>
                <hr className="-mx-4 border-neutral-300" />
                <Link
                  href={`/games/${game.id}/edit`}
                  className="block px-2 py-1.5 text-sm hover:bg-neutral-100"
                >
                  Edit game
                </Link>
              </>
            )}
            <hr className="-mx-4 border-neutral-300" />
            <div className="flex flex-col">
              <button
                onClick={() => router.push("/games")}
                className="block w-full px-2 py-1.5 text-left text-sm hover:bg-neutral-100"
              >
                Back to games
              </button>
              <Link
                href="/auth/logout"
                className="block px-2 py-1.5 text-sm hover:bg-neutral-100"
              >
                Sign out
              </Link>
            </div>
          </div>
        </Popover>
      </Cell>
    </div>
  )
}

export default GameBar
