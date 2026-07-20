# francetravail-search

Recherche d'offres d'emploi via l'API officielle "Offres d'emploi v2" de France Travail.

## Usage

python search.py --keywords "data engineer" --location "35000" --radius 30 --contract CDI --limit 50

## Arguments

- --keywords : mots-clés de recherche (ex: "data engineer", "postgresql")
- --location : code commune INSEE, code département, ou code région
- --radius : rayon de recherche en km autour de la localisation (défaut: 10)
- --contract : type de contrat (CDI, CDD, MIS, SAI, etc.)
- --limit : nombre max d'offres à récupérer (défaut: 50, max par page: 150)
- --experience : niveau d'expérience (D=débutant, E=expérimenté, S=senior)
- --remote : filtre télétravail (1=possible, 2=total)

## Sortie

JSON normalisé sur stdout, une liste d'objets avec les champs :
id, title, company, location, contract_type, description, url, date_creation, salary

## Prérequis

Variables d'environnement dans .env à la racine du repo :

FT_CLIENT_ID=xxx
FT_CLIENT_SECRET=xxx

## Notes

- Le token OAuth2 est mis en cache localement (.ft_token_cache.json) et régénéré automatiquement à expiration.
- Respecte les quotas de l'API (voir francetravail.io, espace développeur).
- Ne jamais committer le .env ni le fichier de cache token (voir .gitignore).