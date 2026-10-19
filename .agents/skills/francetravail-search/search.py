"""CLI de recherche d'offres d'emploi via l'API France Travail Offres d'emploi v2."""
import argparse
import json
import re
import sys
import time
import requests

from auth import get_access_token

API_BASE = "https://api.francetravail.io/partenaire/offresdemploi/v2/offres/search"

CONTRACT_MAP = {
    "CDI": "CDI", "CDD": "CDD", "MIS": "MIS", "SAI": "SAI",
    "LIB": "LIB", "FRA": "FRA", "TTI": "TTI", "DDI": "DDI",
    "CCE": "CCE", "STG": "STG",
}

# L'API attend un code numerique (1 = moins d'un an, 2 = 1 a 3 ans, 3 = plus de 3 ans)
EXPERIENCE_MAP = {"D": "1", "E": "2", "S": "3"}

# L'API n'a pas de filtre teletravail : on filtre sur le texte de l'offre.
REMOTE_ANY = re.compile(r"t[ée]l[ée]\s*-?\s*travail|remote|hybride|distanciel", re.I)
REMOTE_FULL = re.compile(
    r"(100\s*%|full|total|complet|int[ée]gral)\s*(en\s*)?(t[ée]l[ée]\s*-?\s*travail|remote|distanciel)"
    r"|t[ée]l[ée]\s*-?\s*travail\s*(total|complet|int[ée]gral|100\s*%)"
    r"|full[\s-]*remote|remote[\s-]*first",
    re.I,
)


def matches_remote(offer, level):
    text = f"{offer.get('title') or ''} {offer.get('description') or ''}"
    pattern = REMOTE_FULL if level >= 2 else REMOTE_ANY
    return bool(pattern.search(text))

def build_params(args):
    params = {"motsCles": args.keywords}
    if args.location:
        if len(args.location) == 5 and args.location.isdigit():
            params["commune"] = args.location
        elif len(args.location) in (2, 3):
            params["departement"] = args.location
        else:
            params["region"] = args.location
        if args.radius:
            params["distance"] = args.radius
    if args.contract:
        params["typeContrat"] = CONTRACT_MAP.get(args.contract.upper(), args.contract.upper())
    if args.experience:
        params["experience"] = EXPERIENCE_MAP.get(args.experience.upper(), args.experience)
    return params


def fetch_offers(args):
    token = get_access_token()
    params = build_params(args)

    results = []
    # Avec le filtre teletravail, on recupere des pages pleines puis on filtre
    page_size = 150 if args.remote else min(args.limit, 150)
    start = 0
    max_start = 1149  # limite de pagination de l'API

    while len(results) < args.limit and start <= max_start:
        headers = {
            "Authorization": f"Bearer {token}",
            "Range": f"offres {start}-{min(start + page_size - 1, max_start)}",
        }
        resp = requests.get(API_BASE, headers=headers, params=params, timeout=20)

        if resp.status_code == 401:
            token = get_access_token()
            continue

        if resp.status_code == 204:  # aucune offre
            break

        if resp.status_code not in (200, 206):
            print(f"Erreur API ({resp.status_code}): {resp.text}", file=sys.stderr)
            break

        data = resp.json()
        offres = data.get("resultats", [])
        if not offres:
            break

        normalized = (normalize_offer(o) for o in offres)
        if args.remote:
            normalized = (o for o in normalized if matches_remote(o, args.remote))
        results.extend(normalized)
        start += page_size
        time.sleep(0.3)

        if len(offres) < page_size:
            break

    return results[: args.limit]

####


def normalize_offer(o):
    lieu = o.get("lieuTravail", {}) or {}
    entreprise = o.get("entreprise", {}) or {}
    salaire = o.get("salaire", {}) or {}
    return {
        "id": o.get("id"),
        "title": o.get("intitule"),
        "company": entreprise.get("nom", "Non precise"),
        "location": lieu.get("libelle"),
        "contract_type": o.get("typeContratLibelle"),
        "description": o.get("description"),
        "url": o.get("origineOffre", {}).get("urlOrigine"),
        "date_creation": o.get("dateCreation"),
        "salary": salaire.get("libelle", "Non precise"),
    }




def main():
    parser = argparse.ArgumentParser(description="Recherche d'offres via l'API France Travail")
    parser.add_argument("--keywords", required=True, help="Mots-cles de recherche")
    parser.add_argument("--location", help="Code commune (5 chiffres), departement, ou region")
    parser.add_argument("--radius", type=int, default=10, help="Rayon en km")
    parser.add_argument("--contract", help="Type de contrat (CDI, CDD, MIS, ...)")
    parser.add_argument("--experience", help="D=debutant, E=experimente, S=senior (ou code API 0-4)")
    parser.add_argument("--remote", type=int, nargs="?", const=1, choices=[1, 2],
                        help="Filtre teletravail sur le texte de l'offre : 1=possible (defaut), 2=total")
    parser.add_argument("--limit", type=int, default=50, help="Nombre max d'offres")
    args = parser.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    try:
        offers = fetch_offers(args)
    except RuntimeError as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        sys.exit(1)

    print(json.dumps(offers, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()