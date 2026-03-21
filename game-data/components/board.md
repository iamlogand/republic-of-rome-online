# Board {#board}

[← Components Index](README.md)

## Random Events Table {#board-random-events}

Roll 3d6. Results vary by scenario era.

| 3d6 | Early Republic     | Middle Republic    | Late Republic      |
| --- | ------------------ | ------------------ | ------------------ |
| 3   | Mob Violence       | Pretender          | Epidemic           |
| 4   | Natural Disaster   | Storm at Sea       | Storm at Sea       |
| 5   | Ally Deserts       | Ally Deserts       | Ally Deserts       |
| 6   | Evil Omen          | Natural Disaster   | Pretender          |
| 7   | Refuge             | Mob Violence       | Natural Disaster   |
| 8   | Epidemic           | Internal Disorder  | Mob Violence       |
| 9   | Drought            | Drought            | Drought            |
| 10  | Evil Omens         | Evil Omens         | Evil Omens         |
| 11  | Storm at Sea       | Epidemic           | Internal Disorder  |
| 12  | Manpower Shortage  | Manpower Shortage  | Barbarian Raids    |
| 13  | Allied Enthusiasm  | Barbarian Raids    | Manpower Shortage  |
| 14  | New Alliance       | Allied Enthusiasm  | Trial of Verres    |
| 15  | Rhodian Alliance   | New Alliance       | Allied Enthusiasm  |
| 16  | Enemy Ally Deserts | Enemy Ally Deserts | Enemy Ally Deserts |
| 17  | Enemy Leader Dies  | Trial of Verres    | Enemy Leader Dies  |
| 18  | Trial of Verres    | Rhodian Alliance   | New Alliance       |

## Combat Results Table {#board-combat}

Roll 3d6 + Strength Difference + Commander Military rating − 1 per Evil Omen card in play.

| Modified 3d6\* | Result    | Losses                 |
| -------------- | --------- | ---------------------- |
| ≤ 3            | Defeat    | All                    |
| 4              | Defeat    | 4 Legions and 4 Fleets |
| 5              | Defeat    | 3 Legions and 3 Fleets |
| 6              | Defeat    | 2 Legions and 2 Fleets |
| 7              | Defeat    | 1 Legion and 1 Fleet   |
| 8              | Stalemate | 5 Legions and 5 Fleets |
| 9              | Stalemate | 4 Legions and 4 Fleets |
| 10             | Stalemate | 3 Legions and 3 Fleets |
| 11             | Stalemate | 2 Legions and 2 Fleets |
| 12             | Stalemate | 1 Legion and 1 Fleet   |
| 13             | Stalemate | No Losses              |
| 14             | Victory   | 4 Legions and 4 Fleets |
| 15             | Victory   | 3 Legions and 3 Fleets |
| 16             | Victory   | 2 Legions and 2 Fleets |
| 17             | Victory   | 1 Legion and 1 Fleet   |
| ≥ 18           | Victory   | No Losses              |

\*Combat Result = Strength Difference + 2d6 roll

**Disaster**: Half of all Legions and Fleets (round up)

**Standoff**: Quarter of all Legions an Fleets (round up)

**Defeat/Disaster**: increase Unrest level

## Influence / Popularity Gains / Losses Summary {#board-influence-popularity}

| Gaining Office   | Influence | Notes                               |
| ---------------- | --------- | ----------------------------------- |
| Dictator         | +7        | Eligible: 3 Wars or 1 ≥ 20 Strength |
| Consul           | +5        | Cannot repeat; Elected in pairs     |
| Censor           | +5        | May repeat                          |
| Pontifex Maximus | +5        | Office held for life                |
| Master of Horse  | +3        | Appointed by Dictator               |
| Priest           | +1        | Minor Office; Appointed by Pontifex |

| Losing Office    | Influence | Notes                                |
| ---------------- | --------- | ------------------------------------ |
| Pontifex Maximus | +5        | Requires: 2/3 Vote or two Evil Omens |
| Priest           | −1        | Removed/Reassigned by Pontifex       |

| Other Causes                      | Influence              | Notes                                                   |
| --------------------------------- | ---------------------- | ------------------------------------------------------- |
| Minor conviction                  | −5                     | −5 Pop; Loss of Prior Consul, Concessions               |
| Successful Prosecutor             | +1/2 Lost by defendant | Successful Prosecution, Prior Consul                    |
| Faction Leader of Caught Assassin | −5                     | Faces Special Major Prosecution                         |
| Develop Province                  | +3                     | Flips Province to Developed                             |
| Unanimous Proposal Rejection      | −1                     | May be avoided by stepping down as Presiding Magistrate |
| Contributions Treasury            | +1, +3 or +7           | See Contributions in State Treasury                     |
| Military Victory                  | +1/2 War Strength      | Same Popularity gain                                    |
| Combat losses                     | 0                      | −1 Popularity / 2 Legions lost                          |

| Advocates Advanced Rules | Influence | Notes                    |
| ------------------------ | --------- | ------------------------ |
| Successful Advocate      | +3        | Unsuccessful Prosecution |
| Failed Advocate          | −3        | Successful Prosecution   |
| Failed Prosecutor        | −3        | Unsuccessful Prosecution |

## Population Table {#board-population}

