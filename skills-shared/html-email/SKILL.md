---
name: html-email
description: Génération d'emails HTML professionnels : mise en forme optimale, lisibilité maximale, rendu Gmail parfait.
---

# SKILL: html-email
> Génération d'emails HTML professionnels : mise en forme optimale, lisibilité maximale, rendu Gmail parfait.

## Quand utiliser ce skill
- Dès que l'utilisateur demande de préparer un email important (business, proposition, dossier, pitch)
- Dès que le contenu est dense (plusieurs sections, chiffres, listes, liens)
- Dès qu'un email HTML doit être produit (newsletter, mail à un partenaire) ; l'envoi passe par l'outil d'emailing d'IMMO9 après « Go publie »

---

## Règles d'or (à respecter ABSOLUMENT)

### 1. Structure HTML
- **TOUJOURS** utiliser des `<table>` pour le layout principal (pas des `<div>` : Gmail les casse)
- **TOUJOURS** inline les styles CSS critiques (Gmail ignore les `<style>` dans le `<head>` sur mobile)
- **Largeur max : 620px** : au-delà ça déborde sur mobile et dans les preview panes
- **Un seul fond blanc** : pas de background coloré sur le body, juste sur le wrapper

### 2. Typographie
- **Body text : 16px, line-height 1.8** : jamais en dessous de 16px, jamais moins de 1.7 d'interligne
- **H2 : 18px bold** avec border-left colorée (3-4px) pour la hiérarchie visuelle
- **H3 : 15-16px bold** : sous-sections
- **Police : Arial, Helvetica, sans-serif** : les seules qui rendent bien partout
- **Couleur body text : #334155** : pas noir pur (#000), trop agressif
- **Couleur titres : #0f172a** : foncé mais pas noir

### 3. Espacement : LA CLÉ DE LA LISIBILITÉ
- **Padding sections : 32px 40px minimum** : l'email doit respirer
- **Margin entre paragraphes : 16-20px** : jamais coller deux blocs
- **Séparateur visuel entre sections** : `<hr>` style léger OU border-top sur le div suivant
- **Chaque section majeure = son propre bloc** avec padding interne

### 4. Mise en forme du contenu dense
- **Callout/citation** : fond #f8f9ff, border-left 3px #6366f1, padding 16px 20px, texte italic
- **Statistiques** : cellules côte à côte (table 3-4 colonnes), fond #f8fafc, chiffre en grand (24px bold #6366f1)
- **Listes** : `<ul>` avec `li { margin-bottom: 10px; font-size: 16px; }`
- **Liens sources** : 13px, couleur #6366f1, sur ligne séparée avec 🔗 emoji
- **Ne jamais faire de tableaux Markdown** : toujours des `<table>` HTML avec style inline

### 5. Ce qui tue la lisibilité (à bannir)
- ❌ Texte trop dense sans espaces entre blocs
- ❌ Font-size < 15px pour le body
- ❌ Line-height < 1.7
- ❌ Paragraphes > 5 lignes sans break
- ❌ Plus de 3 couleurs différentes
- ❌ Background coloré derrière le texte body (sauf callouts ponctuels)
- ❌ Inline `style=""` trop complexes sur les `<a>` : Gmail les strip parfois

### 6. Longueur et densité
- **Pas de condensation** : si le contenu est long, il reste long : mais aéré
- **Chaque section = respiration** : titre → contenu → espace → section suivante
- **Maximum 600 mots par section** avant d'ajouter un séparateur

---

## Template de base (à copier/adapter)

