"""Cached data loading for LinkedIn Community profiles."""

from pathlib import Path

import pandas as pd
import streamlit as st

from utils.institution_aliases import normalize_institution

LINKEDIN_DIR = Path(__file__).resolve().parent.parent.parent / "linkedin_output" / "csv"
KEYWORD_DIR = Path(__file__).resolve().parent.parent.parent / "keyword_dictionary"


@st.cache_data(ttl=3600)
def load_li_profiles() -> pd.DataFrame:
    return pd.read_csv(LINKEDIN_DIR / "linkedin_dim_profiles.csv")


@st.cache_data(ttl=3600)
def load_li_experience() -> pd.DataFrame:
    return pd.read_csv(LINKEDIN_DIR / "linkedin_dim_experience.csv")


@st.cache_data(ttl=3600)
def load_li_education() -> pd.DataFrame:
    return pd.read_csv(LINKEDIN_DIR / "linkedin_dim_education.csv")


@st.cache_data(ttl=3600)
def load_li_skills() -> pd.DataFrame:
    return pd.read_csv(LINKEDIN_DIR / "linkedin_dim_skills.csv")


@st.cache_data(ttl=3600)
def load_li_publications() -> pd.DataFrame:
    df = pd.read_csv(LINKEDIN_DIR / "linkedin_dim_publications.csv")
    # Drop rows where pub_date contains a LinkedIn connection-degree badge
    # (e.g. "1st", "2nd", "3rd", "3rd+") — these are mistakenly scraped
    # connection/suggested-people entries, not real publications.
    connection_degree = df["pub_date"].astype(str).str.match(r"^\d(?:st|nd|rd)\+?$")
    return df[~connection_degree].reset_index(drop=True)


@st.cache_data(ttl=3600)
def load_li_certifications() -> pd.DataFrame:
    return pd.read_csv(LINKEDIN_DIR / "linkedin_dim_certifications.csv")


@st.cache_data(ttl=3600)
def load_li_research_tags() -> pd.DataFrame:
    return pd.read_csv(LINKEDIN_DIR / "linkedin_dim_research_tags.csv")


@st.cache_data(ttl=3600)
def load_li_institution_tags() -> pd.DataFrame:
    """Return (profile_id, institution_tag) rows from education + experience data."""
    edu = load_li_education()[["profile_id", "school"]].rename(columns={"school": "raw_name"})
    exp = load_li_experience()[["profile_id", "company"]].rename(columns={"company": "raw_name"})
    combined = pd.concat([edu, exp], ignore_index=True).dropna(subset=["raw_name"])
    combined = combined.copy()
    combined["institution_tag"] = combined["raw_name"].apply(normalize_institution)
    return (
        combined[combined["institution_tag"].str.strip() != ""]
        [["profile_id", "institution_tag"]]
        .drop_duplicates()
        .reset_index(drop=True)
    )


def get_profile_institution_tags(profile_id: str) -> list[str]:
    """Return sorted institution tags for a single community profile."""
    tags_df = load_li_institution_tags()
    return sorted(
        tags_df.loc[tags_df["profile_id"] == profile_id, "institution_tag"]
        .dropna()
        .unique()
        .tolist()
    )


@st.cache_data(ttl=3600)
def _load_members_tag_vocabulary() -> tuple[dict, dict]:
    """Build lookup tables from the HBI Members' publishable tag vocabulary.

    Returns
    -------
    cuis_to_tag : dict[str, str]
        Individual UMLS CUI code -> canonical research_tag_publishable from Members.
    strings_to_tag : dict[str, str]
        Lowercase tag string -> canonical research_tag_publishable from Members.
        Covers both the publishable tag itself and final_output_simplified_cleaned.
    """
    df = pd.read_csv(KEYWORD_DIR / "umls_match_all_profiles_final.csv")

    # Rows that have a valid publishable tag
    pub = df[df["research_tag_publishable"].notna()].copy()
    pub["_pub"] = pub["research_tag_publishable"].str.strip()
    pub = pub[pub["_pub"] != ""]

    # ── String lookup (lowercase -> canonical) ────────────────────────────
    strings_to_tag: dict[str, str] = {}

    # 1. Direct publishable tag strings
    for tag in pub["_pub"].unique():
        strings_to_tag[tag.lower()] = tag

    # 2. final_output_simplified_cleaned -> publishable tag (adds synonym coverage)
    fsc_rows = pub[pub["final_output_simplified_cleaned"].notna()].copy()
    fsc_rows["_fsc"] = fsc_rows["final_output_simplified_cleaned"].str.strip().str.lower()
    for _, row in (
        fsc_rows[["_fsc", "_pub"]]
        .drop_duplicates("_fsc")
        .iterrows()
    ):
        if row["_fsc"] and row["_fsc"] not in strings_to_tag:
            strings_to_tag[row["_fsc"]] = row["_pub"]

    # ── CUI lookup (individual CUI -> canonical) ──────────────────────────
    cuis_to_tag: dict[str, str] = {}
    pub_cuis = pub[pub["matched_cuis"].notna()].copy()
    for _, row in pub_cuis[["matched_cuis", "_pub"]].iterrows():
        canonical = row["_pub"]
        for cui in str(row["matched_cuis"]).split("|"):
            cui = cui.strip()
            if cui and cui not in cuis_to_tag:
                cuis_to_tag[cui] = canonical

    return cuis_to_tag, strings_to_tag