| Modified 3d6\* | Result                          |
| -------------- | ------------------------------- |
| ≥ 18           | −3 Unrest Level                 |
| 17             | −2 Unrest Level                 |
| 16             | −1 Unrest Level                 |
| 10–15          | No Change                       |
| 9              | +2 Unrest Level                 |
| 8              | +3 Unrest Level                 |
| 7              | +3 Unrest Level, MS             |
| 6              | +4 Unrest Level                 |
| 5              | +4 Unrest Level, MS             |
| 4              | +5 Unrest Level                 |
| 3              | +5 Unrest Level, MS             |
| 2              | +5 Unrest Level, NR             |
| 1              | +5 Unrest Level, NR, Mob        |
| 0              | +6 Unrest Level, NR, Mob        |
| < 0            | People Revolt; all players lose |

\*3d6 - Unrest Level + HRAO Popularity

MS = Manpower Shortage

NR = No Recruitment this year

Mob = Senate Attacked, Draw six Mortality Chits

## Unrest Level Adjustments {#board-unrest-adjustments}

| Trigger          | Unrest Change | Phase      |
| ---------------- | ------------- | ---------- |
| Victory          | −1            | Population |
| Defeat           | +2            | Population |
| Disaster         | +1            | Population |
| Drought          | +1            | Population |
| Unprosecuted War | +1            | Population |

## Card Piles {#board-card-piles}

- Forum
- Active Wars
- Unprosecuted Wars
- Imminent Wars
- Inactive Wars
- Draw pile
- Discard pile
- Curia
  - Enemy Leaders
    - Without Matching War in Play; End of Forum Phase: Aging 1d6: 5 or 6 Discards
  - Repopulating Rome
    - If < 8 Senators in Rome: Player with fewest Senators draws one from top of Curia. Ties broken by least influence in Rome
    - End of Forum Phase: Recovery on a 5 or 7 on a 1d6
  - Destroyed Concessions
    - End of Forum Phase: Recovery on a 5 or 6 on a 1d6: Return to Forum for Reassignment

## Popular Appeal Table / Trial Appeal Table {#board-appeal}

Used during a Major Prosecution. The Accused rolls 2d6 + his Popularity.

| 2d6 + Pop. Final Verdict\* | Popular Appeal Result | Trial Result |
| -------------------------- | --------------------- | ------------ |
| ≤ 2                        | Accused Killed\*\*    | −20          |
| 3                          | −16 Votes             | −16          |
| 4                          | −12 Votes             | −12          |
| 5                          | −8 Votes              | −8           |
| 6                          | −4 Votes              | −4           |
| 7                          | No Change             | No Change    |
| 8                          | +4 Votes              | +4           |
| 9                          | +8 Votes              | +8           |
| 10                         | +12 Votes             | +12          |
| 11                         | +16 Votes             | +16          |
| ≥ 12                       | Accused Freed\*\*\*   | +20          |

\*Trial Votes = (Advocate's Oratory = Prosecutor's Oratory + 2D6)

Final Verdict = (Popular Appeal Votes + Accused's Influence + Senate Votes) + Trial Votes

\*\*Draw Mortality Chit(s) vs. Advocate

\*\*\*Draw Mortality Chit(s) vs. Censor/Prosecutor

## Legion Allegiance {#board-legion-allegiance}

| Era             | Loyalty Threshold |
| --------------- | ----------------- |
| Early Republic  | 5–6               |
| Middle Republic | 4–6               |
| Late Republic   | 3–6               |

drm: 1 Talent each

## Land Bills Table {#board-land-bills}

|      | Type I | Type II | Type III |
| ---- | ------ | ------- | -------- |
| Cost | 20T    | 5T/year | 10T/year |

| Pass                       | Type I | Type II | Type III |
| -------------------------- | ------ | ------- | -------- |
| Popularity: Sponsor        | +2     | +2      | +4       |
| Popularity: Cosponsor      | +1     | +1      | +2       |
| Popularity: Voting Against | –1     | –1      | –2       |
| Unrest Level               | −1     | −2      | −3       |

| Repeal                 | Type I | Type II | Type III |
| ---------------------- | ------ | ------- | -------- |
| Popularity: Sponsor    | −2     | −2      | −4       |
| Popularity: Voting For | −1     | −1      | −2       |
| Unrest Level           | +1     | +2      | +3       |

## Games Table {#board-games}

| Type           | Cost | Popularity | Unrest Level |
| -------------- | ---- | ---------- | ------------ |
| Slice and Dice | 7T   | +1         | −1           |
| Blood Fest     | 13T  | +2         | −2           |
| Gladiator Gala | 18T  | +3         | −3           |

## Assassination Table {#board-assassination}

| Modified 1d6 | Result    |
| ------------ | --------- |
| ≥ 5          | Killed    |
| 3–4          | No effect |
| ≤ 2          | Caught    |

## Laws {#board-laws}

Played Law cards are displayed here. Laws may be played anytime during the Senate Phase. They need not be passed by vote or proposed by Presiding Magistrate.

They need not be passed by vote or proposed by Presiding Magistrate unless using the Passing Laws Advanced Rule.

## Voting Summary {#board-voting}

Presiding Magistrate Determines Order

| Category        | Modifier                               |
| --------------- | -------------------------------------- |
| Votes           | +Oratory Rating                        |
| Votes           | +Number of Knights                     |
| Votes           | +1 Talent Bribe from Personal Treasury |
| Battle Votes    | +1 Priest                              |
| Battle Votes    | ×2 Pontifex Maximus                    |
| Consul For Life | +Nominee's Influence                   |
| Prosecution     | +Defendants Influence                  |

## State Revenue {#board-revenue}

| Contributions | Influence |
| ------------- | --------- |
| 10T           | +1        |
| 25T           | +3        |
| 50T           | +7        |

| Current Funds | Cost                     |
| ------------- | ------------------------ |
| Active Wars   | −20T Each                |
| Maintenance   | −2T Each Legion or Fleet |
