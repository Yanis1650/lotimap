# importer

CLI Python 3.12 de conversion DXF → GeoJSON. Il lit un plan DAO avec `ezdxf`, contrôle chaque entité configurée, calcule la surface des lots dans la projection source et écrit les géométries en WGS84. Un problème sur une entité est signalé sans interrompre les autres.

## Installation et essai

Depuis la racine du dépôt, avec [uv](https://docs.astral.sh/uv/) installé :

```sh
uv python install 3.12
uv --directory importer sync --locked --python 3.12 --group dev
uv --directory importer run --locked lotimap-import \
  ../data/demo/dxf/clos_du_verger_clean.dxf \
  --layers config/layers.example.yaml \
  --source-crs EPSG:3949 \
  --output ../data/demo/geojson/clos_du_verger.geojson \
  --report ../data/demo/geojson/validation.json
```

Pour un plan Lambert 93, choisir `--source-crs EPSG:2154`. Le DXF n'encode pas ici sa projection de manière fiable : **l'utilisateur doit fournir la bonne projection source**. Les surfaces sont en mètres carrés, calculées avant la transformation en WGS84.

Le rapport est toujours affiché dans le terminal ; `--report` en écrit une version JSON. Par défaut, la CLI continue et termine avec succès malgré des anomalies. `--strict` renvoie un code d'erreur si le rapport n'est pas vide. Un fichier illisible produit un rapport d'erreur et aucun GeoJSON.

## Mapping et limites

Le [mapping YAML](config/layers.example.yaml) associe des noms de calques à `lots`, `numbers`, `roads` et `boundary`. Les noms sont comparés sans tenir compte de la casse. `lots` et `numbers` sont obligatoires ; `roads` et `boundary` sont facultatifs. Chaque calque ne peut appartenir qu'à une catégorie.

Les contours pris en charge sont les polylignes 2D fermées `LWPOLYLINE` et `POLYLINE`, sans segment courbe. `TEXT` et `MTEXT` servent aux numéros. Les autres entités sur les calques configurés, les polylignes ouvertes, les courbes et les géométries invalides sont signalées puis ignorées. Un texte sur une limite commune à plusieurs lots est signalé comme ambigu. Un lot valide sans numéro reste exporté avec `number: null`.

## Tests

```sh
uv run --project importer --locked python -m pytest -q importer/tests enrichment/tests
uv --directory importer run --locked ruff check src tests ../samples ../enrichment
uv --directory importer run --locked ruff format --check src tests ../samples ../enrichment
```

Les tests couvrent le plan sain, cinq anomalies synthétiques, Lambert 93, les anciennes `POLYLINE`, les entités non prises en charge, les fichiers illisibles, le mapping et la limite de 200 lignes par fichier de code.
