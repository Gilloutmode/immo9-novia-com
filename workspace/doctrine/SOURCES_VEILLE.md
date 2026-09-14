# SOURCES_VEILLE.md — Ce que Novia Com a le droit de lire et de citer

> Liste machine dans `knowledge/sources-veille.json` (nom, URL, type, flux RSS s'il existe, fréquence de lecture, confiance). Ce fichier explique les niveaux et les règles. L'équipe ajoute ses sources locales à l'acte 3.

## Niveaux de confiance
- **officiel** : textes et administrations (Légifrance, service-public.fr, BOFiP, ministères, ANIL, Banque de France, INSEE, ADEME). Une information réglementaire ou fiscale doit venir de ce niveau avant d'être publiée.
- **professionnel** : fédérations et observatoires (promotion immobilière, notaires, courtiers, observatoires du crédit). Chiffres de marché utilisables avec source et date.
- **presse** : presse nationale et locale spécialisée. Utilisable pour la veille et les angles ; un chiffre repris de la presse est recoupé quand il conditionne un contenu.
- **social** : Reddit, forums, réseaux. Utilisable pour repérer les questions et les tendances ; jamais comme source d'un fait.

## Règles
- Une source hors liste n'est pas citée dans un contenu public. Elle peut être proposée à l'équipe pour ajout.
- Les flux RSS sont lus par `veille_rss.py` ; les pages sans flux sont lues par `web_fetch` selon la fréquence indiquée.
- Le script marque les URL déjà vues (`state/veille-seen.json`). Un item réapparaît seulement s'il a changé.
- Presse locale par ville : Toulouse, Bordeaux, Montpellier, Nantes, Rennes. À compléter par l'équipe avec les titres qu'elle suit.
- Concurrents : liste dans `knowledge/concurrents.json` (nom, site, comptes). Surveillance de leurs publications publiques uniquement, pour le rapport hebdomadaire ; jamais de contenu qui les cite sans accord de David.
