import streamlit as st
import pandas as pd
from datetime import datetime
import json
import os
import xml.etree.ElementTree as ET
from fpdf import FPDF
import io
import base64

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
        unique_cases = set()
        for item in database:
            unique_cases.update(item[field])
        return sorted(list(unique_cases))

def export_to_pdf(results):
    """Convert results to PDF format"""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Add title
    pdf.cell(200, 10, txt="PCB Research Results", ln=True, align='C')
    
    for pcb in results:
        # Add each PCB entry
        pdf.cell(200, 10, txt=f"{pcb['make']} - {pcb['model_number']}", ln=True)
        pdf.cell(200, 10, txt=f"Form Factor: {pcb['form_factor']}", ln=True)
        pdf.cell(200, 10, txt=f"Use Cases: {', '.join(pcb['use_cases'])}", ln=True)
        pdf.cell(200, 10, txt=f"Purpose: {pcb['purpose']}", ln=True)
        pdf.cell(200, 10, txt=f"Market Use: {pcb['market_use']}", ln=True)
        pdf.cell(200, 10, txt=f"Age in Market: {pcb['age_in_market']} years", ln=True)
        pdf.cell(200, 10, txt=f"Competing Products: {pcb['competing_products']}", ln=True)
        pdf.cell(200, 10, txt="", ln=True)  # Add spacing between entries
    
    return pdf.output(dest='S').encode('latin-1')

def export_to_xml(results):
    """Convert results to XML format"""
    root = ET.Element("PCBDatabase")
    
    for pcb in results:
        pcb_elem = ET.SubElement(root, "PCB")
        for key, value in pcb.items():
            if key == "use_cases":
                use_cases = ET.SubElement(pcb_elem, "use_cases")
                for case in value:
                    case_elem = ET.SubElement(use_cases, "case")
                    case_elem.text = case
            else:
                elem = ET.SubElement(pcb_elem, key)
                elem.text = str(value)
    
    return ET.tostring(root, encoding='unicode', method='xml')

def get_download_link(data, filename, text):
    """Generate a download link for the data"""
    b64 = base64.b64encode(data.encode()).decode()
    href = f'<a href="data:file/txt;base64,{b64}" download="{filename}">{text}</a>'
    return href

def get_binary_download_link(data, filename, text):
    """Generate a download link for binary data"""
    b64 = base64.b64encode(data).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="{filename}">{text}</a>'
    return href

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
        # [Previous Add New PCB code remains the same]
        pass

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
                
                # Display results
                for pcb in results:
                    with st.expander(f"{pcb['make']} - {pcb['model_number']}"):
                        st.write(f"**Form Factor:** {pcb['form_factor']}")
                        st.write(f"**Use Cases:** {', '.join(pcb['use_cases'])}")
                        st.write(f"**Purpose:** {pcb['purpose']}")
                        st.write(f"**Market Use:** {pcb['market_use']}")
                        st.write(f"**Age in Market:** {pcb['age_in_market']} years")
                        st.write(f"**Competing Products:** {pcb['competing_products']}")
                
                # Export options
                st.subheader("Export Results")
                col1, col2, col3, col4 = st.columns(4)
                
                # CSV export
                with col1:
                    df = pd.DataFrame(results)
                    csv = df.to_csv(index=False)
                    st.markdown(get_download_link(csv, "pcb_results.csv", "Download CSV"), unsafe_allow_html=True)
                
                # PDF export
                with col2:
                    pdf_data = export_to_pdf(results)
                    st.markdown(get_binary_download_link(pdf_data, "pcb_results.pdf", "Download PDF"), unsafe_allow_html=True)
                
                # XML export
                with col3:
                    xml_data = export_to_xml(results)
                    st.markdown(get_download_link(xml_data, "pcb_results.xml", "Download XML"), unsafe_allow_html=True)
                
                # JSON export
                with col4:
                    json_data = json.dumps(results, indent=4)
                    st.markdown(get_download_link(json_data, "pcb_results.json", "Download JSON"), unsafe_allow_html=True)
            else:
                st.warning("No results found.")

    elif page == "Market Analysis":
        # [Previous Market Analysis code remains the same]
        pass

if __name__ == "__main__":
    main()
