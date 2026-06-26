# Republic of Rome Online

An online multiplayer adaptation of the board game [The Republic of Rome](https://boardgamegeek.com/boardgame/1513/republic-rome) for 3 to 6 players, playable in the browser. Play it at [www.roronline.com](https://www.roronline.com).

The Republic of Rome is a semi-cooperative political strategy game set in the historical Roman Republic. Rival factions of senators compete for influence and prestige within a corrupt oligarchy, while collectively holding together a republic perpetually on the brink of collapse. If Rome falls, everyone loses, though that never seems to stop factions from stabbing each other in the back anyway, sometimes literally. Every one of them is ultimately angling for the same thing: seizing power as Rome's first emperor in all but name and bringing the Republic to an end on their own terms.

Republic of Rome Online is a free, non-commercial hobby project made purely for the enjoyment of fans of the game. It runs on a small budget and is designed to stay that way. It will never have ads or a subscription. It is licensed under the MIT license, so anyone is free to use, modify, or build upon it for any purpose.

The Republic of Rome is owned by Avalon Hill, a subsidiary of Hasbro. This project is not affiliated with or endorsed by them.

## Tech stack

- **Frontend** — Next.js (React), deployed to AWS Amplify
- **Backend** — Django REST API with WebSocket support via Django Channels and Daphne, deployed to AWS Elastic Beanstalk
- **Database** — PostgreSQL on Amazon RDS
- **Cache / message broker** — Redis

## Contributing

- [How it works](docs/how-it-works.md) — architecture overview for new contributors
- [Setup a development environment](docs/setup-development-environment.md) — get the project running locally
- [Infrastructure](docs/infrastructure.md) — production deployment details
- [Rule interpretations](docs/rule-interpretations.md) — how ambiguous rules are handled
- [Terminology changes](docs/terminology-changes.md) — vocabulary that differs from the original game
- [Orthographic guidelines](docs/orthography.md) — spelling and capitalization conventions

Bug reports and feature suggestions are welcome via [GitHub Issues](https://github.com/iamlogand/republic-of-rome-online/issues).

## Project status

Republic of Rome Online has been in active development for several years, and there's plenty more to come. The immediate goal is to make the early republic scenario feature-complete, then a usability overhaul (UI layout, quality of life improvements, icons and artwork), and eventually support for the mid and late republic scenarios.

The checklist below tracks implementation of the **early republic scenario** — the introductory scenario from the original game and the first target for a complete playthrough. The original game has three scenarios in total, each adding more complexity.

### Feature checklist (early republic scenario)

- [x] Initial phase
  - [x] Temporary rome consul
  - [x] Select faction leader
  - [x] Play statesmen
  - [x] Play concessions
- [x] Mortality phase
  - [x] Mortality
  - [ ] Faction elimination
- [ ] Revenue phase
  - [x] Personal revenue
  - [ ] Provincial spoils
  - [ ] Provincial development
  - [x] State revenue
  - [ ] Rebel maintenance
  - [x] Redistribution
  - [x] Contributions
  - [ ] State debits
    - [x] Active war cost
    - [x] Land bill cost
    - [x] Unit maintenance cost
  - [ ] Returning governors
- [ ] Forum phase
  - [x] Passage of time
  - [ ] Events
    - [ ] Ally deserts
    - [x] Allied enthusiasm
    - [ ] Barbarian raids
    - [x] Drought
    - [ ] Enemy leader dies
    - [ ] Enemy's ally deserts
    - [ ] Epidemic
    - [x] Evil omens
    - [x] Manpower shortage
    - [ ] New alliance
    - [ ] Pretender emerges
    - [ ] Refuge
    - [ ] Rhodian maritime alliance
    - [ ] Storm at sea
    - [ ] Trial of Verres
  - [x] New senator
  - [x] New war
  - [x] New leader
  - [x] Concession card
    - [x] Tax farmers
    - [x] Harbor fees and mining
    - [x] Grains
      - [ ] Famine profiteering
    - [x] Armaments and ship building
    - [x] Land commissioner
  - [x] Statesman card
  - [x] Persuasion attempt
  - [x] Persuasion attempt with seduction
  - [x] Persuasion attempt with blackmail
  - [x] Attract knight
  - [x] Pressure knights
  - [x] Sponsor games
  - [x] Appoint faction leader
  - [x] Initiative auction
  - [ ] Tax farmer destruction
  - [x] Senator revival
  - [x] Leader discard
  - [x] Era ends win
- [ ] Population phase
  - [x] War increases unrest
  - [x] Famine increases unrest
  - [x] State of the republic
  - [x] People revolt
  - [ ] People revolt to rebel end game
- [ ] Senate phase
  - [x] Assassination
  - [ ] Special major prosecution
  - [ ] Repopulate Rome
  - [x] Vote
  - [x] Buy votes
  - [x] Split vote
  - [x] Unanimous defeat
  - [x] Proposal via tribune
  - [x] Veto via tribune
  - [ ] Graft
  - [ ] Murder tribune
  - [ ] Mob incited to violence
  - [x] Consul election
  - [ ] Automatic appointment of consuls
  - [x] Consul roles
  - [x] Outgoing officers
  - [x] Appoint Dictator
  - [x] Dictator election
  - [x] Appoint Master of Horse
  - [x] Censor election
  - [x] Automatic appointment of censor
  - [x] Prosecution
  - [x] Popular appeal
  - [ ] Governor election
  - [ ] Governor recall
  - [x] Award concessions
  - [x] Pass land bill
  - [x] Repeal land bill
  - [x] Raise forces
  - [ ] Eliminate forces
  - [x] Deploy forces
  - [x] Reinforce forces
  - [x] Minimum force commander consent
  - [x] Replace proconsul
  - [x] Recall forces
  - [ ] Elect consul for life
  - [ ] Appoint consul for life
  - [x] Close senate
  - [x] Automatic recall
- [ ] Combat phase
  - [x] War strength multiplication
  - [x] Battle
  - [x] Commander continues attack
  - [ ] New province
  - [ ] Capture
  - [ ] Civil war battle
  - [ ] Rebel attacks war
  - [ ] Rebel wins game
  - [x] Unprosecuted wars
- [ ] Revolution phase
  - [x] Trade cards
  - [x] Play statesmen
  - [x] Play concessions
  - [ ] Discard faction card
  - [ ] Check rebel legions
  - [ ] Declare civil war
  - [ ] Consul for life wins game
- [x] State bankruptcy
- [ ] State bankruptcy to rebel end game
- [x] Military overwhelmed
- [X] Influence peddling
- [x] Combat calculator tool
