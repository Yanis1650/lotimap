# lotimap

[![Checks](https://github.com/Yanis1650/lotimap/actions/workflows/ci.yaml/badge.svg)](https://github.com/Yanis1650/lotimap/actions/workflows/ci.yaml)

[English](README.en.md)

> **Démonstration — données fictives.** Aucun lot proposé à la vente, aucune collecte de données personnelles.

Du plan DAO à la carte web : **lotimap** transforme un DXF de géomètre en GeoJSON contrôlé, puis présente les lots dans une interface adaptée au téléphone et à l'ordinateur. Ce projet de portfolio met l'accent sur la qualité de conversion, la lisibilité du code et l'explication des limites, dans un budget cible d'environ 25 heures.

![Plan paysager interactif du Clos du Verger sur ordinateur](docs/images/lotimap-landscape-desktop.png)

## Le problème et la démonstration

Un plan de géomètre contient des calques, des polylignes et des textes ; il n'apporte pas directement des polygones géographiques fiables avec leurs numéros et surfaces. Le convertisseur sépare la lecture du DXF, les contrôles géométriques, l'association des textes et la transformation de coordonnées. Un mapping YAML adapte les calques à différents plans.

Le scénario est **« Le Clos du Verger »**, un lotissement entièrement fictif de 20 lots près d'Avranches (Manche). L'emprise provisoire est centrée sur 48.684° N, 1.357° O ; elle ne représente aucune opération réelle.

- **Conversion** : Lambert 93 ou CC49, surface dans la projection source, GeoJSON WGS84 et rapport de validation.
- **Carte publique** : plan paysager 2D ou orthophoto IGN, quatre statuts, filtres budget/surface, liste accessible et fiche par lot.
- **Vue 3D légère** : volumes fictifs des maisons et plantations, rotation, zoom et recentrage dans la même carte.
- **Perspectives** : deux illustrations d'ambiance réalistes, explicitement fictives et générées par IA.
- **Administration** : modification des prix et statuts SQLite avec un mot de passe fourni par l'environnement.
- **Enrichissement** : zonage GPU par lot, familles de risques communales et médiane DVF, calculés à l'avance.

![Perspectives d'ambiance fictives générées par IA](docs/images/lotimap-gallery-desktop.png)

## Lancer la carte

### Développement

Installer **Node.js 22.22.2 ou plus récent dans la branche 22**, puis depuis la racine du dépôt :

```sh
cd web
npx --yes npm@12.2.0 ci
npm run dev
```

Ouvrir [http://127.0.0.1:3000](http://127.0.0.1:3000). Le plan et l'enrichissement sont fournis ; SQLite initialise les valeurs fictives au premier appel. Une connexion Internet est nécessaire pour l'orthophoto IGN. L'administration est désactivée tant que ses deux variables ne sont pas renseignées : voir [web/README.md](web/README.md).

### Docker

Avec Docker et Docker Compose récents, depuis la racine :

```sh
docker compose -f deploy/compose.yaml -f deploy/compose.local.yaml up --build -d --wait
```

Ouvrir [http://127.0.0.1:3333](http://127.0.0.1:3333). Les prix et statuts sont conservés dans un volume nommé. La configuration VPS, les variables Traefik, les secrets et la sauvegarde SQLite sont documentés dans [deploy/README.md](deploy/README.md).

## Générer et convertir un plan

Avec [uv](https://docs.astral.sh/uv/) installé, depuis la racine :

```sh
uv python install 3.12
uv run --locked --python 3.12 samples/generate.py
uv sync --project importer --locked --group dev
uv run --project importer --locked lotimap-import data/demo/dxf/clos_du_verger_clean.dxf --layers importer/config/layers.example.yaml --source-crs EPSG:3949 --output data/demo/geojson/clos_du_verger.geojson --report data/demo/geojson/validation.json --strict
```

Le générateur produit un plan sain et cinq variantes : contour ouvert, numéro absent, numéro dupliqué, texte hors lot et géométrie auto-intersectée. Centre, orientation et dimensions sont paramétrables. Avec les mêmes paramètres, les fichiers générés sont identiques.

Pour un DXF Lambert 93, choisir `--source-crs EPSG:2154`. Le DXF ne permet pas ici de déduire sa projection : elle doit être fournie correctement. `--strict` transforme les anomalies en échec utilisable en CI ; sans cette option, les entités exploitables sont exportées et les anomalies sont signalées.

Voir [le générateur](samples/README.md), [le convertisseur et son mapping](importer/README.md). Après toute modification du GeoJSON, recalculer l'enrichissement :

```sh
uv run --project importer --locked python -m enrichment.build
```

La commune, la période DVF et les chemins se règlent en CLI. [La méthode d'enrichissement](enrichment/README.md) détaille les seuils et les limites.

## Architecture

```text
samples/ ──▶ DXF synthétiques ──▶ importer/ ──▶ GeoJSON WGS84
                                                   │
sources ouvertes ──▶ enrichment/ ◀──────────────────┘
                         │                         │
                         ▼                         ▼
                  enrichment.json ──▶ API Nitro ◀── SQLite
                                           │
                                           ▼
                                  Vue 3 + MapLibre GL
```

- `importer/` : Python 3.12, ezdxf, Shapely, pyproj, Typer, YAML, pytest et Ruff.
- `samples/` : générateur DXF déterministe en CC49, avec dépendances verrouillées par uv.
- `enrichment/` : calcul Python réutilisant l'environnement du convertisseur.
- `web/` : Nuxt 4, Vue 3, TypeScript, MapLibre GL, Nitro et better-sqlite3.
- `data/demo/` : plan fictif, GeoJSON, rapport et résultats ouverts agrégés.
- `data/private/` : données locales éventuelles, exclues de Git et du contexte Docker.
- `deploy/` : image Docker en deux étapes, lancement local et configuration Traefik distincts.
- `.github/workflows/ci.yaml` : contrôles Python, web et conteneur, sans publication automatique.

## Choix techniques

**Géométrie avant interface.** Les surfaces sont calculées en mètres dans le système source, avant reprojection. L'association numéro/lot repose sur la position du texte ; une position sur une limite commune est signalée comme ambiguë.

**Nuxt et SQLite.** Un seul service fournit la page et les routes serveur ; un fichier SQLite suffit pour 20 lots et un administrateur. Les données existantes sont conservées au démarrage. Cette démo utilise une seule instance, sans réplication ni authentification externe.

**Pré-calcul des données ouvertes.** Les appels GPU, Géorisques et DVF ne ralentissent pas la consultation. Le résultat conserve ses dates et l'empreinte SHA256 du GeoJSON ; un plan modifié entraîne le retrait du contexte jusqu'au prochain calcul. `.gitattributes` empêche Git de modifier les fins de ligne des GeoJSON, afin de préserver cette empreinte entre Windows et Linux.

**Installation reproductible.** npm 12.2.0 est utilisé en local, dans Docker et en CI. `allowScripts` autorise les versions verrouillées d'esbuild et du résolveur ESLint. SQLite 13 fournit ses binaires natifs : sa recompilation automatique est désactivée pour éviter un échec d'installation avec npm 10 sous Windows. Voir [la gestion des scripts npm](https://docs.npmjs.com/cli/v12/commands/npm-install-scripts/).

**Déploiement sobre.** Debian utilise le binaire SQLite Linux fourni par le paquet. L'image finale contient la sortie Nitro et les données de démonstration ; elle tourne sans root, avec le système de fichiers en lecture seule et un volume pour SQLite. Les secrets restent dans l'environnement d'exécution.

**Lisibilité.** Chaque fichier de code écrit à la main est limité à **200 lignes physiques**, tests et CSS compris. La règle persistante est vérifiée par pytest. Les dépendances npm et uv sont verrouillées.

**Identité Drekky Studio.** La charte fournie est appliquée : crème, ardoise, touches terracotta, Space Grotesk, IBM Plex Sans et IBM Plex Mono. Logos SVG et polices sont hébergés avec le site. [Les choix visuels et droits des éléments](docs/branding.md) sont documentés.

**Plan paysager et images.** Une couche illustrative place maisons et plantations dans les lots fictifs, sans modifier leurs contours ni leurs surfaces. Les perspectives ne représentent pas l'implantation exacte du plan. [La méthode, les limites et les prompts](docs/visuals.md) sont documentés.

**3D légère.** Les couches natives MapLibre mettent en volume les illustrations du plan, avec des hauteurs fictives sur terrain plat. Le navigateur conserve la même carte et les mêmes données dans les trois modes. [Les choix, commandes et limites](docs/3d.md) sont documentés.

## Contrôles et CI

Depuis la racine :

```sh
uv run --project importer --locked python -m pytest -q importer/tests enrichment/tests
uv --directory importer run --locked ruff check src tests ../samples ../enrichment
uv --directory importer run --locked ruff format --check src tests ../samples ../enrichment
```

Depuis `web/` :

```sh
npm run lint
npm run typecheck
npm test
```

Les 18 tests Python couvrent la conversion, les fichiers défectueux, les projections, le mapping, les agrégations et la limite de taille. Le test d'intégration web démarre le serveur compilé avec une base temporaire : connexion, accès refusés, validation, édition, déconnexion et invalidation de l'enrichissement. ESLint contrôle Vue, TypeScript et JavaScript.

Trois tests web supplémentaires vérifient que le paysage reste dans les lots sans modifier le plan, suit les filtres et ignore les formes non prises en charge.

Un cinquième test web valide les couches 2D/3D avec la spécification native de MapLibre. Les contrôles géométriques vérifient aussi que chaque volume appartient à son lot identifié.

GitHub Actions exécute ces contrôles sur les push et pull requests, puis construit et démarre un conteneur de test. Sa vérification de santé appelle `/api/lots`, donc teste aussi les données embarquées et SQLite. Le test conteneur contrôle la persistance après redémarrage, le cookie HTTPS, `noindex` et `robots.txt`. Les tests d'enrichissement n'interrogent pas les services ouverts. Les trois tâches ont réussi lors du [premier passage GitHub, le 4 octobre 2026](https://github.com/Yanis1650/lotimap/actions/runs/37219417210).

**État des dépendances au 4 octobre 2026.** `npm audit` signale 11 dépendances affectées par deux avis : [braces](https://github.com/advisories/GHSA-vfj7-8cjw-p6xm) et [node-forge](https://github.com/advisories/GHSA-86w9-cpqp-85rv), sans version corrigée publiée. Ces modules arrivent via les outils Nuxt de développement/construction et sont absents de la sortie serveur Nitro vérifiée. Le serveur de développement écoute uniquement sur `127.0.0.1`. Recontrôler ces avis avant déploiement et appliquer les correctifs disponibles ; le résultat d'audit n'est pas masqué.

## Limites assumées

- Le convertisseur accepte les contours `LWPOLYLINE` et `POLYLINE` 2D fermés **sans courbes**. Les blocs, courbes et autres entités configurées sont signalés, sans être convertis. Un fichier totalement illisible produit un rapport d'erreur.
- Le mapping adapte les calques, pas toutes les conventions DAO possibles. L'emprise, les calques et la projection doivent être vérifiés lors d'un nouvel import.
- Les risques sont communaux, pas localisés sur les lots. Le code PLU ne garantit pas la constructibilité.
- DVF fournit un indicateur agrégé, avec les limites des exports communaux et de la déduplication. Les prix commerciaux de la démo restent fictifs.
- L'administration est volontairement minimale ; les tentatives de connexion sont limitées en mémoire d'une seule instance.
- Le domaine et les paramètres du VPS restent à renseigner avant le déploiement public.

## Sources, dates et licences

Le plan, les lots, les prix et les statuts sont fictifs. Aucune donnée de propriétaire ni référence cadastrale n'est publiée ; les CSV DVF bruts ne sont pas conservés.

- **IGN Géoplateforme / orthophoto WMTS** : [service et attribution](https://cartes.gouv.fr/aide/fr/guides-utilisateur/utiliser-les-services-de-la-geoplateforme/diffusion/wmts/), consulté le **30 septembre 2026**.
- **IGN, API Carto / GPU** : [source](https://www.data.gouv.fr/dataservices/api-carto-module-geoportail-de-lurbanisme-gpu), consultée le **1er octobre 2026**. Les 20 lots provisoires sont en Uh ; date portée par le document : **27 février 2020**.
- **Géorisques, Ministère / BRGM, GASPAR** : [source](https://www.georisques.gouv.fr/donnees/bases-de-donnees/procedures-administratives-relatives-aux-risques), [conditions d'utilisation](https://www.georisques.gouv.fr/cgu), consultée le **1er octobre 2026**. Sept familles recensées dans la commune d'Avranches.
- **DGFiP, traitement Etalab / DVF** : [source brute](https://www.data.gouv.fr/datasets/demandes-de-valeurs-foncieres), [exports géolocalisés](https://www.data.gouv.fr/datasets/demandes-de-valeurs-foncieres-geolocalisees), consultés le **1er octobre 2026**. Médiane de **80 €/m²**, sur **12 mutations de 2021 à 2025**.

Ces données ouvertes sont attribuées sous [Licence Ouverte 2.0](https://www.etalab.gouv.fr/licence-ouverte-open-licence/). Les conditions DVF interdisent la réidentification et l'indexation externe. Toutes les pages portent une balise `noindex` et l'en-tête `X-Robots-Tag` ; `robots.txt` bloque l'exploration. Ces directives supposent que les robots les respectent.

Le code, la documentation et les plans synthétiques sont sous [licence MIT](LICENSE). Les polices sont sous SIL Open Font License ; les données et logos gardent leurs droits propres, détaillés dans [NOTICE.md](NOTICE.md). L'état du projet et les décisions de reprise sont dans [CONTEXT.md](CONTEXT.md).
