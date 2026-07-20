"""CLI de recherche d'offres d'emploi via l'API France Travail Offres d'emploi v2."""
import argparse
import json
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
        params["experience"] = args.experience
    return params


def fetch_offers(args):
    token = get_access_token()
    params = build_params(args)

    results = []
    page_size = min(args.limit, 150)
    start = 0

    while len(results) < args.limit:
        headers = {
            "Authorization": f"Bearer {token}",
            "Range": f"offres {start}-{start + page_size - 1}",
        }
        resp = requests.get(API_BASE, headers=headers, params=params, timeout=20)

        if resp.status_code == 401:
            token = get_access_token()
            continue

        if resp.status_code not in (200, 206):
            print(f"Erreur API ({resp.status_code}): {resp.text}", file=sys.stderr)
            break

        data = resp.json()
        offres = data.get("resultats", [])
        if not offres:
            break

        results.extend(normalize_offer(o) for o in offres)
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
    parser.add_argument("--experience", help="D=debutant, E=experimente, S=senior")
    parser.add_argument("--remote", action="store_true", help="Filtre teletravail")
    parser.add_argument("--limit", type=int, default=50, help="Nombre max d'offres")
    args = parser.parse_args()

    try:
        offers = fetch_offers(args)
    except RuntimeError as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        sys.exit(1)

    print(json.dumps(offers, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()