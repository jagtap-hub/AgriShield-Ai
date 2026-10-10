import html

import streamlit as st

from ui.style import apply_theme

st.set_page_config(page_title="Farmer Schemes", page_icon="🌾", layout="wide")
apply_theme()


SCHEMES = [
    {
        "name": "PM-KISAN",
        "category": "Household income support",
        "summary": (
            "A central income-support programme that sends assistance to eligible "
            "farmer families through direct benefit transfer."
        ),
        "check": (
            "Eligibility exclusions and identity or land-record checks apply. "
            "Use the portal’s status service to check an individual case."
        ),
        "url": "https://pmkisan.gov.in/",
        "search_terms": "income support dbt farmer family status",
    },
    {
        "name": "Pradhan Mantri Fasal Bima Yojana (PMFBY)",
        "category": "Crop insurance & risk protection",
        "summary": (
            "Crop insurance for notified crops and areas, with protection defined "
            "by the scheme guidelines and the season’s local notification."
        ),
        "check": (
            "Enrolment windows, notified crops, risks, and claim steps vary by "
            "season and location. Check the current notification before acting."
        ),
        "url": "https://pmfby.gov.in/",
        "search_terms": "insurance crop damage premium enrolment season claim",
    },
    {
        "name": "Kisan Credit Card (KCC)",
        "category": "Seasonal farm credit",
        "summary": (
            "A bank credit facility intended to help eligible farmers meet "
            "cultivation and related agricultural needs."
        ),
        "check": (
            "A participating lender assesses applications and sets applicable "
            "limits and terms under current rules; approval is not guaranteed."
        ),
        "url": "https://www.myscheme.gov.in/schemes/kcc",
        "search_terms": "loan credit bank cultivation working capital",
    },
    {
        "name": "Pradhan Mantri Krishi Sinchayee Yojana (PMKSY) — Per Drop More Crop",
        "category": "Water-efficient irrigation",
        "summary": (
            "Promotes more efficient use of water on farms, including micro-irrigation "
            "methods such as drip and sprinkler systems under Per Drop More Crop."
        ),
        "check": (
            "Assistance, eligible equipment, application windows, and delivery are "
            "administered under current programme guidance and may vary by state. "
            "Ask the state agriculture or horticulture department what is open."
        ),
        "url": "https://pmksy.gov.in/",
        "search_terms": "PMKSY Per Drop More Crop drip sprinkler micro irrigation water efficiency",
    },
    {
        "name": "Soil Health Card",
        "category": "Soil health & nutrients",
        "summary": (
            "A soil-testing programme that provides information about soil "
            "nutrients and recommendations to guide balanced fertiliser use."
        ),
        "check": (
            "Testing and card services are coordinated through local authorities "
            "and laboratories; check where and when sampling is available."
        ),
        "url": "https://soilhealth.dac.gov.in/",
        "search_terms": "soil test nutrients fertiliser fertilizer laboratory",
    },
    {
        "name": "National Agriculture Market (e-NAM)",
        "category": "Market access",
        "summary": (
            "An online trading platform that connects participating agricultural "
            "markets and helps farmers access a wider pool of buyers."
        ),
        "check": (
            "Participation depends on mandi onboarding, registration, and "
            "commodity rules. The platform does not guarantee a particular price."
        ),
        "url": "https://enam.gov.in/web/",
        "search_terms": "market mandi buyers trade sell produce",
    },
]

CATEGORIES = ["All categories"] + sorted({scheme["category"] for scheme in SCHEMES})


def filter_schemes(query: str, category: str) -> list[dict[str, str]]:
    """Return schemes matching the search text and selected category."""
    query_terms = query.casefold().split()
    return [
        scheme
        for scheme in SCHEMES
        if (category == "All categories" or scheme["category"] == category)
        and (
            not query_terms
            or all(
                term
                in " ".join(
                    (
                        scheme["name"],
                        scheme["category"],
                        scheme["summary"],
                        scheme["check"],
                        scheme["search_terms"],
                    )
                ).casefold()
                for term in query_terms
            )
        )
    ]


