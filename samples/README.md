# samples

`generate.py` produit le plan **entièrement fictif** du Clos du Verger et cinq variantes défectueuses utilisées par les tests du convertisseur. Il ne lit aucun fichier DAO externe.

## Générer les DXF

Depuis la racine du dépôt, avec [uv](https://docs.astral.sh/uv/) installé :

```sh
uv python install 3.12
uv run --locked --python 3.12 samples/generate.py
```

Les six DXF et `manifest.json` sont écrits dans `data/demo/dxf/`. Le fichier de verrouillage `generate.py.lock` fixe les dépendances du script. Une nouvelle exécution avec les mêmes paramètres produit les mêmes octets.

L'emprise provisoire se règle en ligne de commande :

```sh
uv run --locked --python 3.12 samples/generate.py \
  --center-lat 48.684 --center-lon -1.357 \
  --rotation-deg 0 --frontage-m 24 --depth-m 35 \
  --road-width-m 10 --margin-m 5 \
  --output-dir data/demo/dxf
```

Le schéma contient deux rangées de dix lots, de part et d'autre d'une voirie. La profondeur varie de 80 à 125 % de la profondeur nominale selon le lot : avec les valeurs par défaut, les surfaces vont de 672 à 1 050 m², ce qui rend le filtre de surface de la carte utile. Les nombres sont répartis entre `TEXT` et `MTEXT`. Les coordonnées du DXF sont en mètres, en **CC49 (EPSG:3949)** ; le centre demandé en latitude/longitude est transformé avec `pyproj`. Le plan est schématique et ne décrit aucune parcelle réelle.

## Calques et cas défectueux

- `LOTS` : 20 polylignes de lots.
- `VOIRIE` : une polyligne pour la chaussée.
- `LIMITE_OPERATION` : une polyligne pour l'emprise.
- `NUMEROS_LOTS` : numéros des lots.

| Fichier | Défaut voulu |
| --- | --- |
| `clos_du_verger_clean.dxf` | Aucun. |
| `clos_du_verger_open_polyline.dxf` | Lot 01 non fermé. |
| `clos_du_verger_missing_number.dxf` | Lot 02 sans numéro. |
| `clos_du_verger_duplicate_number.dxf` | Numéro 03 utilisé dans les lots 03 et 04. |
| `clos_du_verger_orphan_text.dxf` | Texte 99 hors de tous les lots. |
| `clos_du_verger_invalid_geometry.dxf` | Lot 05 auto-intersecté. |

Le manifeste enregistre les paramètres, les calques et le défaut attendu pour chaque fichier. Aucun fichier réel ne doit être placé ici ; `data/private/` est prévu pour des données locales exclues de Git.
