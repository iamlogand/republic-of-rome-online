# Rule interpretations

This document records potentially controversial rule interpretations made for this implementation of Republic of Rome. All interpretations are based on the Valley Games Living Rules v1.07B, which is probably the most comprehensive rule set that exists for Republic of Rome.

## Mortality phase

## Revenue phase

## Forum phase

### A leader is matched with every active war in his series (rule 1.07.341)

"If, while an Inactive or Active War is in play, a matching Leader card is drawn, the Leader is immediately placed with the War" (1.07.341) describes the case where one war of the series is in play. It does not tie the leader to that card for the rest of the game.

The implementation reads a leader as matched with every active war in his series. Hannibal drawn while only the 1st Punic War is active is matched with the 1st; when the 2nd Punic War becomes active a turn later he is matched with both, and the 2nd Punic War's tax farmer roll (1.07.8) gains Hannibal's second roll from that turn on.

`EnemyLeader` therefore records only whether a leader is active within his series, with no link to a particular war.

### Destroying a concession clears its corrupt marker (rule 1.07.321)

The corrupt bar is printed on the concession card, so when the card is destroyed and moved to the Curia (1.07.321) the evidence goes with it. A senator who collected revenue on the mining concession and then lost it to a natural disaster in the same forum phase is not liable to a minor prosecution for it in the senate phase that follows.

This matches the treatment of a senator's death, where his concessions return to the forum and his corrupt markers are cleared (1.05.3).

## Population phase

## Senate phase

### Minimum force (rule 1.09.643)

When a presiding magistrate wants to propose deploying forces or recalling forces that results in a commander fighting a war below minimum force, their consent is required. This raises the question of what happens when a commander doesn't give consent due to minimum force concerns.

The implementation makes two decisions here:

1. The would-be proposal doesn't count as a rejected proposal because it was never actually put to the senate for a vote. This means the presiding magistrate can keep asking the same player for consent to the same proposal.
2. The presiding magistrate's requests are public so everyone will see who is responsible for slowing the game down.

## Combat phase

### A land victory needs the enemy fleets beaten first (rule 1.10.4)

"A Land 'Victory' [...] eliminates the War" (1.10.4) but a war that also shows a fleet strength requires two battles, and "the enemy Fleet Strength must be defeated before his land Forces may be attacked" (1.10.12). The implementation reads a land victory as ending the war only once the naval side has already been beaten, so a commander who wins the land battle of a war whose fleets are still at sea has not gained a Land Victory.

This decides who may declare himself in revolt, because only "a Commander who gained a Land Victory in this turn" is offered that choice (1.11.3).

## Revolution phase

### A Primary Rebel who loses his army survives, and still blocks other revolts (rule 1.11.372)

§1.11.371 says a rebel "is considered defeated (i.e., the Revolt fails)" if all his legions are destroyed through combat losses, and §1.11.372 says that when a revolt fails "all Secondary Rebels are killed". Neither kills the Primary Rebel, who is killed by name only on a Senate Victory or by a Mortality Chit.

The implementation therefore leaves him alive with his rebel marker: no offices, no concessions, no revenue, and no army. §1.11.3 says nobody else may revolt "until that Rebel has been killed", so he goes on blocking every other faction's revolt until he dies.

### A land victor declares after cards are played (rule 1.11.3)

The Declaration of Civil War is the third step of the Revolution Phase, after Play Statesmen/Concessions (1.11.1) and Excess Faction Cards (1.11.2), so the implementation holds the victorious commander in the field through card trading and keeps his army with him until he decides.

Until then he is neither a Proconsul, since only "a Commander who survives a non-victorious battle" becomes one (1.10.8), nor subject to any senate proposal, since the Senate Phase has already passed. His Master of Horse, if he has one, stays with him rather than returning to Rome as he would if the Dictator had become a Proconsul (1.10.8), because the Master of Horse may join the revolt (1.11.32) and may fund the loyalty rolls (1.11.31).