st.markdown(
    """
    <div class="scheme-hero">
      <div class="scheme-eyebrow">Farmer scheme directory · National programmes</div>
      <h1>Find support for your farm</h1>
      <p>A practical directory to help you explore income support, crop protection,
         farm credit, water-wise irrigation, soil health and markets. Start with what
         you need, then verify today’s details with the official scheme source.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.warning(
    "**Important:** This is an information guide, not an eligibility checker or "
    "application service. Scheme rules, deadlines, benefits, and availability can "
    "change. Your sample farmer profile does not contain state or district, so this "
    "page does not infer local eligibility or recommend a scheme based on location. "
    "Always confirm current details with the official portal or local department."
)

search_col, category_col = st.columns([1.6, 1])
with search_col:
    search_query = st.text_input(
        "Search schemes",
        placeholder="Try “insurance”, “drip irrigation”, or “credit”",
        key="farmer_scheme_search",
    )
with category_col:
    selected_category = st.selectbox(
        "Filter by category",
        CATEGORIES,
        key="farmer_scheme_category",
    )

filtered_schemes = filter_schemes(search_query, selected_category)
st.caption(
    f"Showing {len(filtered_schemes)} of {len(SCHEMES)} programmes · "
    "Descriptions are summaries; the official scheme rules take precedence."
)

if not filtered_schemes:
    st.info(
        "No schemes match that search. Try a broader term or choose “All categories”."
    )
else:
    for row_start in range(0, len(filtered_schemes), 2):
        columns = st.columns(2)
        for column, scheme in zip(
            columns, filtered_schemes[row_start : row_start + 2]
        ):
            with column:
                name = html.escape(scheme["name"])
                category = html.escape(scheme["category"])
                summary = html.escape(scheme["summary"])
                check = html.escape(scheme["check"])
                url = html.escape(scheme["url"], quote=True)
                st.markdown(
                    f"""
                    <article class="scheme-card">
                      <div class="scheme-card-top">
                        <span class="scheme-mark" aria-hidden="true">✳</span>
                        <span class="scheme-category">{category}</span>
                      </div>
                      <h2>{name}</h2>
                      <p>{summary}</p>
                      <div class="scheme-check">
                        <strong>Before you apply</strong>
                        <span>{check}</span>
                      </div>
                      <a class="scheme-link" href="{url}" target="_blank"
                         rel="noopener noreferrer">
                        Visit official scheme portal <span aria-hidden="true">↗</span>
                      </a>
                    </article>
                    """,
                    unsafe_allow_html=True,
                )

st.markdown(
    """
    <style>
      .scheme-hero {
        position: relative;
        overflow: hidden;
        padding: 2rem 2.2rem;
        margin: .25rem 0 1.1rem;
        border-radius: 22px;
        color: #f5f8ec;
        background:
          radial-gradient(ellipse at 86% 18%, rgba(184,243,107,.24), transparent 30%),
          linear-gradient(112deg, #092b20 0%, #104c3a 64%, #1a6247 100%);
        box-shadow: 0 12px 34px rgba(9,43,32,.13);
      }
      .scheme-hero:after {
        content: "✳";
        position: absolute;
        right: 4%;
        top: -54px;
        color: rgba(232,247,238,.09);
        font-size: 210px;
        line-height: 1;
      }
      .scheme-hero .scheme-eyebrow {
        color: #c5ed91;
        font-size: .76rem;
        font-weight: 750;
        letter-spacing: .13em;
        text-transform: uppercase;
      }
      .scheme-hero h1 {
        position: relative;
        z-index: 1;
        margin: .55rem 0 .4rem;
        color: #fff !important;
        font-size: clamp(2rem, 4vw, 3.2rem);
        letter-spacing: -.045em;
        line-height: 1.08;
      }
      .scheme-hero p {
        position: relative;
        z-index: 1;
        max-width: 690px;
        margin: 0;
        color: #e2f0e4 !important;
        font-size: 1rem;
        line-height: 1.65;
      }
      .scheme-card {
        display: flex;
        min-height: 350px;
        flex-direction: column;
        margin: 0 0 1rem;
        padding: 1.35rem 1.45rem 1.25rem;
        border: 1px solid rgba(16,76,58,.13);
        border-radius: 18px;
        background: linear-gradient(155deg, #fff 0%, #fbfcf8 100%);
        box-shadow: 0 6px 20px rgba(9,43,32,.055);
        transition: transform .18s ease, box-shadow .18s ease;
      }
      .scheme-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 28px rgba(9,43,32,.11);
      }
      .scheme-card-top {
        display: flex;
        align-items: center;
        gap: .7rem;
      }
      .scheme-mark {
        display: inline-grid;
        width: 2rem;
        height: 2rem;
        place-items: center;
        border-radius: 10px;
        color: #092b20;
        background: #dff3c8;
        font-size: 1.05rem;
      }
      .scheme-category {
        color: #45675a;
        font-size: .77rem;
        font-weight: 750;
        letter-spacing: .06em;
        text-transform: uppercase;
      }
      .scheme-card h2 {
        margin: .95rem 0 .45rem;
        color: #092b20 !important;
        font-size: 1.35rem;
        letter-spacing: -.025em;
        line-height: 1.25;
      }
      .scheme-card p {
        margin: 0 0 1rem;
        color: #304a3d !important;
        font-size: .96rem;
        line-height: 1.58;
      }
      .scheme-check {
        display: grid;
        gap: .25rem;
        margin-top: auto;
        padding: .8rem .9rem;
        border-left: 3px solid #d2a94a;
        border-radius: 0 10px 10px 0;
        background: #fbf7eb;
        color: #57471f;
        font-size: .84rem;
        line-height: 1.5;
      }
      .scheme-check strong {
        color: #5c4817;
      }
      .scheme-link {
        display: inline-flex;
        align-items: center;
        gap: .35rem;
        align-self: flex-start;
        margin-top: 1rem;
        color: #0d6243 !important;
        font-size: .9rem;
        font-weight: 750;
        text-decoration: none !important;
      }
      .scheme-link:hover {
        color: #092b20 !important;
        text-decoration: underline !important;
        text-underline-offset: 3px;
      }
      @media (max-width: 640px) {
        .scheme-hero { padding: 1.5rem; }
        .scheme-card { min-height: 0; }
      }
      @media (min-width: 641px) and (max-width: 900px) {
        .scheme-card { min-height: 380px; }
      }
    </style>
    """,
    unsafe_allow_html=True,
)
