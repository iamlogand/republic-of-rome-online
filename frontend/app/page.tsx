const Home = async () => {
  return (
    <div className="px-6 py-4 max-w-[800px]">
      <p className="mb-4">
        I&apos;m developing an online adaptation of the classic strategy board
        game{" "}
        <a
          className="text-blue-600 hover:underline"
          href="https://boardgamegeek.com/boardgame/1513"
        >
          The Republic of Rome
        </a>
        .
      </p>
      <p className="mb-4">
        This project is open source, and the code is available on{" "}
        <a
          className="text-blue-600 hover:underline"
          href="https://github.com/iamlogand/republic-of-rome-online"
        >
          GitHub
        </a>
        . It is licensed under the MIT license, so anyone is free to use,
        modify, or build upon it for any purpose.
      </p>
      <h2 className="text-xl py-4">About the game</h2>
      <p className="mb-4 italic">
        The Republic of Rome is an abstraction of over 250 years of history. It
        simulates the politics of the Roman Senate during the republic. The
        players take the part of various factions vying for the control of the
        senate. They control the various powerful families of the time, who
        compete for state offices, military command, economic concessions and
        new adherents. To win the player must get their faction to become the
        most powerful in Rome. While doing this, however, a balance must be
        maintained. A hostile world situation, and the vagaries of the public of
        Rome means that the players must also cooperate so that Rome herself
        doesn&apos;t go down under this pressure. If Rome does not last, neither
        does the senate, and all players lose!
      </p>
      <p className="mb-4 italic">
        Players make proposals to the Senate which other players then vote on. A
        player&apos;s ability to make proposals is determined by which Offices
        his/her Senators hold. A player&apos;s influence in votes is determined
        by the number of Senators they have recruited and the level of influence
        those Senators have obtained. Proposals may include assigning Senators
        to govern provinces (generating revenue), recruiting an army to fight an
        external foe, addressing the concerns of the Roman people, assigning
        offices or prosecuting previous office holders. Players have to
        co-operate to overcome the various threats that the game sends against
        Rome (wars, famine, unrest, bankruptcy) whilst working to build their
        own Senators&apos; and Generals&apos; positions and undermine that of
        their opponents. A powerful General or an influential Senator may become
        Emperor (thus winning the game) but equally may suddenly fall to the
        plague or an assassin&apos;s blade.
      </p>
    </div>
  )
}

export default Home
