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

### Assassinations during a special major prosecution (rule 1.09.74)

Nothing in the rules forbids an assassination attempt during a special major prosecution, so one is allowed. Alan Richbourg settled the two questions this raises in [a thread on BoardGameGeek](https://boardgamegeek.com/thread/3544272/would-you-allow-assassiation-during-special-major).

An attempt is carried out in one piece: the assassin card, the dice roll, the secret bodyguard and the death of the assassin or the victim all happen before a second "die swine" can take effect. No attempt can be announced while another is being resolved.

The prosecutions those attempts bring about do queue, and are held oldest first. A trial interrupted by an assassination picks up where it left off, and the proposal suspended by the first trial only returns to the floor once every trial has been resolved. The senate can therefore have three things outstanding at once: the trial on the floor punishing the first caught assassin, a trial queued behind it punishing the second, and the proposal the first trial suspended.

A faction still gets only one attempt per turn and can still only be targeted once per turn, so a faction leader is never tried twice, and the faction on trial cannot strike again to save him.

### An accused who dies has no trial (rule 1.09.74)

An assassinated faction leader is replaced by his heir, who did not order the killing the senate is trying his predecessor for. The implementation cancels a special major prosecution whose accused dies before the verdict, and moves on to the next trial or back to the suspended proposal.

### A Censor outside Rome takes no part in a special major prosecution (rule 1.09.74)

The rules name the Censor as presiding magistrate for a special major prosecution, and as the only senator the mob can reach on a popular appeal with no prosecutor, without saying where he has to be. Everywhere else the senate only involves senators who are in Rome.

Only senators in Rome may be prosecuted, and a faction leader escapes the trial entirely by being away from Rome.

The implementation reads the Censor the same way. A Censor outside Rome neither takes over the meeting nor is exposed to the mob, so the current presiding magistrate runs the trial and the chit draw kills nobody.

## Combat phase

## Revolution phase
