from typing import Any

import streamlit as st

from services.db_service import fetch_dataset_farmers


def select_dataset_farmer(key: str) -> dict[str, Any]:
    """Render a farmer selector backed by the local CSV dataset."""
    farmers = fetch_dataset_farmers()
    if not farmers:
        st.error("The farmer dataset contains no profiles.")
        st.stop()

    farmer_by_id = {farmer["farmer_id"]: farmer for farmer in farmers}
    farmer_ids = list(farmer_by_id)
    previous_id = st.session_state.get("selected_farmer_id")
    default_index = farmer_ids.index(previous_id) if previous_id in farmer_by_id else 0
    selected_id = st.selectbox(
        "Select farmer profile from dataset",
        options=farmer_ids,
        index=default_index,
        format_func=lambda farmer_id: (
            f"{farmer_id} — {farmer_by_id[farmer_id]['farmer_name']}"
        ),
        key=key,
    )
    st.session_state["selected_farmer_id"] = selected_id
    st.caption(
        f"Source: crop_data.csv · {len(farmers)} profiles. "
        "Bundled records are generated sample data, not verified live farmer records."
    )
    return farmer_by_id[selected_id]
