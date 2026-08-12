# SkyEng Immo

Domain model for property management that PropMS does not provide:

| DocType | Purpose |
|---|---|
| `Occupant` | Who actually lives in a unit - identity, piece d'identite, dates d'entree/sortie |
| `Visitor Log` | Registre des visiteurs pour la guerite: entree/sortie, identite, hote, vehicule |

PropMS models the *lease* (one Customer per unit). It has no notion of the
people in the unit, so access control and gate registers are impossible on it
alone. This app adds that layer without modifying PropMS.
