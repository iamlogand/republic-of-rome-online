"use client"

import React, { Dispatch, ReactNode, SetStateAction } from "react"

import Link from "next/link"
import { usePathname } from "next/navigation"

import Faction from "@/classes/Faction"
import PlayerPicker from "@/components/PlayerPicker"
import { useAppContext } from "@/contexts/AppContext"

interface AppWrapperProps {
  visible: boolean
  setVisible?: Dispatch<SetStateAction<boolean>>
  children?: ReactNode
  /** Factions of the game being viewed, so the dev player picker can name them. */
  factions?: Faction[]
}

const NavBar = ({
  visible,
  setVisible,
  children,
  factions,
}: AppWrapperProps) => {
  const { user } = useAppContext()
  const pathname = usePathname()

  const handleSignInClick = () => {
    // Save current pathname to localStorage for post-auth redirect
    if (pathname && pathname !== "/auth/login") {
      localStorage.setItem("post_auth_redirect", pathname)
    }
  }

  return (
    <header>
      {visible && (
        <>
          <div className="flex flex-wrap items-baseline justify-between gap-x-8 gap-y-4 px-4 py-4 lg:px-10">
            <Link href="/">
              <h1 className="text-xl font-bold text-[#630330]">
                Republic of Rome Online
              </h1>
            </Link>
            <div className="flex flex-wrap items-baseline gap-x-8 gap-y-2">
              {user ? (
                <>
                  <Link href="/games">
                    <div className="hover:text-blue-600">Games</div>
                  </Link>
                  <Link href="/account">
                    <div className="hover:text-blue-600">
                      Signed in as:{" "}
                      <span className="inline-block max-w-[12ch] truncate align-bottom font-bold">
                        {user.username}
                      </span>
                    </div>
                  </Link>
                  <Link href="/auth/logout">
                    <div className="hover:text-blue-600">Sign out</div>
                  </Link>
                </>
              ) : (
                <Link href="/auth/login" onClick={handleSignInClick}>
                  <div className="hover:text-blue-600">Sign in</div>
                </Link>
              )}
              <PlayerPicker variant="nav" factions={factions} />
            </div>
          </div>
          {children && (
            <>
              <div className="px-4 pb-4 lg:px-10">{children}</div>
              <hr className="border-neutral-300" />
            </>
          )}
        </>
      )}
      {setVisible && (
        <div className="relative box-border h-0 w-full overflow-visible">
          <div className="absolute top-0 z-50 flex w-full justify-end px-8">
            {visible ? (
              <button
                className="rounded-b bg-blue-100 px-2 text-sm text-blue-600"
                onClick={() => setVisible(false)}
              >
                Hide nav
              </button>
            ) : (
              <button
                className="rounded-b bg-blue-100 px-2 text-sm text-blue-600"
                onClick={() => setVisible(true)}
              >
                Show nav
              </button>
            )}
          </div>
        </div>
      )}
    </header>
  )
}

export default NavBar
