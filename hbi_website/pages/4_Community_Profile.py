"""HBI Community Profile — Individual LinkedIn profile view."""

import html as html_mod

import pandas as pd
import streamlit as st

from utils.components import (
    inject_custom_css,
    render_avatar_html,
    render_community_research_tags,
    render_institution_tags,
    section_header,
    COMMUNITY_TEAL,
    COMMUNITY_DARK,
    INSTITUTION_COLOR,
)
from utils.linkedin_data_loader import (
    load_li_profiles,
    load_li_experience,
    load_li_education,
    load_li_skills,
    load_li_publications,
    load_li_certifications,
    load_li_research_tags,
    get_filtered_profile_tags,
    get_profile_institution_tags,
)

_esc = lambda s: html_mod.escape(str(s)) if s else ""

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="Community Profile – HBI", page_icon="🤝", layout="wide")
inject_custom_css()

# ── Resolve profile ID ────────────────────────────────────────────────────────
profile_id = st.session_state.get("selected_community_profile") or st.query_params.get("id")

if not profile_id:
    st.warning("No profile selected.")
    if st.button("← Back to Community"):
        st.switch_page("pages/2_HBI_Community.py")
    st.stop()

st.query_params["id"] = profile_id

# ── Load profile ──────────────────────────────────────────────────────────────
profiles = load_li_profiles()
profile = profiles[profiles["profile_id"] == profile_id]

if profile.empty:
    st.error(f"Profile not found: {profile_id}")
    if st.button("← Back to Community"):
        st.switch_page("pages/2_HBI_Community.py")
    st.stop()

p = profile.iloc[0]
name = str(p["full_name"]) if pd.notna(p["full_name"]) else "Unknown"
headline = str(p["headline"]) if pd.notna(p.get("headline")) else ""
location = str(p["location"]) if pd.notna(p.get("location")) else ""
about = str(p["about"]) if pd.notna(p.get("about")) else ""
li_url = str(p["profile_url"]) if pd.notna(p.get("profile_url")) else ""

# ── Related data ──────────────────────────────────────────────────────────────
mem_exp = (
    load_li_experience()
    .query("profile_id == @profile_id")
    .sort_values("sort_order")
)
mem_edu = (
    load_li_education()
    .query("profile_id == @profile_id")
    .sort_values("sort_order")
)
mem_skills = (
    load_li_skills()
    .query("profile_id == @profile_id")
    .sort_values("sort_order")
)
mem_pubs = (
    load_li_publications()
    .query("profile_id == @profile_id")
    .sort_values("sort_order")
)
_AD_PATTERN = r"(?i)(why am i seeing this ad|manage your ad preferences)"
mem_certs = (
    load_li_certifications()
    .query("profile_id == @profile_id")
    .pipe(lambda df: df[~df["title"].astype(str).str.contains(_AD_PATTERN, regex=True, na=False)])
    .sort_values("sort_order")
)

# Research tags — two-pass Members-vocabulary filter
research_tags = get_filtered_profile_tags(profile_id)

# ── Current title for subtitle ────────────────────────────────────────────────
current_exp = mem_exp[
    mem_exp["end_date"].isna()
    | mem_exp["end_date"].astype(str).str.strip().isin(["", "nan", "None", "Present"])
]
if not current_exp.empty:
    c = current_exp.iloc[0]
    current_title = str(c["title"]) if pd.notna(c["title"]) else ""
    current_company = str(c["company"]) if pd.notna(c["company"]) else ""
elif not mem_exp.empty:
    c = mem_exp.iloc[0]
    current_title = str(c["title"]) if pd.notna(c["title"]) else ""
    current_company = str(c["company"]) if pd.notna(c["company"]) else ""
else:
    current_title = ""
    current_company = ""

# ── Profile banner ────────────────────────────────────────────────────────────
avatar = render_avatar_html(name, 110)

banner_html = (
    f'<div style="background:linear-gradient(135deg,{COMMUNITY_TEAL} 0%,{COMMUNITY_DARK} 100%);'
    f'height:180px;border-radius:10px;"></div>'
    f'<div style="margin-top:-60px;padding-left:2rem;display:flex;'
    f'align-items:flex-end;gap:1.5rem;margin-bottom:1.2rem;">'
    f'<div style="border:4px solid #fff;border-radius:50%;'
    f'box-shadow:0 2px 10px rgba(0,0,0,0.15);line-height:0;">{avatar}</div>'
    f'<div style="padding-bottom:8px;">'
    f'<div style="font-size:1.8rem;font-weight:700;color:#1A1A1A;'
    f'margin:0;line-height:1.3;">{_esc(name)}</div>'
    f'</div></div>'
)
st.markdown(banner_html, unsafe_allow_html=True)

# ── Navigation row ────────────────────────────────────────────────────────────
nav1, nav2, _ = st.columns([1, 1, 2])
with nav1:
    if st.button("← Back to Community"):
        st.switch_page("pages/2_HBI_Community.py")
with nav2:
    if li_url:
        st.link_button("View on LinkedIn ↗", li_url)

# ═══════════════════════════════════════════════════════════════════════════════
# SECTIONS
# ═══════════════════════════════════════════════════════════════════════════════

# ── About ─────────────────────────────────────────────────────────────────────
if about:
    section_header("About", color=COMMUNITY_TEAL)
    st.markdown(about)

# ── Research Areas ────────────────────────────────────────────────────────────
if research_tags:
    section_header("Research Areas", color=COMMUNITY_TEAL)
    st.markdown(
        render_community_research_tags(research_tags, max_show=50),
        unsafe_allow_html=True,
    )
