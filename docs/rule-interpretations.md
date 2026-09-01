# Rule interpretations

This document records potentially controversial rule interpretations made for this implementation of Republic of Rome. All interpretations are based on the Valley Games Living Rules v1.07B, which is probably the most comprehensive rule set that exists for Republic of Rome.

## Mortality phase

## Revenue phase

## Forum phase

## Population phase

## Senate phase

### Minimum force (rule 1.09.643)

When a presiding magistrate wants to propose deploying forces or recalling forces that results in a commander fighting a war below minimum force, their consent is required. This raises the question of what happens when a commander doesn't give consent due to minimum force concerns.

The implementation makes two decisions here:

1. The would-be proposal doesn't count as a rejected proposal because it was never actually put to the senate for a vote. This means the presiding magistrate can keep asking the same player for consent to the same proposal.
2. The presiding magistrate's requests are public so everyone will see who is responsible for slowing the game down.

### Assassinations during a special major prosecution (rule 1.09.74)

A special major prosecution suspends whatever the senate was doing and holds its own vote, so an assassination attempted during it would have to suspend a suspension — and a second caught assassin would call for a special major prosecution nested inside the first one.

The implementation forbids assassination attempts for the duration of a special major prosecution. Attempts are available again as soon as the verdict is in and the senate returns to the business it was interrupted from.

### A Censor outside Rome takes no part in a special major prosecution (rule 1.09.74)

The rules name the Censor as presiding magistrate for a special major prosecution, and as the only senator the mob can reach on a popular appeal with no prosecutor, without saying where he has to be. Everywhere else the senate only involves senators who are in Rome — only senators in Rome may be prosecuted, and a faction leader escapes the trial entirely by being away from Rome.

The implementation reads the Censor the same way. A Censor outside Rome neither takes over the meeting nor is exposed to the mob, so the current presiding magistrate runs the trial and the chit draw kills nobody.

## Combat phase

## Revolution phase
