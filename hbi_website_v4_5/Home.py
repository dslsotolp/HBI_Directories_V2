"""HBI — Landing Page."""

import math

import pandas as pd
import pydeck as pdk
import streamlit as st
from utils.page_config import BLANK_PAGE_ICON

from utils.components import (
    inject_custom_css,
    render_public_sidebar_navigation,
    UCALGARY_RED,
    COMMUNITY_TEAL,
    render_disclaimer,
)
from utils.data_loader import load_members
from utils.linkedin_data_loader import load_community_map_data

st.set_page_config(
    page_title="HBI – Hotchkiss Brain Institute",
    page_icon=BLANK_PAGE_ICON,
    layout="wide",
    initial_sidebar_state="collapsed",
)

# st.page_link and st.switch_page require st.navigation() to be configured in
# Streamlit 1.36+. The home page is represented as a function stub so that
# selecting "Home" does not re-execute this file (which causes recursion).
_on_home = False


def _home_page_stub():
    global _on_home
    _on_home = True


_home_page = st.Page(_home_page_stub, title="Home", default=True)
_members_page = st.Page("pages/1_HBI_Members.py", title="Members")
_community_page = st.Page("pages/2_HBI_Community.py", title="Community")
_areas_of_research_page = st.Page(
    "pages/8_Areas_of_Expertise_2.py",
    title="Areas of Research",
    url_path="Areas_of_Research",
)
_publication_keywords_page = st.Page(
    "pages/7_Scopus_Keywords.py",
    title="Research Keywords from Publications",
    url_path="Research_Keywords_from_Publications",
    visibility="hidden",
)
_organizations_page = st.Page("pages/5_Organizations.py", title="Organizations")

_pg = st.navigation(
    [
        _home_page,
        _members_page,
        _community_page,
        _areas_of_research_page,
        _organizations_page,
        _publication_keywords_page,
        st.Page(
            "pages/1_Member_Profile.py",
            title="Member Profile",
            url_path="Member_Profile",
            visibility="hidden",
        ),
        st.Page(
            "pages/4_Community_Profile.py",
            title="Community Profile",
            url_path="Community_Profile",
            visibility="hidden",
        ),
        st.Page(
            "pages/6_Search_Results.py",
            title="Search Results",
            url_path="Search_Results",
            visibility="hidden",
        ),
        st.Page(
            "pages/9_Profile_Summary_Examples.py",
            title="Profile Summary Explorations",
            url_path="Profile_Summary_Examples",
            visibility="hidden",
        ),
    ],
    position="hidden",
)
_pg.run()

if not _on_home:
    st.stop()

inject_custom_css()
render_public_sidebar_navigation("home")

