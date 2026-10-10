import pandas as pd
import streamlit as st

from ui.components import alert_card, metric_card


BRANCH_REPORTS = {
    "Pune Central Branch": {
        "active_loans": 268,
        "exposure": 1025000000,
        "low_risk_count": 152,
        "low_risk_share": 57,
        "medium_count": 83,
        "medium_share": 31,
        "high_count": 33,
        "high_share": 12,
        "alert_level": "Moderate",
        "alert_icon": "Alert",
        "severity": "warning",
        "crop_context": "Cotton and pomegranate blocks in the western plateau; illustrative heat stress and erratic rainfall pattern.",
        "action": "Review seasonal repayment buffers and schedule an irrigation and water-logging check for the three highest-risk clusters.",
        "weather_note": "Simulated example only - not a forecast, field observation, or validated weather source.",
        "monthly": [
            {"Month": "Jan", "Approvals": 38, "Climate Stress": 22},
            {"Month": "Feb", "Approvals": 42, "Climate Stress": 26},
            {"Month": "Mar", "Approvals": 39, "Climate Stress": 29},
            {"Month": "Apr", "Approvals": 46, "Climate Stress": 34},
            {"Month": "May", "Approvals": 52, "Climate Stress": 41},
            {"Month": "Jun", "Approvals": 49, "Climate Stress": 35},
        ],
    },
    "Nashik Main Branch": {
        "active_loans": 312,
        "exposure": 1468000000,
        "low_risk_count": 176,
        "low_risk_share": 56,
        "medium_count": 101,
        "medium_share": 32,
        "high_count": 35,
        "high_share": 11,
        "alert_level": "Elevated",
        "alert_icon": "Alert",
        "severity": "warning",
        "crop_context": "Grape and onion farms in the Nashik belt; illustrative rainfall shortfall and late-season humidity pressure.",
        "action": "Prioritize field verification for higher moisture-risk farms and confirm crop insurance documentation before renewal.",
        "weather_note": "Simulated example only - not a forecast, observation, or live climate alert.",
        "monthly": [
            {"Month": "Jan", "Approvals": 45, "Climate Stress": 24},
            {"Month": "Feb", "Approvals": 48, "Climate Stress": 27},
            {"Month": "Mar", "Approvals": 51, "Climate Stress": 31},
            {"Month": "Apr", "Approvals": 58, "Climate Stress": 36},
            {"Month": "May", "Approvals": 62, "Climate Stress": 39},
            {"Month": "Jun", "Approvals": 56, "Climate Stress": 42},
        ],
    },
    "Nagpur East Branch": {
        "active_loans": 244,
        "exposure": 872000000,
        "low_risk_count": 135,
        "low_risk_share": 55,
        "medium_count": 77,
        "medium_share": 32,
        "high_count": 32,
        "high_share": 13,
        "alert_level": "High",
        "alert_icon": "Alert",
        "severity": "error",
        "crop_context": "Soybean and wheat clusters in central Vidarbha; illustrative delayed monsoon onset and heat stress risk.",
        "action": "Escalate repayment review for the most exposed farms and arrange a field check for the current season's yield stress.",
        "weather_note": "Simulated example only - not a forecast, observation, or validated climate alert.",
        "monthly": [
            {"Month": "Jan", "Approvals": 37, "Climate Stress": 18},
            {"Month": "Feb", "Approvals": 41, "Climate Stress": 22},
            {"Month": "Mar", "Approvals": 45, "Climate Stress": 26},
            {"Month": "Apr", "Approvals": 49, "Climate Stress": 31},
            {"Month": "May", "Approvals": 53, "Climate Stress": 38},
            {"Month": "Jun", "Approvals": 50, "Climate Stress": 45},
        ],
    },
}


def format_rupees(value):
    return f"Rs {value / 10000000:,.2f} Cr"


