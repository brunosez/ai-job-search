---
name: job-scraper
description: >
  Scrapes French job sites (France Travail, apec.fr, LinkedIn, malt.fr and others) and your Gmail LinkedIn Job Alerts for new positions matching your profile. Deduplicates across runs.
  Triggers on: job scrape, find jobs, search jobs, new jobs, job search, scrape jobs, /scrape
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, WebFetch, WebSearch, Agent, AskUserQuestion, mcp__claude_ai_Gmail__search_threads, mcp__claude_ai_Gmail__get_thread
---

# Job Scraper

---

## How It Works

This skill searches French job portals — the France Travail API plus targeted web searches on apec.fr, LinkedIn, Welcome to the Jungle, malt.fr and others — using targeted queries based on your profile, plus your Gmail inbox for LinkedIn Job Alert emails. It deduplicates against previously seen jobs and the application tracker, and presents new matches with a quick fit assessment.

## Invocation

The user triggers this skill by saying things like:
- "Find new jobs"
- "Scrape for jobs"
- "Any new positions?"
- "/scrape"

Optional arguments:
- A focus area, e.g. "/scrape data science" or "/scrape geophysics"
- "broad" to run all search categories, e.g. "/scrape broad"

---

## Execution Steps

### Step 0: Load State

1. Read `job_scraper/seen_jobs.json` (create if missing - start with `{"seen": {}}`)
2. Read `job_search_tracker.csv` to extract already-applied companies+roles
3. Read `search-queries.md` (this directory) for the search strategy

### Step 1: Search

Run the queries from `search-queries.md`. By default, run the top 3 priority categories. If the user said "broad", run all categories. If the user specified a focus area (e.g. "data science"), prioritize queries from that category.

`search-queries.md` splits queries into two groups — run both:
- **France Travail CLI queries**: run via `Bash`, e.g. `python .agents/skills/francetravail-search/search.py --keywords "..." --remote --limit 50` (see that file for the full list per priority category). This is the primary, highest-signal source — it hits the official API directly. Requires `FT_CLIENT_ID`/`FT_CLIENT_SECRET` in `.env`; if the tool errors on missing credentials, tell the user and fall back to the web-search group only.
- **Supplementary web searches**: use `WebSearch` with the `site:` queries listed under "Supplementary Web Searches" in `search-queries.md` (apec.fr, linkedin.com/jobs, welcome.co, malt.fr, comet.co) — these portals aren't covered by the France Travail API.

Target your configured geographic area (remote-first France-wide, Île-de-France, Bretagne, or Nantes — see `search-queries.md`). Look for postings from the last 14 days.

### Step 1b: Gmail LinkedIn Job Alerts

LinkedIn's own job-matching engine sends you digest emails from `jobalerts-noreply@linkedin.com`, each one bundling several recommended postings. This is a free second source alongside Step 1's web searches.

