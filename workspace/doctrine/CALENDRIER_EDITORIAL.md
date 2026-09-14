# CALENDRIER_EDITORIAL.md : Marronniers, salons, échéances

> Les dates vivent dans `knowledge/calendrier-marronniers.json` (lu par `novia-calendrier`). Ce fichier explique la logique. Les événements récurrents sont connus ; les dates d'édition (salons) sont à confirmer chaque année par l'équipe, le script les signale comme « à confirmer » tant qu'elles ne portent pas `confirmed: true`.

## Trois familles
1. **Échéances réglementaires et fiscales** : loi de finances (automne, vote en décembre), début d'année (entrée en vigueur des mesures), déclaration de revenus (avril à juin), taxe foncière (octobre), échéances DPE et rénovation, dates de fin ou de début de dispositifs. Chaque échéance donne un contenu « ce qui change » deux à quatre semaines avant.
2. **Rythme du marché** : publication mensuelle des taux (début de mois), chiffres trimestriels des notaires et de la promotion (fédérations), rentrée de septembre, creux d'août, fin d'année.
3. **Événements et salons** : salons de l'immobilier dans chaque ville, salons de l'investissement, journées portes ouvertes d'IMMO9, livraisons de programmes, lancements commerciaux.

## Comment le calendrier nourrit la production
- `comite-editorial` (lundi) lit les 30 prochains jours et propose les pièces à préparer.
- `calendrier-preview` (le 25) annonce le mois suivant.
- Une échéance importante déclenche une séquence : annonce (J-21), pédagogie (J-10), rappel (J-2), bilan (J+7).

## Ce que l'équipe complète à l'acte 3
- Dates d'édition des salons de l'année (avec `confirmed: true`).
- Livraisons et lancements de programmes (avec la ville).
- Journées portes ouvertes, événements partenaires.
- Congés et fermetures (pas de publication programmée pendant).
