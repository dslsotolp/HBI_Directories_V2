"""Cached data loading for the HBI Members website."""

from pathlib import Path

import pandas as pd
import streamlit as st

from utils.institution_aliases import normalize_institution

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "output" / "csv"
KEYWORD_DIR = Path(__file__).resolve().parent.parent.parent / "keyword_dictionary"


@st.cache_data(ttl=3600)
def load_members():
    return pd.read_csv(DATA_DIR / "dim_members.csv")


@st.cache_data(ttl=3600)
def load_positions():
    return pd.read_csv(DATA_DIR / "dim_positions.csv")


@st.cache_data(ttl=3600)
def load_research_areas():
    return pd.read_csv(DATA_DIR / "dim_research_areas.csv")


@st.cache_data(ttl=3600)
def load_publishable_research_tags() -> pd.DataFrame:
    """Return a deduplicated DataFrame of (member_id, area) using research_tag_publishable
    from umls_match_all_profiles_final.csv, joined to members via source_url."""
    tags = pd.read_csv(KEYWORD_DIR / "umls_match_all_profiles_final.csv")
    members = load_members()[["member_id", "source_url"]]

    tags = tags.merge(members, on="source_url", how="left")
    tags = tags[tags["member_id"].notna()]
    tags = tags[tags["research_tag_publishable"].notna()]
    tags = tags[tags["research_tag_publishable"].str.strip() != ""]

    # Deduplicate: one row per (member_id, tag)
    result = (
        tags[["member_id", "research_tag_publishable"]]
        .drop_duplicates()
        .rename(columns={"research_tag_publishable": "area"})
        .sort_values(["member_id", "area"])
        .reset_index(drop=True)
    )
    return result


@st.cache_data(ttl=3600)
def load_education():
    return pd.read_csv(DATA_DIR / "dim_education.csv")


@st.cache_data(ttl=3600)
def load_member_institution_tags() -> pd.DataFrame:
    """Return (member_id, institution_tag) rows from members' educational background."""
    edu = load_education()[["member_id", "institution"]].rename(columns={"institution": "raw_name"})
    combined = edu.dropna(subset=["raw_name"]).copy()
    combined["institution_tag"] = combined["raw_name"].apply(normalize_institution)
    return (
        combined[combined["institution_tag"].str.strip() != ""]
        [["member_id", "institution_tag"]]
        .drop_duplicates()
        .reset_index(drop=True)
    )


@st.cache_data(ttl=3600)
def load_publications():
    return pd.read_csv(DATA_DIR / "dim_publications.csv")


@st.cache_data(ttl=3600)
def load_activities():
    return pd.read_csv(DATA_DIR / "dim_activities.csv")


@st.cache_data(ttl=3600)
def load_contact_info():
    return pd.read_csv(DATA_DIR / "dim_contact_info.csv")


@st.cache_data(ttl=3600)
def load_news():
    return pd.read_csv(DATA_DIR / "dim_news.csv")


@st.cache_data(ttl=3600)
def build_directory_data():
    """Pre-join members with primary position and research areas for the directory."""
    members = load_members()
    positions = load_positions()
    research_areas = load_publishable_research_tags()

    # Primary position per member (lowest sort_order)
    pos_sorted = positions.sort_values(["member_id", "sort_order"])
    primary_pos = (
        pos_sorted.groupby("member_id")
        .first()[["title", "department", "faculty"]]
        .reset_index()
    )

    # Research areas as list per member
    areas_by_member = (
        research_areas.groupby("member_id")["area"]
        .apply(lambda x: x.dropna().tolist())
        .to_dict()
    )

    # HBI membership status (Full Member, Associate Member, etc. followed by HBI row)
    _HBI_STATUSES = {
        "Full Member", "Associate Member", "Affiliate Member",
        "Emeritus Member", "Full Member and Chair", "Joint Member",
        "Primary Member", "Principal Member",
    }
    hbi_rows = set(
        zip(
            positions[positions["title"] == "Hotchkiss Brain Institute"]["member_id"],
            positions[positions["title"] == "Hotchkiss Brain Institute"]["sort_order"],
        )
    )
    status_rows = positions[positions["title"].isin(_HBI_STATUSES)].copy()
    status_rows["hbi_follows"] = [
        (mid, so + 1) in hbi_rows
        for mid, so in zip(status_rows["member_id"], status_rows["sort_order"])
    ]
    hbi_status = (
        status_rows[status_rows["hbi_follows"]]
        .sort_values("sort_order")
        .drop_duplicates("member_id", keep="first")
        .set_index("member_id")["title"]
        .to_dict()
    )

    # Merge
    directory = members.merge(primary_pos, on="member_id", how="left")
    directory["research_areas_list"] = directory["member_id"].map(
        lambda mid: areas_by_member.get(mid, [])
    )
    directory["hbi_membership"] = directory["member_id"].map(
        lambda mid: hbi_status.get(mid, "")
    )

    return directory