1. Call `mcp__claude_ai_Gmail__search_threads` with query `from:jobalerts-noreply@linkedin.com newer_than:14d` (widen to `newer_than:30d` only if the user asked for "broad"). If the tool returns a re-authorization error, tell the user their Gmail connector needs reconnecting in Claude's integration settings and skip this source for the run (don't block Step 1's web results on it).
2. For each thread, call `mcp__claude_ai_Gmail__get_thread` with `messageFormat: FULL_CONTENT` and read the `plaintextBody` field (not `htmlBody` — LinkedIn's HTML is heavily obfuscated with tracking params and not worth parsing).
3. Each digest email's plaintext body is a series of blocks separated by a line of dashes, each block shaped like:
   ```
   <Job Title>
   <Company>
   <Location>
   [This company is actively hiring]      <- optional line, ignore it
   View job: https://www.linkedin.com/comm/jobs/view/<JOB_ID>/?trackingId=...&...
   ```
   Split on the dash separator, then parse each block's first three non-empty lines as title/company/location, and extract `<JOB_ID>` from the `jobs/view/<JOB_ID>` segment of the URL (regex `jobs/view/(\d+)`).
4. Build a clean URL for each job as `https://www.linkedin.com/jobs/view/<JOB_ID>/` (strip all tracking query params — they expire and bloat storage).
5. Use `li_<JOB_ID>` as the dedup key in `seen_jobs.json` (the `li_` prefix avoids collisions with France Travail's numeric/alphanumeric offer IDs used elsewhere in the same file).
6. Feed the extracted (title, company, location, url) tuples into Step 2 alongside Step 1's web results — same fit assessment, same dedup, same presentation. LinkedIn alert emails don't include the full job description, so the "key requirements" field from Step 2 will just be the title/location until the user asks to evaluate a specific one in detail (at which point the job-application-assistant workflow fetches the full posting from the URL).

### Step 2: Fetch & Parse

For each promising result from Step 1 (and Step 1b):
- For web search results: use `WebFetch` to retrieve the job posting page
- For Gmail LinkedIn alerts: title/company/location/URL are already extracted in Step 1b; only `WebFetch` the LinkedIn URL if the user wants a detailed evaluation (LinkedIn job pages often require login, so this may fail — fall back to presenting title/company/location only and note that full details need manual review)
- Extract: **job title**, **company**, **location**, **posting date** (or "recent"), **URL**, **key requirements** (brief), **application deadline** (if listed)
- Skip if the URL or company+title combo already exists in `seen_jobs.json`
- Skip if the company+role already appears in `job_search_tracker.csv`

### Step 3: Quick Fit Assessment

For each new job, do a rapid fit check (NOT the full evaluation from `04-job-evaluation.md` - just a quick signal):

- **High match**: Role directly involves your core skills
- **Medium match**: Role is adjacent to your experience
- **Low match**: Role requires significant skills you lack

### Step 4: Deduplicate & Store

1. Add ALL fetched jobs (new and skipped) to `seen_jobs.json` with structure:
```json
{
  "seen": {
    "<url_or_company_title_key>": {
      "title": "...",
      "company": "...",
      "url": "...",
      "first_seen": "YYYY-MM-DD",
      "fit": "high/medium/low",
      "status": "new/skipped/evaluated/ranked/expired"
    }
  }
}
```
2. Only present jobs NOT already in the seen list or tracker.

### Step 5: Present Results

Present new jobs in a table sorted by fit (high first):

```
## New Job Matches - YYYY-MM-DD

Found X new positions (Y high, Z medium, W low match).

| # | Fit | Title | Company | Location | Deadline | URL |
|---|-----|-------|---------|----------|----------|-----|
| 1 | High | ... | ... | ... | ... | [Link](...) |

### High-Match Highlights
For each high-match job, add 2-3 bullet points:
- Why it matches your profile
- Key requirements to check
- Any red flags
```

After presenting, ask:
> "Want me to evaluate any of these in detail? Just give me the number(s)."

If the user picks a number, invoke the **job-application-assistant** skill workflow (fit evaluation first, then CV + cover letter if approved).

If the run found many new jobs (roughly 8+), also suggest `/rank` - it batch-scores all new postings against the full fit framework and returns a ranked shortlist, which beats eyeballing a long table. (`/rank` sets the `ranked` and `expired` status values in `seen_jobs.json`; treat both as already-seen for dedup purposes.)

### Step 6: Update Tracker (Optional)

If the user decides to apply to any job, add a row to `job_search_tracker.csv`.

---

## Important Rules

1. **Never fabricate job postings.** Only present jobs found via actual France Travail CLI, WebSearch/WebFetch, or Gmail results.
2. **Respect deduplication.** Always check seen_jobs.json AND job_search_tracker.csv before presenting.
3. **Focus on configured geographic area.** Skip jobs that require relocation outside the Bretagne/Île-de-France/Nantes footprint or are clearly outside commute range (see `search-queries.md` for location filters).
4. **Only open positions.** Skip postings with expired deadlines or those marked as closed.
5. **Be efficient with WebFetch.** Don't fetch every search result - use titles and snippets to pre-filter before fetching.
6. **Parallel searches.** Use the Agent tool or parallel WebSearch/Bash calls to speed up the search phase.
7. **Gmail is best-effort.** If the Gmail connector isn't authorized or errors out, skip Step 1b silently (after telling the user) rather than failing the whole run.
8. **No Alternance/apprentissage/stage postings.** Bruno is a senior independent consultant, not a student. Drop any posting whose title or contract type contains "Alternance", "Apprenti(e)", "Stage"/"Stagiaire", or "VIE" before it reaches the shortlist — the France Travail API's `--contract` flag can't exclude by type, so filter on title/contract_type text after fetching.