st.markdown(
    f"""
    <div class="hbi-banner">
        <h1>Hotchkiss Brain Institute</h1>
        <p>University of Calgary &nbsp;·&nbsp; Research Community Directory</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("<br>", unsafe_allow_html=True)

st.markdown(
    """
    Welcome to the **HBI Directory** — explore faculty members,
    community, research areas, and organizations across the Hotchkiss Brain Institute.
    """
)

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(
        '<a href="/HBI_Members" target="_self" class="hbi-nav-card">'
        '<span style="display:block;font-size:2.5rem;">🧠</span>'
        '<span style="display:block;font-size:1.2rem;font-weight:700;margin:12px 0 6px;">HBI Members</span>'
        '<span style="display:block;color:#666;font-size:0.9rem;">Browse the full directory of HBI faculty members and filter by membership type, department, or research area.</span>'
        '</a>',
        unsafe_allow_html=True,
    )

with c2:
    st.markdown(
        '<a href="/HBI_Community" target="_self" class="hbi-nav-card">'
        '<span style="display:block;font-size:2.5rem;">🤝</span>'
        '<span style="display:block;font-size:1.2rem;font-weight:700;margin:12px 0 6px;">HBI Community</span>'
        '<span style="display:block;color:#666;font-size:0.9rem;">Explore LinkedIn profiles from the broader HBI research community, including collaborators and alumni.</span>'
        '</a>',
        unsafe_allow_html=True,
    )

with c3:
    st.markdown(
        '<a href="/Areas_of_Research" target="_self" class="hbi-nav-card">'
        '<span style="display:block;font-size:2.5rem;">🔬</span>'
        '<span style="display:block;font-size:1.2rem;font-weight:700;margin:12px 0 6px;">Areas of Research</span>'
        '<span style="display:block;color:#666;font-size:0.9rem;">Explore research areas found in public research profiles and keywords identified from publications.</span>'
        '</a>',
        unsafe_allow_html=True,
    )

with c4:
    st.markdown(
        '<a href="/Organizations" target="_self" class="hbi-nav-card">'
        '<span style="display:block;font-size:2.5rem;">🏢</span>'
        '<span style="display:block;font-size:1.2rem;font-weight:700;margin:12px 0 6px;">Organizations</span>'
        '<span style="display:block;color:#666;font-size:0.9rem;">Explore the organizations and institutions connected to the HBI research community and their collaborative ties.</span>'
        '</a>',
        unsafe_allow_html=True,
    )

# ── Global search ─────────────────────────────────────────────────────────────
st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align:center; font-weight:700; font-size:1.56rem; margin-bottom:8px;'>Start Here:</p>",
    unsafe_allow_html=True,
)
st.markdown(
    """
    <style>
    div[data-testid='stForm'] div[data-testid='column']:last-child .stFormSubmitButton button {
        width: 100%;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

with st.form("home_search_form", clear_on_submit=False):
    _search_col, _btn_col = st.columns([5, 1])
    with _search_col:
        _query = st.text_input(
            label="search",
            label_visibility="collapsed",
                placeholder="Find a researcher, research area, organization, or keyword…",
            key="home_search_query",
        )
    with _btn_col:
        _search_clicked = st.form_submit_button("Search", use_container_width=True, type="primary")

if _search_clicked and _query and _query.strip():
    st.session_state["global_search_query"] = _query.strip()
    st.switch_page("pages/6_Search_Results.py")

# ── Community Map ─────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("---")
st.markdown("### 🌍 Where is our community?")

# University of Calgary — HBI home base
_UCALGARY_LAT = 51.0784
_UCALGARY_LON = -114.1348
_BASE_RADIUS  = 4_000    # metres per single profile
_MAX_RADIUS   = 30_000   # cap — keeps Calgary from filling Alberta when zoomed in

try:
    _community_df = load_community_map_data()
    _members_df   = load_members()
    _hbi_count    = int((_members_df["crawl_status"] == "success").sum())

    if not _community_df.empty:
        _total_community = int(_community_df["count"].sum())
        _cities          = int(_community_df["city"].nunique())
        _countries       = int(_community_df["country"].nunique())

        # Stats strip
        st.markdown(
            f'<p style="color:#666;font-size:0.95rem;margin-top:-6px;">'
            f'<span style="color:{UCALGARY_RED};font-weight:700;">{_hbi_count}</span> HBI members'
            f' &nbsp;·&nbsp; '
            f'<span style="color:{COMMUNITY_TEAL};font-weight:700;">{_total_community:,}</span> community profiles'
            f' &nbsp;·&nbsp; '
            f'<span style="color:{COMMUNITY_TEAL};font-weight:700;">{_cities}</span> cities'
            f' &nbsp;·&nbsp; '
            f'<span style="color:{COMMUNITY_TEAL};font-weight:700;">{_countries}</span> countries/regions'
            f'</p>',
            unsafe_allow_html=True,
        )

        # Sqrt-scale bubble radius
        _community_df = _community_df.copy()
        _community_df["radius"] = _community_df["count"].apply(
            lambda c: min(_MAX_RADIUS, _BASE_RADIUS * math.sqrt(c))
        )

        # Arc data: one row per community city, source = UCalgary
        _arc_df = _community_df.copy()
        _arc_df["src_lat"]   = _UCALGARY_LAT
        _arc_df["src_lon"]   = _UCALGARY_LON
        _arc_df["arc_width"] = _arc_df["count"].apply(
            lambda c: max(1, min(6, int(math.sqrt(c))))
        )

        # UCalgary hub bubble (HBI members)
        _hub_df = pd.DataFrame([{
            "lat":     _UCALGARY_LAT,
            "lon":     _UCALGARY_LON,
            "count":   _hbi_count,
            "city":    "University of Calgary",
            "country": "Canada — HBI Members",
            "radius":  min(_MAX_RADIUS, _BASE_RADIUS * math.sqrt(_hbi_count)),
        }])

        # Layer 1 — arc connections (UCalgary → community cities)
        _arc_layer = pdk.Layer(
            "ArcLayer",
            id="arc_layer",
            data=_arc_df,
            get_source_position=["src_lon", "src_lat"],
            get_target_position=["lon", "lat"],
            get_width="arc_width",
            get_source_color=[207, 7, 34, 140],    # UCALGARY_RED
            get_target_color=[51, 113, 109, 200],  # Dark green COMMUNITY_TEAL
            pickable=True,
            auto_highlight=True,
        )

        # Layer 2 — community city bubbles (teal)
        _scatter_community = pdk.Layer(
            "ScatterplotLayer",
            id="community_layer",
            data=_community_df,
            get_position=["lon", "lat"],
            get_radius="radius",
            get_fill_color=[51, 113, 109, 185],
            get_line_color=[36, 90, 85, 235],
            radius_min_pixels=5,
            radius_max_pixels=50,
            line_width_min_pixels=1,
            pickable=True,
        )

        # Layer 3 — UCalgary hub bubble (red)
        _scatter_hbi = pdk.Layer(
            "ScatterplotLayer",
            id="hbi_layer",
            data=_hub_df,
            get_position=["lon", "lat"],
            get_radius="radius",
            get_fill_color=[207, 7, 34, 200],
            get_line_color=[207, 7, 34, 255],
            radius_min_pixels=7,
            radius_max_pixels=60,
            line_width_min_pixels=2,
            pickable=True,
        )

        _view = pdk.ViewState(
            latitude=48.0,
            longitude=-85.0,
            zoom=2.5,
            pitch=30,
        )

        _tooltip = {
            "html": "<b>{city}</b><br/>{country}<br/>{count} profile(s)",
            "style": {
                "backgroundColor": "#1A1A2E",
                "color": "white",
                "fontSize": "13px",
                "padding": "8px 12px",
                "borderRadius": "6px",
            },
        }

        _map_event = st.pydeck_chart(
            pdk.Deck(
                layers=[_arc_layer, _scatter_community, _scatter_hbi],
                initial_view_state=_view,
                tooltip=_tooltip,
                map_style="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json",
            ),
            on_select="rerun",
            selection_mode="single-object",
            key="community_map",
            use_container_width=True,
            height=500,
        )

        # Handle bubble clicks — navigate to the relevant profiles page
        try:
            _sel = _map_event.selection.objects
            if _sel.get("community_layer"):
                _clicked_city = _sel["community_layer"][0].get("city", "")
                if _clicked_city:
                    st.session_state["community_city_filter"] = _clicked_city
                    st.switch_page("pages/2_HBI_Community.py")
            elif _sel.get("hbi_layer"):
                st.switch_page("pages/1_HBI_Members.py")
        except AttributeError:
            pass  # no selection yet

        # Legend
        st.markdown(
            f'<div style="display:flex;gap:24px;margin-top:6px;font-size:0.85rem;color:#555;">'
            f'<span>'
            f'<span style="display:inline-block;width:12px;height:12px;border-radius:50%;'
            f'background:{UCALGARY_RED};margin-right:5px;vertical-align:middle;"></span>'
            f'HBI Members (University of Calgary)'
            f'</span>'
            f'<span>'
            f'<span style="display:inline-block;width:12px;height:12px;border-radius:50%;'
            f'background:{COMMUNITY_TEAL};margin-right:5px;vertical-align:middle;"></span>'
            f'Community Profiles'
            f'</span>'
            f'<span style="color:#aaa;">Lines connect from the HBI hub to each community location</span>'
            f'</div>',
            unsafe_allow_html=True,
        )
        st.caption("Based on LinkedIn profile location data · Bubble size = number of profiles · Hover for details")
    else:
        st.info("No location data available.")
except Exception as _map_err:
    st.caption(f"Map unavailable: {_map_err}")

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("---")
render_disclaimer()
