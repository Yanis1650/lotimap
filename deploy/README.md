# Déploiement Docker et Traefik

Les commandes suivantes sont lancées **depuis la racine du dépôt**, avec Docker et Docker Compose prenant en charge `up --wait` (Compose v2.20 ou plus récent). Docker Desktop doit utiliser le moteur Linux sous Windows.

## Structure

- `Dockerfile` installe les dépendances avec npm 12.2.0 et compile Nuxt sous Node 22 / Debian, puis copie uniquement la sortie Nitro et les deux fichiers de démonstration dans l'image finale. SQLite utilise son binaire Linux fourni.
- `compose.yaml` définit l'application, son volume SQLite et une vérification de santé qui lit `/api/lots`. Il ne publie aucun port sur l'hôte.
- `compose.local.yaml` ajoute un port lié uniquement à `127.0.0.1` et désactive la découverte Traefik.
- `compose.traefik.yaml` connecte l'application à votre réseau Traefik existant et définit le routage HTTPS. Utiliser cet ajout **ou** le fichier local, jamais les deux ensemble.

Le conteneur tourne avec l'utilisateur `node` (UID 1000). Le système de fichiers est en lecture seule, sauf `/tmp` et le volume `/app/state`. Les outils de construction web restent dans l'étape de construction. `.dockerignore` exclut les dépendances locales, sorties de compilation, bases, secrets et `data/private/` du contexte transmis à Docker.

## Essai local

```sh
docker compose -f deploy/compose.yaml -f deploy/compose.local.yaml up --build -d --wait
docker compose -f deploy/compose.yaml -f deploy/compose.local.yaml ps
```

Ouvrir [http://127.0.0.1:3333](http://127.0.0.1:3333). Pour arrêter sans perdre les prix/statuts :

```sh
docker compose -f deploy/compose.yaml -f deploy/compose.local.yaml down
```

Si le port est occupé, copier `deploy/.env.example` vers `deploy/.env`, choisir `LOTIMAP_LOCAL_PORT=3334`, puis ajouter `--env-file deploy/.env` après `docker compose` dans toutes les commandes. Le fichier `.env` est ignoré par Git.

## Activer l'administration

Dans `deploy/.env`, renseigner `LOTIMAP_ADMIN_PASSWORD` et `LOTIMAP_SESSION_SECRET`. Générer le secret localement :

```sh
node -e "console.log(require('node:crypto').randomBytes(32).toString('hex'))"
```

Avec les deux variables vides, l'administration reste désactivée. Les secrets sont injectés à l'exécution ; ils ne sont ni dans l'image ni dans les labels Traefik. Après une modification du fichier, recréer le service avec `up -d --wait`. `docker compose config` affiche les variables interpolées : ne pas publier sa sortie lorsque de vrais secrets sont configurés.

## VPS derrière Traefik

Cette configuration utilise votre **Traefik existant**. Renseigner dans `deploy/.env` :

- `LOTIMAP_DOMAIN` : nom DNS du site, sans protocole ni chemin ;
- `TRAEFIK_NETWORK` : nom réel du réseau Docker partagé avec Traefik ;
- `TRAEFIK_ENTRYPOINT` : entrée HTTPS existante, par défaut `websecure` ;
- `TRAEFIK_CERTRESOLVER` : résolveur ACME déjà configuré dans Traefik ;
- les deux secrets admin si l'administration doit être disponible.

Le DNS doit pointer vers le VPS, Traefik doit écouter en HTTPS et disposer du réseau/résolveur indiqués. Les exemples `.example` ne sont pas des valeurs de production. Le réseau externe doit déjà exister ; Compose ne crée ni Traefik ni ses certificats.

```sh
docker compose --env-file deploy/.env -f deploy/compose.yaml -f deploy/compose.traefik.yaml config --quiet
docker compose --env-file deploy/.env -f deploy/compose.yaml -f deploy/compose.traefik.yaml up --build -d --wait
```

`LOTIMAP_PUBLIC_ORIGIN` est construit automatiquement depuis le domaine (`https://…`). Il sert au contrôle d'origine des requêtes admin. Traefik transmet les en-têtes de protocole ; le cookie devient `Secure` en HTTPS. Ne pas exposer le port 3000 directement. Si un autre proxy précède Traefik, ne faire confiance qu'aux en-têtes de ce proxy connu.

Les labels sont décrits dans la [documentation Traefik](https://doc.traefik.io/traefik/reference/routing-configuration/other-providers/docker/). Le réseau partagé suit le mécanisme [Docker Compose des réseaux externes](https://docs.docker.com/reference/compose-file/networks/).

## Persistance et sauvegarde

Le volume Compose `sales` conserve `lotimap.sqlite` et ses journaux WAL. Le nom dépend du projet Compose (par défaut `lotimap_sales`). **Garder le même nom de projet** pour les mises à jour. `down` conserve le volume ; `down --volumes` efface les prix/statuts.

Une seule instance doit utiliser cette base. Pour sauvegarder, arrêter les écritures et copier **tout le répertoire** avant de redémarrer :

```sh
docker compose -f deploy/compose.yaml stop web
docker compose -f deploy/compose.yaml cp web:/app/state ./data/private/sqlite-backup
docker compose -f deploy/compose.yaml -f deploy/compose.local.yaml start web
```

Créer d'abord `data/private/` si nécessaire et utiliser un dossier de sauvegarde neuf. Sur le VPS, employer la commande Traefik avec `--env-file deploy/.env` pour le redémarrage. Pour restaurer, arrêter le service, copier le répertoire complet vers `/app/state`, vérifier son propriétaire UID 1000, puis redémarrer. Ne pas copier uniquement le fichier principal pendant que la base écrit en WAL.

## Mise à jour des données

Le plan et l'enrichissement sont embarqués dans l'image. Régénérer le GeoJSON, recalculer l'enrichissement, puis reconstruire l'image avec `up --build`. L'empreinte du plan doit correspondre au résultat d'enrichissement. Les valeurs existantes sont liées aux identifiants des entités DXF : un changement de ces identifiants peut initialiser de nouveaux lots avec leurs valeurs fictives par défaut. Préparer une nouvelle base pour un scénario entièrement différent.

Les en-têtes `noindex`, le bandeau de démonstration et le blocage `robots.txt` restent actifs dans l'image. L'application ne lance aucun enrichissement au démarrage et la CI ne déploie pas sur le VPS.

## Test du conteneur

La CI utilise le projet Compose isolé **`lotimap-check`**, avec des identifiants factices réservés au test. `deploy/tests/container.test.mjs` contrôle les pages et l'API, le cookie simulant un proxy HTTPS, une modification de prix/statut et sa persistance après redémarrage. Il doit uniquement être lancé contre ce projet de test, car il modifie un lot et redémarre le service.

Le conteneur et son volume de test sont supprimés à la fin de la CI, y compris en cas d'échec. Les prix/statuts de la démonstration et ses secrets n'interviennent pas dans ce test.