def get_monthly_demo_frame(branch_name):
    monthly = pd.DataFrame(BRANCH_REPORTS[branch_name]["monthly"])
    monthly["MonthOrder"] = pd.Categorical(
        monthly["Month"],
        categories=["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
        ordered=True,
    )
    monthly = monthly.sort_values("MonthOrder").drop(columns="MonthOrder").reset_index(drop=True)
    return monthly


st.title("Branch Reports & Climate Alerts")
st.write("Branch-level risk exposure, portfolio climate risk distribution, and exportable compliance reports.")

c1, c2 = st.columns([1, 1])
with c1:
    branch = st.selectbox("Branch Context", list(BRANCH_REPORTS.keys()))
with c2:
    period_start, period_end = st.date_input(
        "Reporting Period",
        value=(pd.to_datetime("2026-04-01"), pd.to_datetime("2026-06-30")),
    )

selected_branch = BRANCH_REPORTS[branch]

st.warning("Illustrative demo data - not real branch exposure, verified loan history, or live weather.")
st.caption(
    f"Demo view for {branch} - {pd.Timestamp(period_start).strftime('%b %d, %Y')} to {pd.Timestamp(period_end).strftime('%b %d, %Y')} - sample values only."
)

st.markdown("### Branch Risk Portfolio Exposure")
summary_cols = st.columns(2)
with summary_cols[0]:
    metric_card(
        "Active loans",
        f"{selected_branch['active_loans']} loans",
        "Loans",
        "Illustrative portfolio size only",
    )
    metric_card(
        "Low risk",
        f"{selected_branch['low_risk_share']}% ({selected_branch['low_risk_count']})",
        "Low",
        "Sample bucket; not a trained default prediction",
    )
with summary_cols[1]:
    metric_card(
        "Demo exposure",
        format_rupees(selected_branch["exposure"]),
        "Value",
        "Illustrative rupee value only",
    )
    metric_card(
        "High indicator",
        f"{selected_branch['high_share']}% ({selected_branch['high_count']})",
        "Alert",
        "Sample bucket; not a trained default prediction",
    )

st.markdown("---")
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.markdown("### Portfolio Indicator Breakdown")
    indicator_df = pd.DataFrame(
        {
            "Band": ["Low", "Medium", "High"],
            "Count": [selected_branch["low_risk_count"], selected_branch["medium_count"], selected_branch["high_count"]],
            "Share": [selected_branch["low_risk_share"], selected_branch["medium_share"], selected_branch["high_share"]],
        }
    )
    st.bar_chart(indicator_df.set_index("Band")["Count"], height=220)
    st.dataframe(indicator_df, width="stretch", hide_index=True)
    st.caption("Indicator bands are sample buckets, not trained credit-default predictions.")

with chart_col2:
    st.markdown("### Monthly demo history")
    history_df = get_monthly_demo_frame(branch)
    st.caption(
        "Selected reporting dates are metadata only for this demo export; the monthly chart stays on the illustrative Jan-Jun demo history for readable comparison."
    )
    st.line_chart(history_df.set_index("Month")[["Approvals"]], height=180, x_label="Month", y_label="Approvals (loans)")
    st.caption("Approvals are illustrative loan counts in the demo branch history.")
    st.line_chart(history_df.set_index("Month")[["Climate Stress"]], height=180, x_label="Month", y_label="Climate stress (demo index)")
    st.caption("Climate stress reflects a sample climate index, not a live forecast or observation.")
    st.dataframe(
        history_df.rename(columns={"Month": "Month", "Approvals": "Approvals (loans)", "Climate Stress": "Climate stress (demo index)"}),
        width="stretch",
        hide_index=True,
    )
    st.caption("Illustrative demo history - not a live climate observation or verified approvals record.")

st.markdown("---")
st.markdown("### Branch Weather / Climate Panel")
st.caption("Every alert below is a simulated example - not a forecast, observation, or validated bank signal.")
alert_card(
    f"{selected_branch['alert_level']} climate alert",
    f"{selected_branch['crop_context']} {selected_branch['weather_note']}",
    severity=selected_branch["severity"],
    icon=selected_branch["alert_icon"],
)

weather_col1, weather_col2, weather_col3 = st.columns([1, 1.2, 1.8])
with weather_col1:
    st.markdown("**Alert level**")
    st.write(selected_branch["alert_level"])
with weather_col2:
    st.markdown("**Crop / context**")
    st.write(selected_branch["crop_context"])
with weather_col3:
    st.markdown("**Practical action**")
    st.write(selected_branch["action"])

st.markdown("---")
st.markdown("### Demo Export")
export_df = pd.DataFrame(
    [
        {
            "Branch": branch,
            "Reporting Period Start": pd.Timestamp(period_start).strftime("%Y-%m-%d"),
            "Reporting Period End": pd.Timestamp(period_end).strftime("%Y-%m-%d"),
            "Active Loans": selected_branch["active_loans"],
            "Total Demo Exposure": selected_branch["exposure"],
            "Low Risk Share %": selected_branch["low_risk_share"],
            "Low Risk Count": selected_branch["low_risk_count"],
            "High Indicator Share %": selected_branch["high_share"],
            "High Indicator Count": selected_branch["high_count"],
            "Alert Level": selected_branch["alert_level"],
        }
    ]
)
csv_data = export_df.to_csv(index=False)
file_name = f"{branch.lower().replace(' ', '_')}_demo_branch_report.csv"
st.download_button(
    label="Download illustrative demo branch report (.csv)",
    data=csv_data,
    file_name=file_name,
    mime="text/csv",
    width="stretch",
)
st.caption("Demo output only. Not a compliance-certified bank record or validated audit pack.")
