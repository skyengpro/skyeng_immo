# Flux d'utilisation de l'application immobilière

Ce document décrit comment chaque rôle utilise l'application dans les deux modes opérationnels définis dans EP-01. Les écrans à implémenter sont présentés à part, dans `ecrans-immo-mode-a.mermaid` et `ecrans-immo-mode-b.mermaid`.

Le paiement en ligne n'est pas couvert. Tant qu'il n'est pas conçu, un paiement reçu (espèces, virement, MoMo hors application) est enregistré par le gestionnaire dans le desk.

## Rôles et accès

| Rôle | Mode A : Sky owns an instance | Mode B : A customer owns an instance |
| --- | --- | --- |
| System Manager / Property Manager | L'équipe Sky. Desk uniquement. | L'équipe du client. Desk et application. |
| Bailleur | Chaque bailleur du site. Application uniquement, en consultation. | Un propriétaire tiers dont le client gère les biens. Application uniquement, en consultation. Ce rôle est facultatif. |
| Locataire | Application uniquement. | Application uniquement. |

Dans les deux modes, une seule application sert tous les rôles. Le rôle de la personne connectée décide de l'écran d'accueil et des biens visibles :

- le gestionnaire voit tous les biens du site ;
- le bailleur voit les biens dont il est propriétaire (`unit_owner`), avec leurs lots ;
- le locataire voit les biens de ses baux.

Toute la gestion se fait dans le desk : bailleurs, biens, baux, locataires, comptes et paiements. Dans l'application, la seule action d'écriture est la demande de maintenance du locataire.

## 1. Mise en service

### 1.1 Mode A : Sky inscrit un bailleur

Les bailleurs n'ont pas d'instance à eux. L'équipe Sky les inscrit sur le site Sky, sous la société unique de Sky.

```mermaid
sequenceDiagram
    autonumber
    actor S as Équipe Sky (desk)
    participant D as Site Sky
    actor B as Bailleur
    actor L as Locataire

    S->>D: Crée le bailleur (Customer)
    S->>D: Crée ses biens dans l'arbre (immeuble, puis lots), avec le bailleur comme propriétaire
    S->>D: Crée chaque bail, avec son locataire, son loyer et son échéancier
    S->>D: Crée le compte du bailleur et ceux de ses locataires
    D-->>B: E-mail d'invitation
    D-->>L: E-mail d'invitation
    B->>D: Ouvre le lien et choisit son mot de passe
    D-->>B: L'application s'ouvre sur ses biens
    L->>D: Ouvre le lien et choisit son mot de passe
    D-->>L: L'application s'ouvre sur son logement
    Note over S,L: Un second bailleur suit le même parcours sur le même site. Aucun des deux ne voit les biens de l'autre.
```

L'inscription commence comme une liste de contrôle manuelle pour l'équipe Sky.

### 1.2 Mode B : le client met en place son instance

Le client reçoit son propre site. Son équipe y saisit ses biens. Si le client gère aussi les biens de propriétaires tiers, il peut leur ouvrir un accès bailleur.

```mermaid
sequenceDiagram
    autonumber
    actor G as Équipe du client (desk)
    participant D as Site du client
    actor B as Bailleur tiers
    actor L as Locataire

    G->>D: Crée ses biens dans l'arbre, avec la société du client comme propriétaire
    opt Biens gérés pour un propriétaire tiers
        G->>D: Crée le bailleur tiers (Customer) et lui rattache ses biens
        G->>D: Crée le compte du bailleur tiers
        D-->>B: E-mail d'invitation
    end
    G->>D: Crée chaque bail, avec son locataire, son loyer et son échéancier
    G->>D: Crée les comptes des locataires
    D-->>L: E-mail d'invitation
    L->>D: Ouvre le lien et choisit son mot de passe
    D-->>L: L'application s'ouvre sur son logement
```

Le propriétaire est toujours renseigné sur chaque bien, même quand c'est la société du client elle-même. Les règles de visibilité restent ainsi les mêmes dans les deux modes.

## 2. Facturation et paiement (les deux modes)

PropMS génère les factures à partir de l'échéancier de chaque bail. Le gestionnaire enregistre les paiements reçus. L'application ne fait que montrer le résultat.

