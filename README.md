# Republic of Rome Online

A online adaptation of a board game called [The Republic of Rome](https://boardgamegeek.com/boardgame/1513/republic-rome). The production version of this site can be found at [www.roronline.com](https://www.roronline.com). For more info, including a guide for setting up a local development environment, check out the [wiki](https://github.com/iamlogand/republic-of-rome-online/wiki).

## Attempt 2

Attempt 1 of Republic of Rome Online was developed in 2023 and 2024. However, in early 2025 I realized that I'd spent too much time on the UI; this included things like logos, artwork, notifications, and helper text. Developing these unnecessary UI features was fun for a while, but I increasingly felt that the project would never be completed because of how many peripheral features I had to account for each time I added a new core feature.

To streamline development, I started over. Attempt 2 has a much simpler UI and simpler backend structures for managing game logic, allowing new features to be developed far quicker than was possible in attempt 1. I'm focusing on getting the game into a playable state as quickly as possible. The UI for Attempt 2 is plainer, less interesting, and less intuitive than Attempt 1’s, but a finished game is better than an unfinished one with nice aesthetics.

### Feature checklist (early republic scenario)

- [ ] Initial phase
  - [x] Temporary rome consul
  - [x] Select faction leader
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
  - [ ] Returning governors
- [ ] Forum phase
  - [ ] Passage of time
  - [ ] Events
    - [ ] Ally deserts
    - [ ] Allied enthusiasm
    - [ ] Barbarian raids
    - [ ] Drought
    - [ ] Enemy leader dies
    - [ ] Enemy's ally deserts
    - [ ] Epidemic
    - [ ] Evil omens
    - [ ] Internal disorder
    - [ ] Manpower shortage
    - [ ] New alliance
    - [ ] Pretender emerges
    - [ ] Refuge
    - [ ] Rhodian maritime alliance
    - [ ] Storm at sea
    - [ ] Trial of Verres
  - [ ] New senator
  - [ ] New war
  - [ ] New bequest
  - [ ] New leader
  - [ ] Persuasion attempt
  - [ ] Persuasion attempt with seduction
  - [ ] Persuasion attempt with blackmail
  - [x] Attract knight
  - [ ] Pressure knights
  - [x] Sponsor games
  - [x] Appoint faction leader
  - [x] Initiative auction
  - [ ] Major corruption
  - [ ] Tax farmer destruction
  - [ ] Concession revival
  - [ ] Senator revival
  - [ ] Leader discard
  - [ ] Era ends win
- [ ] Forum phase
  - [ ] War increases unrest
  - [ ] Drought increases unrest
  - [ ] State of the republic
  - [ ] People revolt
  - [ ] People revolt to rebel end game
- [ ] Senate phase
  - [ ] Assassination
  - [ ] Special major prosecution
  - [ ] Repopulate Rome
  - [ ] Vote
  - [ ] Proposal via tribune
  - [ ] Veto via tribune
  - [ ] Graft
  - [ ] Murder tribune
  - [ ] Mob incited to violence
  - [ ] Consul election
  - [ ] Consul roles
  - [ ] Outgoing officers
  - [ ] Appoint Dictator
  - [ ] Dictator election
  - [ ] Appoint Master of Horse
  - [ ] Censor election
  - [ ] Appoint Censor
  - [ ] Prosecution
  - [ ] Governor election
  - [ ] Governor recall
  - [ ] Assign concessions
  - [ ] Pass land bill
  - [ ] Repeal land bill
  - [ ] Recruit forces
  - [ ] Deploy forces
  - [ ] Recall proconsul
  - [ ] Elect consul for life
  - [ ] Appoint consul for life
  - [ ] Close senate
  - [ ] Automatic recall
- [ ] Combat phase
  - [ ] Battle
  - [ ] Commander continues attack
  - [ ] New province
  - [ ] Civil war battle
  - [ ] Rebel attacks war
  - [ ] Rebel wins game
  - [ ] Send faction card
- [ ] Revolution phase
  - [ ] Play statesmen
  - [ ] Play concessions
  - [ ] Discard faction card
  - [ ] Check rebel legions
  - [ ] Declare civil war
  - [ ] Consul for life wins game
- [ ] State bankruptcy
- [ ] State bankruptcy to rebel end game
- [ ] Influence peddling