---
name: novia-veille
description: "Veille IMMO9 : marché du neuf, réglementaire et fiscal, presse nationale et locale (Toulouse, Bordeaux, Montpellier, Nantes, Rennes), concurrents, questions Reddit et forums, tendances. Lecture des sources autorisées (knowledge/sources-veille.json) par flux RSS avec dédoublonnage (scripts/veille_rss.py), repérage Reddit (scripts/reddit_scan.py), digest court dans le groupe et cumul dans learning/VEILLE.md. Auto, quotidien et hebdomadaire."
metadata: {"openclaw": {"emoji": "🔎", "requires": {"bins": ["python3"]}}}
---

# novia-veille : lire ce qui compte, ne rien répéter, tout sourcer

## Digest du matin (cron `veille-matin`, lundi à vendredi)
1. `python3 skills/novia-veille/scripts/veille_rss.py --days 2` : lit les sources RSS de `knowledge/sources-veille.json`, filtre avec `knowledge/veille-keywords.json`, écarte ce qui a déjà été vu (`state/veille-seen.json`), imprime les nouveautés groupées par thème et les ajoute à `learning/VEILLE.md`.
2. Pour les sources sans flux (pages « actualités » officielles), `web_fetch` de la page selon la fréquence indiquée ; ne retenir que ce qui est daté.
3. `python3 skills/novia-veille/scripts/reddit_scan.py --days 2` : questions récentes des subreddits et mots-clés configurés. Pour chaque question pertinente, un brouillon de réponse utile (voir `novia-editorial`).
4. Rédiger le digest (3 à 6 lignes, format `rules/format-reponses.md`) : chaque ligne = fait daté + source + ce qu'on en fait (angle, post proposé, rien). S'il n'y a rien : `NO_REPLY`.
5. Un item réglementaire ou fiscal repris dans un contenu doit être confirmé sur une source « officiel » avant rédaction.

## Rapport hebdomadaire (cron `veille-hebdo`, vendredi)
- Concurrents (`knowledge/concurrents.json`) : leurs publications publiques de la semaine (sujets, formats, fréquence), lues via leurs pages ou comptes publics ; pas de scraping intrusif.
- Tendances : formats et sujets qui reviennent dans la veille de la semaine, hashtags observés, questions récurrentes.
- Google Trends et « People Also Ask » : si un fournisseur est configuré (voir `connectors/README.md`), sinon via `web_search` sur les mots-clés de la semaine.
- Sortie : 5 à 8 lignes dans le groupe, détail dans `learning/VEILLE-HEBDO.md`.

## Mensuel
- Manques Wikipédia (opportunités de sourçage) : lecture des pages liées aux villes et au logement neuf, repérage des sections « à sourcer » ; rapport court, aucune modification de Wikipédia par l'agent.

## Règles
- Sources hors liste : proposées à l'équipe, jamais citées dans un contenu.
- Chaque item porte URL et date ; sans date, il ne nourrit pas un chiffre.
- Le script ne fait aucune recherche payante ; `deep-search` et `last30days`, s'ils sont installés, servent aux recherches approfondies demandées par l'équipe.
