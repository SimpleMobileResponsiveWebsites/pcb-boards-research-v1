import streamlit as st
import pandas as pd
from datetime import datetime
import json
import os

def load_database():
    """Load existing PCB database if it exists, otherwise create new one"""
    if os.path.exists('pcb_database.json'):
        with open('pcb_database.json', 'r') as f:
            return json.load(f)
    return []

def save_database(data):
    """Save PCB database to JSON file"""
    with open('pcb_database.json', 'w') as f:
        json.dump(data, f, indent=4)

def get_unique_values(database, field):
    """Get unique values for a given field from the database"""
    if field != "use_cases":
        return sorted(list(set(item[field] for item in database)))
    else:
        # For use_cases, we need to flatten the list of lists
        unique_cases = set()
        for item in database:
            unique_cases.update(item[field])
        return sorted(list(unique_cases))

def main():
    st.title("PCB Research Tool")
    
    # Sidebar for navigation
    page = st.sidebar.selectbox(
        "Choose a function",
        ["Add New PCB", "Search PCB", "Market Analysis"]
    )
    
    # Initialize or load database
    if 'pcb_database' not in st.session_state:
        st.session_state.pcb_database = load_database()
    
    if page == "Add New PCB":
        st.header("Add New PCB Entry")
        
        # Input form
        with st.form("pcb_entry_form"):
            form_factor = st.text_input("Form Factor")
            model_number = st.text_input("Model Number")
            make = st.text_input("Make/Manufacturer")
            model = st.text_input("Model Name")
            
            # Use cases (multiple selection)
            use_cases = st.multiselect(
                "Use Cases",
                ["Industrial", "Consumer Electronics", "Automotive", "Medical", "Aerospace", "IoT", "Other"],
                default=[]
            )
            
            purpose = st.text_area("Purpose/Description")
            market_use = st.text_area("Intended Market Use")
            
            # Market age slider
            age_in_market = st.slider(
                "Age in Market (Years)",
                min_value=0,
                max_value=20,
                value=1
            )
            
            competing_products = st.text_area("Competing Products/Functions")
            
            submitted = st.form_submit_button("Submit PCB Entry")
            
            if submitted:
                new_entry = {
                    "form_factor": form_factor,
                    "model_number": model_number,
                    "make": make,
                    "model": model,
                    "use_cases": use_cases,
                    "purpose": purpose,
                    "market_use": market_use,
                    "age_in_market": age_in_market,
                    "competing_products": competing_products,
                    "entry_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                
                st.session_state.pcb_database.append(new_entry)
                save_database(st.session_state.pcb_database)
                st.success("PCB entry added successfully!")

    elif page == "Search PCB":
        st.header("Search PCB Database")

        if not st.session_state.pcb_database:
            st.info("No PCB entries available. Please add some entries first.")
            return

        # Search filters
        search_type = st.selectbox(
            "Search by",
            ["Model Number", "Make", "Form Factor", "Use Cases"]
        )

        # Get appropriate options based on search type
        if search_type == "Use Cases":
            search_terms = st.multiselect(
                "Select Use Cases",
                get_unique_values(st.session_state.pcb_database, "use_cases"),
                default=None
            )
        else:
            field_map = {
                "Model Number": "model_number",
                "Make": "make",
                "Form Factor": "form_factor"
            }
            search_terms = st.multiselect(
                f"Select {search_type}",
                get_unique_values(st.session_state.pcb_database, field_map[search_type]),
                default=None
            )

        if search_terms:
            results = []
            for pcb in st.session_state.pcb_database:
                if search_type == "Use Cases":
                    if any(term in pcb["use_cases"] for term in search_terms):
                        results.append(pcb)
                else:
                    field = field_map[search_type]
                    if pcb[field] in search_terms:
                        results.append(pcb)

            if results:
                st.write(f"Found {len(results)} results:")
                for pcb in results:
                    with st.expander(f"{pcb['make']} - {pcb['model_number']}"):
                        st.write(f"**Form Factor:** {pcb['form_factor']}")
                        st.write(f"**Use Cases:** {', '.join(pcb['use_cases'])}")
                        st.write(f"**Purpose:** {pcb['purpose']}")
                        st.write(f"**Market Use:** {pcb['market_use']}")
                        st.write(f"**Age in Market:** {pcb['age_in_market']} years")
                        st.write(f"**Competing Products:** {pcb['competing_products']}")
            else:
                st.warning("No results found.")

    elif page == "Market Analysis":
        st.header("Market Analysis")
        
        if st.session_state.pcb_database:
            # Convert database to DataFrame for analysis
            df = pd.DataFrame(st.session_state.pcb_database)
            
            # Use cases distribution
            st.subheader("Use Cases Distribution")
            use_cases_flat = [item for sublist in df['use_cases'] for item in sublist]
            use_cases_dist = pd.Series(use_cases_flat).value_counts()
            st.bar_chart(use_cases_dist)
            
            # Age distribution
            st.subheader("Age Distribution in Market")
            age_dist = df['age_in_market'].value_counts().sort_index()
            st.bar_chart(age_dist)
            
            # Manufacturer distribution
            st.subheader("Manufacturer Distribution")
            make_dist = df['make'].value_counts()
            st.bar_chart(make_dist)
            
            # Form factor distribution
            st.subheader("Form Factor Distribution")
            form_factor_dist = df['form_factor'].value_counts()
            st.bar_chart(form_factor_dist)
        else:
            st.info("No data available for analysis. Please add some PCB entries first.")

if __name__ == "__main__":
    main()
