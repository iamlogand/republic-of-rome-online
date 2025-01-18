const Home = async () => {
  return (
    <div className="px-6 py-4 max-w-[800px]">
      <p className="mb-4">
        I was developing an online adaptation of the classic strategy board game{" "}
        <a
          className="text-blue-500 underline"
          href="https://boardgamegeek.com/boardgame/1513"
        >
          The Republic of Rome
        </a>
        . While I believe the project had great potential, after two years of
        work, I&apos;ve decided to stop development. The scope of the project
        proved to be more ambitious than I could manage with the time available.
      </p>
      <p className="mb-4">
        This project is open source, and the code is still available on{" "}
        <a
          className="text-blue-500 underline"
          href="https://github.com/iamlogand/republic-of-rome-online"
        >
          GitHub
        </a>
        . It is licensed under the MIT license, so anyone is free to use,
        modify, or build upon it for any purpose.
      </p>
      <p className="mb-4">
        Thank you to everyone who showed interest and supported the project.
      </p>
      <ul></ul>
    </div>
  )
}

export default Home
