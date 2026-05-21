"""NetSuite Script Formatter — Streamlit edition.

A web-based tool that wraps a raw NetSuite Saved Search search.create
snippet into a properly formatted require(['N/search'], ...) deployment script.
"""

import streamlit as st

st.set_page_config(
    page_title="NetSuite Script Formatter",
    layout="centered",
)

st.title("NetSuite Script Formatter")
st.markdown(
    "Paste your NetSuite Saved Search creation code, add metadata, "
    "and generate a formatted deployment script."
)


def format_script(script: str, name: str, id_suffix: str, description: str) -> str:
    """Build the formatted SuiteScript from user inputs."""
    search_id = "customsearch" + id_suffix

    # Format description as block comments
    formatted_desc = "        // Description:\n"
    for line in description.strip().split("\n"):
        formatted_desc += f"        // {line}\n"

    # Locate the search variable declaration
    start_idx = script.find("var ")
    end_idx = script.find(" = search.create")
    if start_idx == -1 or end_idx == -1:
        raise ValueError("Could not find a 'var ... = search.create(...)' statement in the pasted script.")

    search_var = script[start_idx + 4 : end_idx].strip()

    # Extract the search.create(...) section, cutting off .run().each / searchResultCount noise
    # Find the closing paren of search.create(...) by counting balanced parens
    create_start = script.find("search.create(", start_idx)
    if create_start == -1:
        raise ValueError("Could not find 'search.create(' in the pasted script.")
    paren_depth = 0
    i = create_start + len("search.create(")
    while i < len(script):
        if script[i] == "(":
            paren_depth += 1
        elif script[i] == ")":
            if paren_depth == 0:
                create_end = i + 1
                break
            paren_depth -= 1
        i += 1
    else:
        raise ValueError("Unmatched parentheses in search.create(...) call.")
    search_create_code = script[start_idx:create_end].strip()


    # Assemble final script
    parts = [
        "require(['N/search'], function(search) {",
        "    try {",
        formatted_desc,
        "        " + search_create_code,
        f'        {search_var}.id="{search_id}";',
        f'        {search_var}.title="{name}";',
        f"        var newSearchId = {search_var}.save();",
        "",
        "        console.log('Search recreated successfully');",
        "",
        "    } catch (e) {",
        "        console.error(e.message);",
        "    }",
        "})",
    ]
    return "\n".join(parts)


# ── Input form ──────────────────────────────────────────────────────────────

script = st.text_area(
    "Paste NetSuite Saved Search Script",
    height=280,
    placeholder="var mySearch = search.create({ ... });",
    help="Paste the full script including the 'var ... = search.create(...)' statement.",
    key="script_input",
)

col1, col2 = st.columns(2)

with col1:
    name = st.text_input(
        "Search Name",
        placeholder="e.g. Open Sales Orders",
        help="A human-readable name for the saved search.",
        key="name_input",
    )
    description = st.text_area(
        "Description",
        height=100,
        placeholder="Brief notes about this saved search…",
        help="Notes that will be rendered as comments in the output script.",
        key="description_input",
    )

with col2:
    id_col1, id_col2 = st.columns([2, 3])
    with id_col1:
        st.text_input(
            "Search ID Prefix",
            value="customsearch",
            disabled=True,
            help="The 'customsearch' prefix is prepended automatically.",
        )
    with id_col2:
        id_suffix = st.text_input(
            "Search ID Suffix",
            placeholder="e.g. _sales_order",
            help="The part after 'customsearch'. For example 'customsearch_sales_order' → suffix '_sales_order'.",
            key="id_suffix_input",
        )

# ── Action buttons ──────────────────────────────────────────────────────────

col_a, col_b = st.columns([1, 5])
preview_clicked = col_a.button("Preview", type="secondary", use_container_width=True)
clear_clicked = col_b.button("Clear", use_container_width=True)

if clear_clicked:
    for key in ("script_input", "name_input", "id_suffix_input", "description_input",
                 "script_preview", "formatted_script"):
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()

if preview_clicked or st.session_state.get("script_preview"):
    errors = []
    if not script:
        errors.append("Script is required.")
    if not name:
        errors.append("Search Name is required.")
    if not id_suffix:
        errors.append("Search ID Suffix is required.")
    if not description:
        errors.append("Description is required.")

    if errors:
        for err in errors:
            st.error(err)
    else:
        try:
            formatted = format_script(script, name, id_suffix, description)
            st.session_state.formatted_script = formatted
            st.session_state.script_preview = True

            st.subheader("Preview")
            st.code(formatted, language="javascript")

            st.download_button(
                label="Download .js File",
                data=formatted,
                file_name=name.replace(" ", "_") + ".js",
                mime="text/javascript",
                type="primary",
            )
        except ValueError as e:
            st.error(str(e))
        except Exception as e:
            st.error(f"Unexpected error: {e}")