def _filter_community_tags(rt_df: pd.DataFrame) -> pd.DataFrame:
    """Two-pass Members-vocabulary filter on a LinkedIn research_tags DataFrame.

    Pass 1 (CUI-based): keep rows whose matched_cuis intersects the Members'
    CUI set; display label = the canonical Member tag for that CUI.

    Pass 2 (string fallback): for rows not yet matched, check whether
    final_output_simplified_cleaned (case-insensitive) is in the Members'
    string vocabulary; display label = the canonical Member tag.

    Returns a deduplicated DataFrame with columns [profile_id, display_tag].
    """
    cuis_to_tag, strings_to_tag = _load_members_tag_vocabulary()

    df = rt_df[["profile_id", "matched_cuis", "final_output_simplified_cleaned"]].copy()

    # Pass 1 — CUI match
    def _cui_hit(cuis_str) -> str | None:
        if not pd.notna(cuis_str):
            return None
        for cui in str(cuis_str).split("|"):
            canonical = cuis_to_tag.get(cui.strip())
            if canonical:
                return canonical
        return None

    df["_pass1"] = df["matched_cuis"].apply(_cui_hit)

    # Pass 2 — string match on final_output_simplified_cleaned (rows not yet matched)
    mask_no_hit = df["_pass1"].isna() & df["final_output_simplified_cleaned"].notna()
    df.loc[mask_no_hit, "_pass2"] = (
        df.loc[mask_no_hit, "final_output_simplified_cleaned"]
        .str.strip()
        .str.lower()
        .map(strings_to_tag)
    )

    df["display_tag"] = df["_pass1"].combine_first(df.get("_pass2", pd.Series(dtype=str)))

    matched = (
        df[df["display_tag"].notna()][["profile_id", "display_tag"]]
        .drop_duplicates()
        .reset_index(drop=True)
    )
    return matched


def get_filtered_profile_tags(profile_id: str) -> list[str]:
    """Return filtered, sorted research tags for a single community profile."""
    rt_df = load_li_research_tags()
    profile_rt = rt_df[rt_df["profile_id"] == profile_id]
    if profile_rt.empty:
        return []
    matched = _filter_community_tags(profile_rt)
    return sorted(matched["display_tag"].dropna().unique().tolist())


