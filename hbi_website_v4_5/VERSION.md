# HBI Directory Website v4.5 — Publication Track

Created from the active v4.4 site on 2026-08-14. The publication-track profile
design makes the hybrid UMLS–MeSH taxonomy the sole public research-area method.

## v4.5 profile changes

- Replaces Areas of Expertise 1, 2, and 3 labels with **Areas of Research**.
- Shows source/profile wording and standardized UMLS-resolved, MeSH-preferred
  terms together in Areas of Research.
- Shows broad HBI groupings in a parallel **Research Themes** section.
- Presents publication-based keywords publicly as **Research Keywords from
  Publications**, without using a database vendor in the feature name.
- Moves the official UCalgary profile link from the page header into Research
  Footprint.
- Orders research profiles as UCalgary, Google Scholar, ORCID, ResearchGate,
  Scopus, then other verified profiles such as PubMed and Academia.edu.
- Keeps labs, research groups, centres, institutes, networks, and associated
  websites in the separate Labs, Groups & Ventures subsection.
- Refreshes explicitly labelled scholarly and research-ecosystem URLs from
  official UCalgary profiles.
- Labels emails found inside an official Preferred method of communication block.
- Preserves each official UCalgary affiliation card independently, including
  repeated position titles attached to different departments or institutes.
- Preserves each explicitly marked UCalgary research title as one atomic phrase,
  so grammatical commas within a title are never mistaken for separate areas.
- Uses source-preserved research phrases consistently in profiles and global
  search, with a legacy-data fallback only when a source page cannot be fetched.
- Moves Areas of Research and Research Themes explanations into compact help
  icons and removes classification-method terminology from the public profile.
- Links every declared area, standardized term, and Research Theme to a shared
  results view listing the other HBI profiles with the same selection.
- Removes decorative browser-tab icons from every publication-site page.
- Uses 4:5 portrait profile photos throughout the site at 150% of their former
  width, with matching rectangular initials fallbacks.
- Keeps the **Researcher-declared areas** subsection visible and shows a neutral
  empty-state message when no researcher-declared wording is available.
- Adopts the animated collapsing portrait hero (prototype Option 4) for live HBI
  member profiles. It contracts to a persistent portrait-and-name bar while
  scrolling and includes responsive and non-supporting-browser fallbacks.
- Enlarges both the expanded and collapsed states of the animated profile hero
  by 25%, including its portrait, name, container, and spacing.
- Enlarges the collapsed sticky state by a further 25% while leaving the
  expanded hero unchanged.
- Enlarges the collapsed sticky state by an additional 25% after visual review.
- Adds a reviewed, field-scoped display correction for Richard Frayne’s
  affiliation title ("Profesor" to "Professor"). The exact member-and-title
  rule is applied only by position loaders and cannot alter research keywords.
- Adds one temporary hidden Aaron Phillips comparison page for three KPI and
  selected-recognition layout explorations; live profiles remain unchanged.
- Applied the dedicated at-a-glance layout to live member profiles, limited to
  Research at a Glance and Selected Recognition; recognition years now display
  as whole years without CSV-derived `.0` suffixes.
- Ordered Selected Recognition entries from newest to oldest, with undated
  entries following dated recognitions.
- Added an accessible question-mark tooltip beside Selected Recognition that
  explains the UCalgary Research profile source and three-entry selection.
- Added the matching source tooltip to Research at a Glance, distinguishing
  publication-derived metrics from the UCalgary-sourced recognition count.
- Matched both at-a-glance headings to the size and weight of the other profile
  section headers.
- Separated publication-derived keywords, metrics, and research connections
  from Research into their own Publications panel; UCalgary-listed publication
  links are labeled separately within that panel.
- Matched the Selected Recognition column height to the KPI grid so both sides
  align at their top and bottom edges.
- Framed the Selected Recognition entries in a soft-white card matching the KPI
  cards' radius and shadow.
- Increased the position and affiliation typography in expanded member-profile
  headers for easier scanning.
- Increased the expanded header-detail typography by a further 20%.
- Added source and methodology tooltips to relevant profile headings, including
  member-specific publication coverage on Publications, and replaced public
  vendor references with neutral indexed-publication wording.
- Expanded Affiliations to show four position/affiliation pairs in a two-column
  grid, with View All reserved for profiles containing more than four entries.
- Grouped Standardized research terms and Research Themes in the right Research
  column and added guidance that their links can identify potential partners or
  collaborators working in the same field.
- Added a tooltip defining researcher-declared areas as unstandardized profile
  wording and directing collaborator discovery to standardized terms and themes.
- Renamed the main Research profile section to Areas of Research, removed its
  duplicate inner heading, and retained the three research-type subheaders.