```html
<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Email</title>
<style>
  body { margin:0; padding:0; background:#f0f2f5; font-family:Arial,Helvetica,sans-serif; }
  .wrap { max-width:620px; margin:0 auto; background:#fff; }
  p { font-size:16px; line-height:1.8; color:#334155; margin:0 0 18px; }
  h2 { font-size:18px; color:#0f172a; font-weight:700; margin:36px 0 14px; padding-left:14px; border-left:3px solid #6366f1; }
  h3 { font-size:16px; color:#1e293b; font-weight:700; margin:24px 0 10px; }
  ul { margin:12px 0 20px; padding-left:22px; }
  li { font-size:16px; line-height:1.8; color:#334155; margin-bottom:8px; }
  a { color:#6366f1; text-decoration:none; }
  .callout { background:#f8f9ff; border-left:3px solid #6366f1; padding:16px 20px; margin:20px 0; font-style:italic; color:#3730a3; font-size:15px; line-height:1.7; }
  .divider { border:none; border-top:1px solid #f1f5f9; margin:32px 0; }
  .sources { line-height:2.2; margin:16px 0; }
  .sources a { font-size:13px; display:block; }
</style>
</head>
<body>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#f0f2f5;padding:30px 0;">
  <tr><td align="center">
    <table role="presentation" class="wrap" width="620" cellpadding="0" cellspacing="0" style="background:#fff;border-radius:10px;overflow:hidden;box-shadow:0 2px 16px rgba(0,0,0,0.07);">

      <!-- HEADER -->
      <tr><td style="padding:40px 44px 8px;">
        <p style="font-size:13px;color:#94a3b8;margin:0 0 6px;">À : [Destinataire]</p>
        <h1 style="font-size:20px;font-weight:700;color:#0f172a;margin:0 0 8px;line-height:1.4;">[TITRE DU MAIL]</h1>
        <p style="font-size:14px;color:#64748b;margin:0 0 28px;padding-bottom:24px;border-bottom:1px solid #f1f5f9;">[Sous-titre ou contexte court]</p>
      </td></tr>

      <!-- BODY -->
      <tr><td style="padding:0 44px 44px;">

        <p>[Intro]</p>

        <h2>[Section 1]</h2>
        <p>[Contenu...]</p>

        <div class="callout">"[Citation clé]"</div>

        <hr class="divider">

        <h2>[Section 2]</h2>
        <ul>
          <li><strong>Point 1</strong> : explication</li>
          <li><strong>Point 2</strong> : explication</li>
        </ul>

        <div class="sources">
          <a href="#">🔗 Source 1 : description</a>
          <a href="#">🔗 Source 2 : description</a>
        </div>

        <!-- CLOSING -->
        <hr class="divider">
        <p>[Conclusion]</p>
        <p><strong>Gil</strong></p>

      </td></tr>
    </table>
  </td></tr>
</table>
</body>
</html>
```

---

## Composants réutilisables

### Stats block (3 colonnes)
```html
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin:20px 0;">
  <tr>
    <td width="33%" style="padding:6px;">
      <table width="100%" style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:8px;text-align:center;padding:16px;">
        <tr><td style="font-size:26px;font-weight:800;color:#6366f1;">[CHIFFRE]</td></tr>
        <tr><td style="font-size:12px;color:#64748b;padding-top:4px;">[LABEL]</td></tr>
      </table>
    </td>
    <!-- répéter pour chaque stat -->
  </tr>
</table>
```

### Agent/card grid (3 colonnes)
```html
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin:16px 0;">
  <tr>
    <td width="33%" style="padding:6px;vertical-align:top;">
      <table width="100%" style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:8px;padding:12px 14px;">
        <tr><td style="font-weight:700;font-size:14px;color:#1e293b;">[NOM]</td></tr>
        <tr><td style="font-size:12px;color:#6366f1;padding:3px 0;">[MODÈLE]</td></tr>
        <tr><td style="font-size:12px;color:#64748b;">[RÔLE]</td></tr>
      </table>
    </td>
  </tr>
</table>
```

### Level/colored block
```html
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin:14px 0;">
  <tr><td style="background:#eef2ff;border-left:3px solid #4338ca;border-radius:0 8px 8px 0;padding:18px 22px;">
    <p style="font-weight:700;font-size:15px;color:#1e293b;margin:0 0 8px;">[TITRE DU LEVEL]</p>
    <p style="font-size:14px;color:#475569;margin:0;">[Contenu]</p>
  </td></tr>
</table>
```

---

## Checklist avant envoi

- [ ] Largeur max 620px respectée
- [ ] Font-size body ≥ 16px
- [ ] Line-height ≥ 1.8
- [ ] Padding sections ≥ 32px
- [ ] Séparateurs visuels entre sections majeures
- [ ] Tous les liens cliquables avec 🔗
- [ ] Texte non condensé (contenu complet, pas de résumé)
- [ ] Envoyé d'abord à l'utilisateur pour validation
- [ ] **JAMAIS envoyer à un tiers sans confirmation explicite de l'utilisateur**

---


## Circuit Novia Com
Toute newsletter ou email produit avec ces règles est une pièce de l'outbox : présentation en carte, « Go publie » d'une personne autorisée, envoi par l'adaptateur configuré (Brevo) ou manuellement par l'équipe. Aucune adresse personnelle, aucun envoi direct depuis ce skill.