# ── Organizations & Institutions ─────────────────────────────────────────────
profile_institution_tags = get_profile_institution_tags(profile_id)
if profile_institution_tags:
    section_header("Organizations & Institutions", color=INSTITUTION_COLOR)
    st.markdown(
        render_institution_tags(profile_institution_tags, max_show=50),
        unsafe_allow_html=True,
    )
# ── Experience ────────────────────────────────────────────────────────────────
if not mem_exp.empty:
    section_header("Experience", color=COMMUNITY_TEAL)
    for _, exp in mem_exp.iterrows():
        title = str(exp["title"]) if pd.notna(exp["title"]) else ""
        company = str(exp["company"]) if pd.notna(exp["company"]) else ""
        emp_type = str(exp["employment_type"]) if pd.notna(exp.get("employment_type")) else ""
        loc = str(exp["location"]) if pd.notna(exp.get("location")) else ""
        start = str(exp["start_date"]) if pd.notna(exp.get("start_date")) else ""
        end = str(exp["end_date"]) if pd.notna(exp.get("end_date")) else "Present"
        duration = str(exp["duration"]) if pd.notna(exp.get("duration")) else ""
        desc = str(exp["description"]) if pd.notna(exp.get("description")) else ""

        header_parts = [p for p in [title, emp_type] if p]
        if header_parts:
            st.markdown(f"**{_esc(' · '.join(header_parts))}**")
        if company:
            meta = " · ".join(p for p in [company, loc] if p)
            st.caption(meta)
        if start or end:
            date_range = f"{start} – {end}" if start else end
            if duration:
                date_range += f" · {duration}"
            st.caption(date_range)
        if desc:
            with st.expander("Details"):
                st.markdown(desc)
        st.markdown("")

# ── Education ─────────────────────────────────────────────────────────────────
if not mem_edu.empty:
    section_header("Education", color=COMMUNITY_TEAL)
    for _, ed in mem_edu.iterrows():
        school = str(ed["school"]) if pd.notna(ed["school"]) else ""
        degree = str(ed["degree"]) if pd.notna(ed.get("degree")) else ""
        field = str(ed["field_of_study"]) if pd.notna(ed.get("field_of_study")) else ""
        start = str(ed["start_date"]) if pd.notna(ed.get("start_date")) else ""
        end = str(ed["end_date"]) if pd.notna(ed.get("end_date")) else ""
        desc = str(ed["description"]) if pd.notna(ed.get("description")) else ""

        degree_parts = [p for p in [degree, field] if p]
        if degree_parts:
            st.markdown(f"**{_esc(', '.join(degree_parts))}**")
        if school:
            st.caption(school)
        if start or end:
            st.caption(" – ".join(p for p in [start, end] if p))
        if desc:
            with st.expander("Details"):
                st.markdown(desc)
        st.markdown("")

# ── Skills ────────────────────────────────────────────────────────────────────
if not mem_skills.empty:
    section_header("Skills", color=COMMUNITY_TEAL)
    skill_names = mem_skills["skill_name"].dropna().tolist()
    pills_html = "".join(
        f'<span class="li-tag">{_esc(s)}</span>' for s in skill_names[:40]
    )
    if len(skill_names) > 40:
        pills_html += f'<span class="li-tag">+{len(skill_names)-40} more</span>'
    st.markdown(
        f'<div style="line-height:2;">{pills_html}</div>',
        unsafe_allow_html=True,
    )

# ── Publications ──────────────────────────────────────────────────────────────
if not mem_pubs.empty:
    section_header("Publications", color=COMMUNITY_TEAL)
    for _, pub in mem_pubs.iterrows():
        ptitle = str(pub["title"]) if pd.notna(pub["title"]) else ""
        publisher = str(pub["publisher"]) if pd.notna(pub.get("publisher")) else ""
        pub_date = str(pub["pub_date"]) if pd.notna(pub.get("pub_date")) else ""
        purl = str(pub["url"]) if pd.notna(pub.get("url")) else ""
        raw = str(pub["raw_text"]) if pd.notna(pub.get("raw_text")) else ""
        display = ptitle or raw
        if display:
            if purl:
                st.markdown(f"- [{_esc(display)}]({purl})")
            else:
                st.markdown(f"- {_esc(display)}")
            meta = " · ".join(p for p in [publisher, pub_date] if p)
            if meta:
                st.caption(f"  {meta}")

# ── Certifications ────────────────────────────────────────────────────────────
if not mem_certs.empty:
    section_header("Certifications", color=COMMUNITY_TEAL)
    for _, cert in mem_certs.iterrows():
        ctitle = str(cert["title"]) if pd.notna(cert["title"]) else ""
        issuer = str(cert["issuer"]) if pd.notna(cert.get("issuer")) else ""
        issue_date = str(cert["issue_date"]) if pd.notna(cert.get("issue_date")) else ""
        expiry = str(cert["expiry_date"]) if pd.notna(cert.get("expiry_date")) else ""
        curl = str(cert["credential_url"]) if pd.notna(cert.get("credential_url")) else ""

        if ctitle:
            if curl:
                st.markdown(f"**[{_esc(ctitle)}]({curl})**")
            else:
                st.markdown(f"**{_esc(ctitle)}**")
        meta_parts = [p for p in [issuer, issue_date] if p]
        if expiry:
            meta_parts.append(f"Expires {expiry}")
        if meta_parts:
            st.caption(" · ".join(meta_parts))
        st.markdown("")

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.caption("Data sourced from LinkedIn via HBI Crawler · Hotchkiss Brain Institute")
