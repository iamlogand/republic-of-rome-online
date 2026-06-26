import NavBar from "@/components/NavBar"

const Home = async () => {
  return (
    <div className="flex min-h-screen flex-col items-center">
      <div className="flex w-full max-w-[1000px] flex-1 flex-col">
        <NavBar visible />
        <div className="flex flex-col gap-6 px-4 py-4 lg:px-10">
          <p>
            Welcome to Republic of Rome Online. This is a free multiplayer
            adaptation of the board game{" "}
            <a
              className="text-blue-600 hover:underline"
              href="https://boardgamegeek.com/boardgame/1513"
            >
              The Republic of Rome
            </a>{" "}
            for 3 to 6 players.
          </p>
          <p>
            This semi-cooperative political strategy game is set in the
            historical Roman Republic. Rival factions of senators compete for
            influence and prestige within a corrupt oligarchy, while
            collectively holding together a republic perpetually on the brink of
            collapse. If Rome falls, everyone loses — though that never seems to
            stop factions from stabbing each other in the back anyway, sometimes
            literally. Every faction is ultimately angling for the same thing:
            seizing power as Rome&apos;s first emperor in all but name.
          </p>
          <div className="my-2 flex flex-col gap-4 rounded bg-neutral-100 px-8 py-6 text-sm">
            <h2 className="text-lg">Before you play</h2>
            <ul className="flex list-disc flex-col gap-2 pl-8">
              <li>
                Sign in to browse and create games (a minimum of 3 players is
                required to start)
              </li>
              <li>
                For the best experience, play with 5 or 6 players in real time
                while on a Discord voice call
              </li>
              <li>
                The early republic scenario is the only one currently available,
                and it&apos;s playable but not yet feature-complete. See the{" "}
                <a
                  className="text-blue-600 hover:underline"
                  href="https://github.com/iamlogand/republic-of-rome-online?tab=readme-ov-file#feature-checklist-early-republic-scenario"
                >
                  feature checklist
                </a>{" "}
                for a full breakdown.
              </li>
              <li>
                The UI is functional but bare-bones for now. A full visual
                overhaul, including tooltips, icons, artwork, and a proper color
                scheme, is planned for a later stage of development.
              </li>
              <li>
                Bugs are expected, so please report any you encounter via{" "}
                <a
                  className="text-blue-600 hover:underline"
                  href="https://github.com/iamlogand/republic-of-rome-online/issues"
                >
                  GitHub Issues
                </a>
              </li>
            </ul>
          </div>
        </div>
        <div className="mt-auto flex justify-center">
          <p className="px-4 py-4 text-center text-sm text-neutral-600 lg:px-10">
            This is an open source project available on{" "}
            <a
              className="text-blue-600 hover:underline"
              href="https://github.com/iamlogand/republic-of-rome-online"
            >
              GitHub
            </a>
            . Not affiliated with or endorsed by Avalon Hill or Hasbro.
          </p>
        </div>
      </div>
    </div>
  )
}

export default Home
