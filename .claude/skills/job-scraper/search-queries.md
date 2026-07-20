# Search Queries for Job Scraper

<!-- Populated by /setup for Bruno SEZNEC — French job market, remote-first, Paris/Bretagne bases -->

## Job Market Context

Bruno is based in France (Bretagne + Île-de-France). Searches target the French job market: the France Travail (Pôle Emploi) API via `.agents/skills/francetravail-search/`, plus Google `site:` searches on French portals for sites not covered by that API.

**French job portals to search:**
- **apec.fr** — cadres/ingénieurs, primary target for senior profiles
- **linkedin.com/jobs** — international and French companies, best for GenAI/tech roles
- **welcome.co** (Welcome to the Jungle) — startups and tech companies, strong GenAI/AI scene
- **freelance-info.fr / malt.fr / comet.co** — freelance missions (TJM-based), matches Bruno's model
- **pole-emploi.fr / francetravail.fr** — broad coverage including public sector
- **Monster.fr / Indeed.fr** — broad but lower signal for senior profiles

## Location Filters

- **Ideal:** Full remote (France-wide) | IDF hybrid (75, radius 30km) | Bretagne on-site (56, radius 30km) | Nantes on-site (44, radius 30km)
- **Acceptable:** Paris/IDF occasional on-site (1–2 days/week)
- **Borderline:** IDF full on-site (discuss case by case)
- **Too far:** Requires relocation outside France; requires permanent daily on-site outside IDF/Bretagne/Nantes

## France Travail CLI Queries

Tool: `python .agents/skills/francetravail-search/search.py`
Flags: `--experience S` (senior), `--limit 50`

### Priority 1: Generative AI / RAG / LLM Engineering

```bash
# Remote-first (all France)
python .agents/skills/francetravail-search/search.py --keywords "IA générative" --remote 2 --experience S --limit 50
python .agents/skills/francetravail-search/search.py --keywords "RAG langchain" --remote 2 --experience S --limit 50
python .agents/skills/francetravail-search/search.py --keywords "LLM engineer" --remote 2 --experience S --limit 50

# Île-de-France (dept 75, radius 30km, télétravail possible)
python .agents/skills/francetravail-search/search.py --keywords "IA générative" --location "75" --radius 30 --remote 1 --experience S --limit 50
python .agents/skills/francetravail-search/search.py --keywords "LLM RAG" --location "75" --radius 30 --remote 1 --experience S --limit 50

# Morbihan / Bretagne (dept 56, radius 30km)
python .agents/skills/francetravail-search/search.py --keywords "IA générative" --location "56" --radius 30 --experience S --limit 50
python .agents/skills/francetravail-search/search.py --keywords "data engineer" --location "56" --radius 30 --experience S --limit 50

# Nantes / Loire-Atlantique (dept 44, radius 30km)
python .agents/skills/francetravail-search/search.py --keywords "IA générative" --location "44" --radius 30 --experience S --limit 50
python .agents/skills/francetravail-search/search.py --keywords "data engineer" --location "44" --radius 30 --experience S --limit 50
```

### Priority 2: Data Quality & Governance / Data Catalog

```bash
# Remote-first
python .agents/skills/francetravail-search/search.py --keywords "data quality" --remote 2 --experience S --limit 50
python .agents/skills/francetravail-search/search.py --keywords "data governance" --remote 2 --experience S --limit 50
python .agents/skills/francetravail-search/search.py --keywords "data catalog OpenMetadata" --remote 2 --experience S --limit 50

# Île-de-France
python .agents/skills/francetravail-search/search.py --keywords "data quality python" --location "75" --radius 30 --remote 1 --experience S --limit 50
python .agents/skills/francetravail-search/search.py --keywords "data governance consultant" --location "75" --radius 30 --remote 1 --experience S --limit 50
```

### Priority 3: Data Engineering / MLOps