- Added visible guidance beneath researcher-declared areas explaining that the
  source wording may not be standardized and directing users to standardized
  terms and themes for more consistent collaborator matching.
- Simplified the researcher-declared source wording to “public research profile.”
- Bolded the exact plural Standardized research terms and Research Themes labels
  in the researcher-declared matching guidance.
- Increased those two guidance labels to dark, extra-bold text for stronger
  visual contrast.
- Softened that emphasis to a medium-dark bold treatment at roughly 75% of the
  previous visual intensity.
- Matched related-profile “+N more” indicators to the exact dimensions and
  alignment of their neighboring research-keyword pills.
- Reduced the saturation and contrast of the Community teal palette across
  banners, cards, tags, maps, network nodes, links, and hover states.
- Lightened the muted Community teal palette one additional step.
- Restored more teal saturation while keeping the palette softer than the
  original high-contrast treatment.
- Shifted the Community teal palette subtly toward green by approximately 10%.
- Darkened the green-shifted Community palette while retaining its teal base.
- Changed member photos to fit completely inside portrait frames on a neutral
  white surface, preventing transparent or undersized images from appearing cut
  off or exposing the colored initials fallback.

The preserved source snapshots are:

- `hbi_website_backup_4_4_pre_publication_v4_5_20260814_151553/`
- `hbi_website_backup_4_5_preexisting_20260814_151553/`

## v4.4 history

## Areas of Expertise 2 comparison

The original Areas of Expertise methodology and its output remain unchanged.
An experimental, source-preserving **Areas of Expertise 2** section now appears
alongside it on member profiles, with its own searchable explorer page.

- Preserves researcher-declared wording from UCalgary profile fields
- Uses normalized labels to connect spelling and formatting variants
- Adds MeSH concepts and HBI umbrella categories as matching metadata without
  replacing the visible source labels
- Keeps uncertain and unmatched source-declared labels visible for comparison
- Displays accepted standardized MeSH terms and reusable HBI umbrella categories
  as separate tag layers alongside the researcher-declared wording
- Includes accepted medical concepts recovered from legacy research narratives,
  while uncertain narrative fragments remain excluded from public tags
- Covers 361 successfully fetched profiles; 10 UCalgary pages returned HTTP 403

The preserved pre-change snapshot is:

`hbi_website_backup_4_4_pre_expertise2/`

Version 4.3 was created from the completed v4.2 public website on 2026-07-29.
The preserved pre-change snapshot is:

`hbi_website_backup_4_2/`

## v4.3 feature

Member profiles now include an interactive **Research Connections** section
based on the existing 2004–2026 Scopus collection.

- Combined, Topics, and Connections-only views
- Connection grouping by collaborator, affiliated institution, or country
- Exact distinct-publication counts for every grouping
- Exact publication-year filtering shared with Research Keywords from Publications
- Independent left/right controls for 10, 20, 30, 40, or 50 nodes
- Separate minimum-publication thresholds for keywords and connections
- In-place header-arrow sorting on every publication-keyword table column, without
  navigating away from the profile
- Minimum shared-publication threshold
- HBI-collaborator-only filter
- UCalgary-only collaborator and institution filter, including recognized
  UCalgary faculties, schools, institutes, and Scopus naming variants
- Clickable research-keyword and HBI profile nodes
- Hover evidence with publication counts, years, affiliations, and countries
- Complete, year-filtered collaborator, institution, or country table
- Vertically scrollable expanded views and horizontal mobile scrolling
- Edge-to-edge Research Connections diagram with compact nodes and typography
  dynamically derived from browser body text minus approximately two points
- Doubled visualization height so the default 10 keyword and 10 connection
  nodes appear together, with balanced side margins
- Vertical gaps between adjacent keyword and connection nodes reduced by half
- Reduced top and bottom visualization whitespace, with 5, 10, 20, and 50 as
  the available keyword and connection display counts
- Node-count-aware SVG height removes excess heading and legend whitespace in
  larger 20- and 50-node views
- Automatic iframe height follows the rendered SVG, eliminating the internal
  vertical scrollbar for every node-count option while reflowing later sections
- Center researcher node width adapts to the rendered researcher-name length
- All four connection KPIs recalculate for the active HBI-only and
  UCalgary-only collaborator cohort
- Help icons define each connection KPI and clarify Scopus affiliation
  entities and collaborators associated with multiple countries over time
- Other collaborator nodes use neutral slate gray, clearly separating them
  from teal HBI collaborator nodes and legend markers

The visualization loads one compressed, public-safe schema-v2 file per profile from
`data/scopus_connections/`. It does not make live Scopus API calls and does not
contain UCIDs, email addresses, or abstracts.

## Local preview

- v4.2 comparison site: `http://localhost:8504`
- v4.3 public site: `http://localhost:8506`
- unchanged admin site: `http://localhost:8505`
