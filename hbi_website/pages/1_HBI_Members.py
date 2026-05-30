"""HBI Members — Directory listing + individual profile view (dual-mode)."""

import html as html_mod

import pandas as pd
import streamlit as st

from utils.data_loader import (
    load_members,
    load_positions,
    load_research_areas,
    load_education,
    load_publications,
    load_activities,
    load_contact_info,
    load_news,
    load_publishable_research_tags,
    load_member_institution_tags,
    build_directory_data,
)
from utils.linkedin_data_loader import build_community_directory_data
from utils.components import (
    inject_custom_css,
    render_avatar_html,
    render_research_tags,
    render_institution_tags,
    render_community_card_html,
    render_card_html,
    render_card_grid,
    render_list_row_html,
    render_list_view,
    section_header,
    UCALGARY_RED,
    COMMUNITY_TEAL,
    INSTITUTION_COLOR,
)

_esc = lambda s: html_mod.escape(str(s)) if s else ""

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="HBI Members", page_icon="🧠", layout="wide",
                   initial_sidebar_state="expanded")
inject_custom_css()

# ── Route: directory vs individual profile ───────────────────────────────────
member_id = st.query_params.get("id")

# ═══════════════════════════════════════════════════════════════════════════════
# DIRECTORY MODE
# ═══════════════════════════════════════════════════════════════════════════════
if not member_id:

    # ── Header banner ─────────────────────────────────────────────────────────
    st.markdown(
        """
        <div class="hbi-banner">
            <h1>Member Directory</h1>
            <p>Hotchkiss Brain Institute · University of Calgary</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Cached data ───────────────────────────────────────────────────────────
    directory = build_directory_data()
    members = load_members()
    positions = load_positions()
    research_areas = load_publishable_research_tags()
    education = load_education()

    # ── Sidebar filters ───────────────────────────────────────────────────────
    _MEM_FILTER_KEYS = ["mem_search", "mem_membership", "mem_area", "mem_dept", "mem_faculty", "mem_year"]

    # Apply pending reset BEFORE widgets are instantiated.
    if st.session_state.pop("_mem_reset", False):
        st.session_state["mem_search"] = ""
        st.session_state["mem_membership"] = "All"
        st.session_state["mem_area"] = ""
        st.session_state["mem_dept"] = "All"
        st.session_state["mem_faculty"] = "All"
        if "mem_year" in st.session_state:
            del st.session_state["mem_year"]
        st.session_state["mem_page"] = 0

    with st.sidebar:
        st.markdown('<div style="height:70px"></div>', unsafe_allow_html=True)
        st.markdown('<p style="font-size:1.4rem; font-weight:700; margin-bottom:0.4rem;">Search</p>', unsafe_allow_html=True)
        search_query = st.text_input(
            "Search",
            placeholder="Name, keyword, research area…",
            label_visibility="collapsed",
            key="mem_search",
        )

        st.markdown('<p style="font-size:1.4rem; font-weight:700; margin-bottom:0.4rem;">Filters</p>', unsafe_allow_html=True)

        _membership_order = ["Full Member", "Associate Member", "Emeritus Member"]
        hbi_statuses_raw = directory["hbi_membership"].replace("", pd.NA).dropna().unique().tolist()
        hbi_statuses = [s for s in _membership_order if s in hbi_statuses_raw] + \
                       [s for s in sorted(hbi_statuses_raw) if s not in _membership_order]
        sel_membership = st.selectbox(
            "Membership Status",
            ["All"] + hbi_statuses,
            index=0,
            key="mem_membership",
        )

        filter_area = st.text_input("Research Area", placeholder="e.g. neuroscience", key="mem_area")

        _dept_options = sorted(
            positions["department"]
            .dropna()
            .loc[lambda s: s.str.startswith("Department of")]
            .str.split("|").str[0]
            .str.strip()
            .str.replace(r"^Department of\s+", "", regex=True)
            .unique()
            .tolist()
        )
        sel_dept = st.selectbox("Department", ["All"] + _dept_options, index=0, key="mem_dept")

        _known_faculties = {
            "cumming school of medicine",
            "schulich school of engineering",
            "faculty of science",
            "faculty of arts",
            "faculty of nursing",
            "faculty of kinesiology",
            "faculty of veterinary medicine",
            "faculty of social work",
            "faculty of education",
            "faculty of law",
            "haskayne school of business",
            "werklund school of education",
        }
        _faculty_options = sorted(
            v for v in positions["faculty"].dropna().unique().tolist()
            if v.lower() in _known_faculties
        )
        sel_faculty = st.selectbox("Faculty", ["All"] + _faculty_options, index=0, key="mem_faculty")

        edu_years = education["year"].dropna()
        year_range = None
        if not edu_years.empty:
            yr_min_full, yr_max_full = int(edu_years.min()), int(edu_years.max())
            if yr_min_full < yr_max_full:
                year_range = st.slider(
                    "Highest Degree Earned (Year)",
                    yr_min_full,
                    yr_max_full,
                    (yr_min_full, yr_max_full),
                    key="mem_year",
                )

        st.markdown("---")
        if st.button("🔄 Reset All Filters", use_container_width=True):
            st.session_state["_mem_reset"] = True
            st.rerun()

    # ── Apply filters ─────────────────────────────────────────────────────────
    ids = set(members["member_id"])

    if search_query:
        q = search_query.lower()
        name_hit = set(
            members[members["name"].str.lower().str.contains(q, na=False)]["member_id"]
        )
        area_hit = set(
            research_areas[
                research_areas["area"].str.lower().str.contains(q, na=False)
            ]["member_id"]
        )
        pos_hit = set(
            positions[
                positions["title"].str.lower().str.contains(q, na=False)
                | positions["department"].str.lower().str.contains(q, na=False)
            ]["member_id"]
        )
        ids &= name_hit | area_hit | pos_hit

    if filter_area:
        fa = filter_area.lower()
        ids &= set(
            research_areas[
                research_areas["area"].str.lower().str.contains(fa, na=False)
            ]["member_id"]
        )

    if sel_membership != "All":
        ids &= set(directory[directory["hbi_membership"] == sel_membership]["member_id"])

    if sel_dept != "All":
        _dept_full = f"Department of {sel_dept}"
        ids &= set(
            positions[positions["department"].str.split("|").str[0].str.strip() == _dept_full]["member_id"]
        )

    if sel_faculty != "All":
        ids &= set(
            positions[positions["faculty"] == sel_faculty]["member_id"]
        )

    if year_range:
        yr_lo, yr_hi = year_range
        if (yr_lo, yr_hi) != (yr_min_full, yr_max_full):
            _DEGREE_RANK = {
                "phd": 5, "ph.d": 5, "doctor of philosophy": 5, "d.phil": 5,
                "md": 4, "m.d": 4, "d.v.m": 4,
                "msc": 3, "m.sc": 3, "master of science": 3,
                "ma": 3, "m.a": 3, "master of arts": 3, "meng": 3,
                "bsc": 2, "b.sc": 2, "b.sc.": 2, "bsc.": 2,
                "bachelor of science": 2,
                "ba": 2, "b.a": 2, "bachelor of arts": 2,
                "beng": 2, "b.eng": 2,
            }
            _edu = education.dropna(subset=["year"]).copy()
            _edu["_rank"] = _edu["degree"].str.lower().str.strip().map(_DEGREE_RANK).fillna(0)
            _top = _edu.sort_values("_rank", ascending=False).drop_duplicates("member_id", keep="first")
            ids &= set(
                _top[(_top["year"] >= yr_lo) & (_top["year"] <= yr_hi)]["member_id"]
            )

    filtered = (
        directory[directory["member_id"].isin(ids)]
        .sort_values("name")
        .reset_index(drop=True)
    )

    # ── Results count + view toggle + per-page selector ───────────────────────
    rcount_col, toggle_col, perpage_col = st.columns([3, 1, 1])
    with rcount_col:
        st.markdown(f"Showing **{len(filtered)}** of **{len(members)}** members")
    with toggle_col:
        st.markdown("**View mode**")
        view_mode = st.selectbox(
            "View mode", ["Grid", "List"], index=0, label_visibility="collapsed"
        )
    with perpage_col:
        st.markdown("**Profiles per Page**")
        per_page_options = ["25", "50", "100", "All"]
        per_page_choice = st.selectbox(
            "Profiles per Page", per_page_options, index=0, label_visibility="collapsed"
        )

    # ── Export button (sidebar) ───────────────────────────────────────────────
    with st.sidebar:
        if not filtered.empty:
            export = filtered[["name", "title", "department", "faculty", "profile_url"]].copy()
            export.columns = ["Name", "Primary Position", "Department", "Faculty", "Profile URL"]
            export["Research Areas"] = filtered["research_areas_list"].apply(
                lambda x: "; ".join(str(a) for a in x) if isinstance(x, list) else ""
            )
            st.download_button(
                "📥 Download Filtered Results",
                export.to_csv(index=False),
                "hbi_members_filtered.csv",
                "text/csv",
                use_container_width=True,
            )

    # ── Pagination setup ──────────────────────────────────────────────────────
    PER_PAGE = len(filtered) if per_page_choice == "All" else int(per_page_choice)
    total_pages = max(1, -(-len(filtered) // PER_PAGE)) if PER_PAGE > 0 else 1

    _fhash = hash((
        search_query, filter_area, sel_membership,
        sel_dept, sel_faculty, str(year_range), per_page_choice,
    ))
    if st.session_state.get("_fh") != _fhash:
        st.session_state["dir_page"] = 0
        st.session_state["_fh"] = _fhash

    page = max(0, min(st.session_state.get("dir_page", 0), total_pages - 1))
    start_idx = page * PER_PAGE
    page_data = filtered.iloc[start_idx : start_idx + PER_PAGE]

    # ── Member card grid / list ───────────────────────────────────────────────
    if page_data.empty:
        st.info("No members match your current filters. Try broadening your search.")
    else:
        if view_mode == "Grid":
            cards = []
            for _, row in page_data.iterrows():
                mid = row["member_id"]
                nm = str(row["name"]) if pd.notna(row["name"]) else "Unknown"
                title = str(row["title"]) if pd.notna(row.get("title")) else ""
                dept = str(row["department"]) if pd.notna(row.get("department")) else ""
                areas = row.get("research_areas_list", [])
                if not isinstance(areas, list):
                    areas = []
                cards.append(render_card_html(nm, title, dept, areas, member_id=mid))
            st.markdown(render_card_grid(cards), unsafe_allow_html=True)
        else:
            rows_html = []
            for _, row in page_data.iterrows():
                mid = row["member_id"]
                nm = str(row["name"]) if pd.notna(row["name"]) else "Unknown"
                title = str(row["title"]) if pd.notna(row.get("title")) else ""
                dept = str(row["department"]) if pd.notna(row.get("department")) else ""
                areas = row.get("research_areas_list", [])
                if not isinstance(areas, list):
                    areas = []
                rows_html.append(render_list_row_html(nm, title, dept, areas, member_id=mid))
            st.markdown(render_list_view(rows_html), unsafe_allow_html=True)

        # ── Pagination controls ───────────────────────────────────────────────
        st.markdown("")
        c1, c2, c3, c4, c5 = st.columns([1, 1, 2, 1, 1])
        with c1:
            if st.button("⏮ First", disabled=page == 0, key="pg_first"):
                st.session_state["dir_page"] = 0
                st.rerun()
        with c2:
            if st.button("◀ Prev", disabled=page == 0, key="pg_prev"):
                st.session_state["dir_page"] = page - 1
                st.rerun()
        with c3:
            st.markdown(
                f"<div style='text-align:center;padding:8px 0;'>"
                f"Page <b>{page + 1}</b> of <b>{total_pages}</b></div>",
                unsafe_allow_html=True,
            )
        with c4:
            if st.button("Next ▶", disabled=page >= total_pages - 1, key="pg_next"):
                st.session_state["dir_page"] = page + 1
                st.rerun()
        with c5:
            if st.button("Last ⏭", disabled=page >= total_pages - 1, key="pg_last"):
                st.session_state["dir_page"] = total_pages - 1
                st.rerun()

    st.markdown("---")
    st.caption("Data sourced from UCalgary Profiles · Hotchkiss Brain Institute")

# ═══════════════════════════════════════════════════════════════════════════════
# PROFILE MODE
# ═══════════════════════════════════════════════════════════════════════════════
else:
    # Keep URL bookmarkable
    st.query_params["id"] = member_id

    # ── Load member ───────────────────────────────────────────────────────────
    members = load_members()
    member = members[members["member_id"] == member_id]

    if member.empty:
        st.error(f"Member not found: {member_id}")
        if st.button("← Back to Directory"):
            st.query_params.clear()
            st.rerun()
        st.stop()

    m = member.iloc[0]
    name = str(m["name"]) if pd.notna(m["name"]) else "Unknown"
    profile_url = str(m["profile_url"]) if pd.notna(m.get("profile_url")) else None
    honorific = str(m["honorific"]) if pd.notna(m.get("honorific")) else ""
    biography = str(m["biography"]) if pd.notna(m.get("biography")) else ""
    looking_for = str(m["looking_for"]) if pd.notna(m.get("looking_for")) else ""

    # ── Related data ──────────────────────────────────────────────────────────
    mem_positions = (
        load_positions()
        .query("member_id == @member_id")
        .sort_values("sort_order")
    )
    mem_areas = (
        load_publishable_research_tags()
        .query("member_id == @member_id")
        .sort_values("area")
    )
    mem_edu = (
        load_education()
        .query("member_id == @member_id")
        .sort_values("sort_order")
    )
    mem_pubs = (
        load_publications()
        .query("member_id == @member_id")
        .sort_values("sort_order")
    )
    mem_acts = (
        load_activities()
        .query("member_id == @member_id")
        .sort_values("sort_order")
    )
    mem_contact = load_contact_info().query("member_id == @member_id")
    mem_news = (
        load_news()
        .query("member_id == @member_id")
        .sort_values("sort_order")
    )

    # ── Profile banner + avatar ───────────────────────────────────────────────
    display_name = f"{honorific} {name}".strip() if honorific else name
    avatar = render_avatar_html(name, 110)

    banner_html = (
        f'<div style="background:linear-gradient(135deg,{UCALGARY_RED} 0%,#8B0015 100%);'
        f'height:180px;border-radius:10px;"></div>'
        f'<div style="margin-top:-60px;padding-left:2rem;display:flex;'
        f'align-items:flex-end;gap:1.5rem;margin-bottom:1.2rem;">'
        f'<div style="border:4px solid #fff;border-radius:50%;'
        f'box-shadow:0 2px 10px rgba(0,0,0,0.15);line-height:0;">{avatar}</div>'
        f'<div style="padding-bottom:8px;">'
        f'<div style="font-size:1.8rem;font-weight:700;color:#1A1A1A;'
        f'margin:0;line-height:1.3;">{_esc(display_name)}</div>'
        f'</div></div>'
    )

    st.markdown(banner_html, unsafe_allow_html=True)

    # ── Navigation row ────────────────────────────────────────────────────────
    nav1, nav2, _ = st.columns([1, 1, 2])
    with nav1:
        if st.button("← Back to Directory"):
            st.query_params.clear()
            st.rerun()
    with nav2:
        if profile_url:
            st.link_button("View on UCalgary ↗", profile_url)

    # ── Positions ─────────────────────────────────────────────────────────────
    if not mem_positions.empty:
        section_header("Positions")
        for _, pos in mem_positions.iterrows():
            ptitle = str(pos["title"]) if pd.notna(pos["title"]) else ""
            pdept = str(pos["department"]) if pd.notna(pos["department"]) else ""
            pfac = str(pos["faculty"]) if pd.notna(pos["faculty"]) else ""
            sub = " · ".join(p for p in [pdept, pfac] if p)
            if ptitle:
                st.markdown(f"**{_esc(ptitle)}**")
            if sub:
                st.caption(sub)

    # ── Contact Information ───────────────────────────────────────────────────
    if not mem_contact.empty:
        section_header("Contact Information")
        for _, c in mem_contact.iterrows():
            ctype = str(c["contact_type"]) if pd.notna(c["contact_type"]) else ""
            label = str(c["label"]) if pd.notna(c["label"]) else ctype.title()
            value = str(c["value"]) if pd.notna(c["value"]) else ""
            url = str(c["url"]) if pd.notna(c["url"]) else ""

            if ctype == "email" and value:
                st.markdown(f"**{_esc(label)}:** [{_esc(value)}](mailto:{value})")
            elif url:
                display = value if value else url
                st.markdown(f"**{_esc(label)}:** [{_esc(display)}]({url})")
            elif value:
                st.markdown(f"**{_esc(label)}:** {_esc(value)}")

    # ── Background ────────────────────────────────────────────────────────────
    if biography or looking_for or not mem_edu.empty:
        section_header("Background")

        if biography:
            st.markdown(biography)
            st.markdown("")

        if looking_for:
            st.markdown("##### Looking For")
            st.markdown(looking_for)
            st.markdown("")

        if not mem_edu.empty:
            st.markdown("##### Educational Background")
            for _, ed in mem_edu.iterrows():
                degree = str(ed["degree"]) if pd.notna(ed["degree"]) else ""
                field = str(ed["field_of_study"]) if pd.notna(ed.get("field_of_study")) else ""
                inst = str(ed["institution"]) if pd.notna(ed["institution"]) else ""
                year = str(int(ed["year"])) if pd.notna(ed["year"]) else ""
                parts = [p for p in [degree, field, inst, year] if p]
                if parts:
                    st.markdown(f"- {', '.join(parts)}")

        # Affiliated Organizations
        _member_inst_tags = load_member_institution_tags()
        _this_inst_tags = sorted(
            _member_inst_tags.loc[
                _member_inst_tags["member_id"] == member_id, "institution_tag"
            ].dropna().unique().tolist()
        )
        if _this_inst_tags:
            st.markdown("##### Affiliated Organizations")
            st.markdown(
                render_institution_tags(_this_inst_tags, max_show=50),
                unsafe_allow_html=True,
            )

    # ── Research Areas ────────────────────────────────────────────────────────
    if not mem_areas.empty:
        section_header("Research")
        st.markdown("##### Areas of Research")
        areas_list = mem_areas["area"].dropna().tolist()
        st.markdown(
            render_research_tags(areas_list, max_show=50),
            unsafe_allow_html=True,
        )

    # ── Publications ──────────────────────────────────────────────────────────
    if not mem_pubs.empty:
        section_header("Publications")
        for _, pub in mem_pubs.iterrows():
            ptitle = str(pub["title"]) if pd.notna(pub["title"]) else ""
            purl = str(pub["url"]) if pd.notna(pub["url"]) else ""
            raw = str(pub["raw_text"]) if pd.notna(pub["raw_text"]) else ""
            display = ptitle or raw
            if purl and display:
                st.markdown(f"- [{_esc(display)}]({purl})")
            elif display:
                st.markdown(f"- {_esc(display)}")
            elif purl:
                st.markdown(f"- [{purl}]({purl})")

    # ── Activities ────────────────────────────────────────────────────────────
    if not mem_acts.empty:
        section_header("Activities")
        for cat in mem_acts["category"].dropna().unique():
            cat_rows = mem_acts[mem_acts["category"] == cat]
            st.markdown(f"**{str(cat).title()}**")
            items, seen = [], set()
            for _, act in cat_rows.iterrows():
                text = str(act["title"]) if pd.notna(act["title"]) else ""
                key = text[:80]
                if not text or key in seen:
                    continue
                seen.add(key)
                items.append(text[:200] + ("…" if len(text) > 200 else ""))
            for item in items[:5]:
                st.markdown(f"- {item}")
            if len(items) > 5:
                with st.expander(f"Show all {len(items)} items"):
                    for item in items[5:]:
                        st.markdown(f"- {item}")

    # ── News ──────────────────────────────────────────────────────────────────
    if not mem_news.empty:
        section_header("News")
        for _, n in mem_news.iterrows():
            headline = str(n["headline"]) if pd.notna(n["headline"]) else ""
            source = str(n["source"]) if pd.notna(n["source"]) else ""
            date = str(int(n["date"])) if pd.notna(n["date"]) else ""
            nurl = str(n["url"]) if pd.notna(n["url"]) else ""
            if headline:
                if nurl:
                    st.markdown(f"📰 [{_esc(headline)}]({nurl})")
                else:
                    st.markdown(f"📰 {_esc(headline)}")
                meta = " · ".join(p for p in [source, date] if p)
                if meta:
                    st.caption(meta)

    # ── Related HBI Community Profiles ───────────────────────────────────────
    if not mem_areas.empty:
        _member_tags = set(t.lower() for t in mem_areas["area"].dropna().tolist())
        if _member_tags:
            _community = build_community_directory_data()

            def _overlap(tags: list) -> int:
                return sum(1 for t in tags if t.lower() in _member_tags)

            _community["_overlap"] = _community["research_tags_list"].apply(_overlap)
            _related = (
                _community[_community["_overlap"] > 0]
                .sort_values("_overlap", ascending=False)
                .head(6)
            )

            if not _related.empty:
                section_header("Related HBI Community Profiles", color=COMMUNITY_TEAL)
                st.caption("LinkedIn profiles from the HBI Community with overlapping research areas.")
                _cards = []
                for _, cr in _related.iterrows():
                    _cards.append(
                        render_community_card_html(
                            name=str(cr["full_name"]) if pd.notna(cr["full_name"]) else "Unknown",
                            current_title=str(cr["current_title"]) if pd.notna(cr.get("current_title")) else "",
                            current_company=str(cr["current_company"]) if pd.notna(cr.get("current_company")) else "",
                            location=str(cr["location"]) if pd.notna(cr.get("location")) else "",
                            tags=cr.get("research_tags_list", []),
                            profile_id=str(cr["profile_id"]),
                        )
                    )
                st.markdown(render_card_grid(_cards), unsafe_allow_html=True)
                st.page_link(
                    "pages/2_HBI_Community.py",
                    label="View all Community profiles →",
                    icon="🤝",
                )

    st.markdown("---")
    st.caption("Data sourced from UCalgary Profiles · Hotchkiss Brain Institute")