```bash
# Remote-first
python .agents/skills/francetravail-search/search.py --keywords "data engineer python spark" --remote 2 --experience S --limit 50
python .agents/skills/francetravail-search/search.py --keywords "MLOps kubernetes" --remote 2 --experience S --limit 50
python .agents/skills/francetravail-search/search.py --keywords "data engineer airflow" --remote 2 --experience S --limit 50

# Île-de-France
python .agents/skills/francetravail-search/search.py --keywords "data engineer" --location "75" --radius 30 --remote 1 --experience S --limit 50
python .agents/skills/francetravail-search/search.py --keywords "MLOps" --location "75" --radius 30 --remote 1 --experience S --limit 50

# Morbihan
python .agents/skills/francetravail-search/search.py --keywords "data engineer" --location "56" --radius 30 --experience S --limit 50

# Nantes
python .agents/skills/francetravail-search/search.py --keywords "MLOps" --location "44" --radius 30 --experience S --limit 50
```

### Priority 4: Adjacent / Broader Technical Consulting

```bash
# Remote-first
python .agents/skills/francetravail-search/search.py --keywords "architecte data" --remote 2 --experience S --limit 50
python .agents/skills/francetravail-search/search.py --keywords "consultant IA" --remote 2 --experience S --limit 50

# Île-de-France
python .agents/skills/francetravail-search/search.py --keywords "architecte data consultant" --location "75" --radius 30 --remote 1 --experience S --limit 50
```

## Supplementary Web Searches (apec.fr, LinkedIn, malt.fr)

For portals not covered by the France Travail API, use Google `site:` searches:

### Priority 1: Generative AI / RAG
```
site:apec.fr "IA générative" consultant remote
site:linkedin.com/jobs "RAG" "Langchain" France
site:welcome.co "generative AI" France
site:malt.fr "expert RAG" OR "LLM engineering"
site:comet.co "IA générative" consultant
```

### Priority 2: Data Quality & Governance
```
site:apec.fr "data quality" "data governance" consultant
site:apec.fr "OpenMetadata" OR "DataHub" OR "data catalog"
site:malt.fr "data governance" "data quality" consultant
```

### Priority 3: Data Engineering / MLOps
```
site:apec.fr "data engineer" python spark remote
site:linkedin.com/jobs "data engineer" "airflow" France remote
site:malt.fr "data engineer" freelance
```

### Priority 4: Broader
```
site:apec.fr "architecte data" consultant remote
site:welcome.co "AI consultant" OR "data architect" France
```

## Role Titles to Search

Primary: Expert IA Générative, LLM Engineer, RAG Engineer, Consultant IA, Data Engineer, Architecte Data
Secondary: Data Quality Engineer, MLOps Engineer, Data Scientist, Architecte Big Data, Technical Consultant Data & AI
Adjacent (worth exploring): Knowledge Graph Engineer, Semantic Web Consultant, AI Solutions Architect

## Key Skills as Search Terms (distinctive and ATS-visible)

- RAG / LLM / Langchain / LlamaIndex
- PgVector / OpenMetadata / Great Expectations
- Kubeflow / Dataiku / Airflow / Spark
- "IA générative" / "Generative AI"
- RAGAS / Langfuse

## Date Filter

Only include jobs posted within the last 14 days, or with an application deadline that has not yet passed.

## Contract Type Filter

Exclude Alternance, Apprentissage, Stage/Stagiaire, and VIE postings — Bruno is a senior independent consultant (TJM 600-800€), not a student or entry-level candidate. Filter these out by title/contract_type after fetching; the France Travail API has no exclude-by-type parameter.

## Adapting Queries

If the user specifies a focus area with `/scrape [focus]`, select from the matching priority category and generate 2–3 additional custom queries for that focus. For example:
- `/scrape GenAI` → Priority 1 queries + custom LLM/RAG variations
- `/scrape data quality` → Priority 2 queries + OpenMetadata/Collibra variations
- `/scrape freelance` → Add malt.fr / comet.co / freelance-info.fr variants across all priorities