```mermaid
sequenceDiagram
    autonumber
    participant D as Site
    actor G as Gestionnaire (desk)
    actor L as Locataire
    actor B as Bailleur

    D->>D: À la date de l'échéancier, génère la facture et la valide
    D-->>L: Rappel par e-mail quelques jours avant l'échéance
    alt Le locataire paie
        L->>G: Paie hors application (espèces, virement, MoMo)
        G->>D: Enregistre le paiement sur la facture
        D-->>L: Reçu par e-mail
        D-->>B: Avis de paiement par e-mail
        Note over L,B: Dans l'application, la facture passe à « payée » et le reçu est téléchargeable.
    else Aucun paiement à l'échéance
        Note over D,B: La facture reste impayée. Elle apparaît dans les factures en retard sur l'accueil du bailleur et dans le solde dû du locataire.
    end
```

En mode B, le bailleur n'existe que pour les biens gérés pour un tiers. Pour les biens du client lui-même, l'avis de paiement va au gestionnaire.

## 3. Consultation par le bailleur (les deux modes)

Le bailleur consulte seulement. Il ne saisit ni paiement, ni locataire, ni bail.

```mermaid
sequenceDiagram
    autonumber
    actor B as Bailleur
    participant A as Application
    participant D as Site

    B->>A: Se connecte
    A->>D: Demande les biens visibles
    D-->>A: Rôle Bailleur : ses biens et leurs lots
    A-->>B: Accueil : biens, locataires, encaissé du mois, total impayé, factures en retard
    B->>A: Ouvre « Mes biens »
    A-->>B: Arbre par immeuble. Pour chaque lot : statut, locataire, loyer
    B->>A: Ouvre un bien
    A-->>B: Bail en cours, locataires et date d'entrée, caution, échéancier, factures, anciens baux
    B->>A: Ouvre un locataire
    A-->>B: Conditions du bail, paiements (dates et montants), factures encore dues
    B->>A: Télécharge une facture
    A-->>B: PDF de la facture
    Note over B,D: Depuis l'accueil, une facture en retard ouvre directement la fiche du locataire concerné.
```

## 4. Gestionnaire dans l'application (mode B)

En mode B, l'équipe du client peut ouvrir l'application pour consulter ses biens loin du bureau. Elle voit les mêmes écrans que le bailleur, mais sur tous les biens du site.

```mermaid
sequenceDiagram
    autonumber
    actor G as Gestionnaire du client
    participant A as Application
    participant D as Site du client

    G->>A: Se connecte avec son compte du desk
    A->>D: Demande les biens visibles
    D-->>A: Rôle Property Manager : tous les biens du site
    A-->>G: Accueil : totaux sur tous les biens
    G->>A: Ouvre « Mes biens »
    A-->>G: Arbre de tous les biens, regroupé par bailleur quand le client gère pour des tiers
    G->>A: Ouvre un bien, puis un locataire
    A-->>G: Mêmes fiches que pour le bailleur
    Note over G,D: Pour modifier quoi que ce soit, le gestionnaire passe par le desk, avec le même compte.
```

En mode A, l'équipe Sky travaille dans le desk et n'a pas besoin de l'application.

## 5. Locataire (les deux modes)

Le locataire consulte son bail et ses factures. Il peut aussi signaler un problème dans son logement.

```mermaid
sequenceDiagram
    autonumber
    actor L as Locataire
    participant A as Application
    participant D as Site
    actor G as Gestionnaire (desk)

    L->>A: Se connecte
    A->>D: Demande ses baux
    D-->>A: Rôle Locataire : son logement et ses baux
    A-->>L: Accueil : solde dû, prochaine échéance, dernière demande de maintenance
    L->>A: Ouvre « Mon bail »
    A-->>L: Logement, dates, loyer et rythme, caution, échéancier avec le statut de chaque ligne
    L->>A: Ouvre « Factures et reçus »
    A-->>L: Factures à payer et payées
    L->>A: Télécharge une facture ou un reçu
    A-->>L: PDF
    L->>A: Crée une demande de maintenance, avec une photo
    A->>D: Enregistre la demande sur le bien concerné
    D-->>G: La demande apparaît dans le desk
    G->>D: Traite la demande et met à jour son statut
    L->>A: Ouvre « Maintenance »
    A-->>L: Liste de ses demandes et leur statut
```

## 6. Ce qui diffère d'un mode à l'autre

| Point | Mode A | Mode B |
| --- | --- | --- |
| Qui tient le desk | L'équipe Sky | L'équipe du client |
| Société ERPNext | Une seule, celle de Sky, pour tous les bailleurs | Celle du client |
| Bailleurs | Tous les propriétaires du site | Seulement les propriétaires tiers, s'il y en a |
| Gestionnaire dans l'application | Non | Oui, sur tous les biens, regroupés par bailleur |
| Écrans bailleur et locataire | Identiques | Identiques |