@st.cache_data(ttl=3600)
def build_community_directory_data() -> pd.DataFrame:
    """Pre-join profiles with current job, location, research tags, and institution tags for the directory."""
    profiles = load_li_profiles()
    experience = load_li_experience()
    research_tags = load_li_research_tags()
    education = load_li_education()

    # ── Current / most-recent experience per profile ──────────────────────────
    exp_sorted = experience.sort_values(["profile_id", "sort_order"])

    _current_mask = (
        exp_sorted["end_date"].isna()
        | exp_sorted["end_date"].astype(str).str.strip().isin(["", "nan", "None", "Present"])
    )
    current_exp = (
        exp_sorted[_current_mask]
        .groupby("profile_id", as_index=False)
        .first()[["profile_id", "title", "company"]]
        .rename(columns={"title": "current_title", "company": "current_company"})
    )
    # Fallback: most recent overall (for profiles with no "current" entry)
    most_recent_exp = (
        exp_sorted
        .groupby("profile_id", as_index=False)
        .first()[["profile_id", "title", "company"]]
        .rename(columns={"title": "recent_title", "company": "recent_company"})
    )

    # ── Research tags: two-pass Members-vocabulary filter ────────────────────
    matched_tags = _filter_community_tags(research_tags)
    tags_by_profile = (
        matched_tags.groupby("profile_id")["display_tag"]
        .apply(lambda x: sorted(set(x.dropna().tolist())))
        .reset_index()
        .rename(columns={"display_tag": "research_tags_list"})
    )

    # ── Education institutions per profile ───────────────────────────────────
    edu_by_profile = (
        education.dropna(subset=["school"])
        .groupby("profile_id")["school"]
        .apply(lambda x: sorted(set(x.dropna().tolist())))
        .reset_index()
        .rename(columns={"school": "education_list"})
    )

    # ── Institution tags per profile (education + experience, normalised) ────
    _edu_inst = education[["profile_id", "school"]].rename(columns={"school": "raw_name"})
    _exp_inst = experience[["profile_id", "company"]].rename(columns={"company": "raw_name"})
    _all_inst = pd.concat([_edu_inst, _exp_inst], ignore_index=True).dropna(subset=["raw_name"]).copy()
    _all_inst["institution_tag"] = _all_inst["raw_name"].apply(normalize_institution)
    _all_inst = _all_inst[_all_inst["institution_tag"].str.strip() != ""]
    inst_by_profile = (
        _all_inst.groupby("profile_id")["institution_tag"]
        .apply(lambda x: sorted(set(x.dropna().tolist())))
        .reset_index()
        .rename(columns={"institution_tag": "institution_tags_list"})
    )

    # ── Assemble directory DataFrame ─────────────────────────────────────────
    dir_df = profiles[
        ["profile_id", "profile_url", "full_name", "headline", "location"]
    ].copy()

    dir_df = dir_df.merge(current_exp, on="profile_id", how="left")
    dir_df = dir_df.merge(most_recent_exp, on="profile_id", how="left")
    dir_df = dir_df.merge(tags_by_profile, on="profile_id", how="left")
    dir_df = dir_df.merge(edu_by_profile, on="profile_id", how="left")
    dir_df = dir_df.merge(inst_by_profile, on="profile_id", how="left")

    # Fill current_title / current_company from fallback when missing
    dir_df["current_title"] = dir_df["current_title"].fillna(dir_df["recent_title"])
    dir_df["current_company"] = dir_df["current_company"].fillna(dir_df["recent_company"])
    dir_df.drop(columns=["recent_title", "recent_company"], inplace=True)

    # Ensure list columns are proper lists, not NaN
    for _lc in ("research_tags_list", "education_list", "institution_tags_list"):
        dir_df[_lc] = dir_df[_lc].apply(lambda x: x if isinstance(x, list) else [])

    # ── Deduplicate by profile_url ────────────────────────────────────────────
    # The re-crawl may have assigned new UUIDs to existing profiles, leaving
    # multiple rows per URL with data split across them.  Collapse each URL
    # group into one row: keep the profile_id that has the richest exp data
    # (i.e. non-null current_title), union list columns across all duplicates.
    if dir_df["profile_url"].duplicated().any():
        scalar_cols = ["full_name", "headline", "location",
                       "current_title", "current_company"]
        list_cols   = ["research_tags_list", "education_list", "institution_tags_list"]

        merged_rows = []
        for url, grp in dir_df.groupby("profile_url", sort=False):
            row: dict = {"profile_url": url}

            # Prefer the profile_id whose row has current_title; else first
            has_title = grp[grp["current_title"].notna()]
            best = has_title.iloc[0] if not has_title.empty else grp.iloc[0]
            row["profile_id"] = best["profile_id"]

            for col in scalar_cols:
                non_null = grp[col].dropna()
                row[col] = non_null.iloc[0] if not non_null.empty else None
            for col in list_cols:
                seen: set = set()
                merged: list = []
                for lst in grp[col]:
                    for item in (lst if isinstance(lst, list) else []):
                        if item not in seen:
                            seen.add(item)
                            merged.append(item)
                row[col] = sorted(merged)
            merged_rows.append(row)

        dir_df = pd.DataFrame(merged_rows)[
            ["profile_url", "profile_id"] + scalar_cols + list_cols
        ]

    return dir_df


@st.cache_data(ttl=3600)
def load_community_map_data() -> pd.DataFrame:
    """
    Return aggregated location data for the community map.

    Columns: city, country, lat, lon, count

    Uses a static geocoding dict (no API) — only locations that can be
    resolved are included. Unresolvable location strings are silently dropped.
    """
    from utils.geo_utils import geocode_location

    profiles = load_li_profiles()
    locs = profiles[["profile_id", "location"]].dropna(subset=["location"]).copy()
    locs = locs[locs["location"].str.strip() != ""]

    # Geocode each location string
    locs["_coords"] = locs["location"].apply(geocode_location)
    locs = locs[locs["_coords"].notna()].copy()
    locs["lat"] = locs["_coords"].apply(lambda c: c[0])
    locs["lon"] = locs["_coords"].apply(lambda c: c[1])

    # Derive display city/country labels (strip LinkedIn work-mode suffix first)
    import re as _re

    def _strip_mode_suffix(s: str) -> str:
        return _re.sub(r"\s*[·•]\s*(?:on-site|remote|hybrid).*$", "", s, flags=_re.I).strip()

    def _city_label(loc_str: str) -> str:
        parts = [p.strip() for p in _strip_mode_suffix(str(loc_str)).split(",")]
        return parts[0] if parts else loc_str

    def _country_label(loc_str: str) -> str:
        parts = [p.strip() for p in _strip_mode_suffix(str(loc_str)).split(",")]
        return parts[-1] if len(parts) >= 2 else ""

    locs["city"] = locs["location"].apply(_city_label)
    locs["country"] = locs["location"].apply(_country_label)

    # Aggregate: count profiles per (city, country, lat, lon)
    agg = (
        locs.groupby(["city", "country", "lat", "lon"], as_index=False)
        .agg(count=("profile_id", "nunique"))
        .sort_values("count", ascending=False)
        .reset_index(drop=True)
    )
    return agg
