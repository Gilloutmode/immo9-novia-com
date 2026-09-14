# Installation pas à pas

Public : Julien (administrateur technique). Durée : une heure pour l'installation, l'onboarding se fait ensuite avec l'équipe sur quelques jours. Tout est rejouable : les scripts sont idempotents et sauvegardent avant d'écrire.

## 0. Prérequis sur le serveur
- OpenClaw 2026.6 ou plus récent (recommandé : 2026.9.x ; `cron.skipMissedJobs` demande 2026.9.1). Vérifier : `openclaw --version`.
- `python3` ≥ 3.8, `ffmpeg` et `ffprobe` (déclinaisons, audiograms), `git`.
- Recommandé : `chromium` (rendu des carrousels et infographies en PNG et PDF ; sinon l'outil `browser` d'OpenClaw fait les captures), `node` ≥ 18 (HyperFrames, supermonteur).
- Debian/Ubuntu : `sudo apt install -y python3 ffmpeg chromium git` (police pour les audiograms : `fonts-dejavu`).

## 1. Récupérer le dépôt et diagnostiquer
```bash
cd /opt/openclaw   # ou le dossier où vivent vos workspaces
git clone git@github.com:Gilloutmode/immo9-novia-com.git
cd immo9-novia-com
bash scripts/doctor.sh
```
Le diagnostic liste ce qui manque. Les avertissements sur l'onboarding et la charte sont normaux à ce stade.

## 2. Telegram : bot, groupe, personnes
1. Avec @BotFather : `/newbot`, nom « Novia Com », récupérer le jeton. Désactiver le mode « privacy » du bot si vous voulez qu'il lise tous les messages du groupe (`/setprivacy`).
2. Créer le groupe Telegram « Novia Com », y ajouter le bot et l'équipe.
3. Identifiants : `openclaw directory` (une fois le compte ajouté) ou @userinfobot pour les personnes, et l'identifiant du groupe (commence par `-100`).
4. Remplir `workspace/state/approvers.json` (personnes autorisées à dire « Go » et « Go publie ») et `workspace/state/channels.json` (`telegram_group_id`, adaptateurs de publication). Exemples : les fichiers `.example` voisins.

## 3. Variables d'environnement (avant l'installation)
Copier `config/env.example`, remplir ce qui est disponible (au minimum `NOVIA_TELEGRAM_BOT_TOKEN`), et déclarer ces variables dans l'environnement du service gateway (unité systemd gérée par `openclaw daemon` : fichier d'environnement référencé par l'unité, ou export dans le shell qui lance le gateway). Jamais dans le dépôt. Exporter aussi ces variables dans le shell qui va lancer l'installation : l'installateur ne lit que leur présence (pour décider quoi configurer) et référence leur nom dans la configuration, jamais leur valeur.

## 4. Installer l'agent
```bash
bash scripts/install.sh                 # simulation : montre chaque action, valide le fragment de configuration
bash scripts/install.sh --apply          # écrit : agent, configuration (dont compte Telegram), skills partagés, crons
```
Ce que fait `--apply` :
- sauvegarde de `openclaw.json` (`.bak-novia-<date>`) ;
- `openclaw agents add novia-com --workspace <dépôt>/workspace` (un agent isolé, sans toucher aux autres) ;
- `openclaw config patch` avec `config/openclaw.novia-com.patch.json5` : politique d'outils de l'agent, compte Telegram `novia-com` (jeton référencé par `NOVIA_TELEGRAM_BOT_TOKEN`, DM et groupe en allowlist des personnes de `approvers.json`, groupe déclaré dans `groups`), variables des connecteurs présentes, `cron.skipMissedJobs` ;
- `openclaw agents bind --agent novia-com --bind telegram:novia-com` ;
- `openclaw skills install <dossier> --global` pour chaque skill de `skills-shared/` (visible par tous vos agents : c'est la seule modification hors de l'agent, avec `cron.skipMissedJobs`) ;
- déclaration des 12 crons, tous désactivés, si le gateway répond.
L'installateur refuse d'écrire tant que `state/approvers.json` contient les identifiants d'exemple. Si votre configuration Telegram a déjà un compte, définir `channels.telegram.defaultAccount` sur votre compte existant (`openclaw config set channels.telegram.defaultAccount default`).
Modèle : l'agent hérite de `agents.defaults.model`. Pour imposer un modèle : `--model openai/gpt-6-astra` par exemple.
```bash
openclaw daemon restart && openclaw doctor
bash scripts/doctor.sh
```

## 5. Onboarding avec l'équipe (dans Telegram)
Premier message dans le groupe ou en DM : « Commençons l'onboarding ». L'agent suit `workspace/skills/novia-onboarding/SKILL.md` :
- acte 0 : diagnostic (il lit `doctor.sh`, dit ce qui manque) ;
- acte 1 : identité, équipe, canal, plafonds de coût (David, Julien) ;
- acte 2 : voix, extraite du site et des comptes existants (équipe com) ;
- acte 3 : lignes rouges, personas, formats, charte (`templates/_tokens.json`, logos dans `templates/_brand/`), salons, concurrents, presse locale ;
- acte 4 : trois pièces test gratuites, corrections, puis `complete`.
Le passage à `complete` est refusé tant que les conditions ne sont pas remplies (`python3 workspace/skills/novia-onboarding/scripts/onboarding_state.py --check`).

## 6. Crons et première publication
```bash
bash crons/install-crons.sh --enable-p1     # 7 crons du palier 1 actifs, 5 du palier 2 désactivés
openclaw cron list
```
Première publication réelle : une pièce, « Go publie » dans Telegram, vérification sur la plateforme. Avant cela, `python3 workspace/skills/novia-publish/scripts/publish.py <id> --preview` montre ce qui partirait, sans approbation ni appel externe.

## 7. Chaque semaine
```bash
bash scripts/update.sh
```
Récupère la dernière version (`git pull --ff-only`), réapplique l'installation, relance le diagnostic. `CHANGELOG.md` liste les nouveautés. Vos fichiers d'état, d'apprentissage et de mémoire ne sont jamais écrasés.

## Vérifications utiles
```bash
openclaw agents list --bindings
openclaw skills check --agent novia-com
openclaw config validate
bash scripts/acceptance.sh        # tests hors ligne : verrous d'approbation et de publication, scripts
```

## Désinstaller
`openclaw cron rm` sur les jobs « Novia · … », `openclaw agents delete novia-com`, retirer le compte Telegram (`openclaw channels remove --channel telegram --account novia-com`) et les skills partagés si vous ne les utilisez pas ailleurs, ou restaurer la sauvegarde `openclaw.json.bak-novia-<date>`.
