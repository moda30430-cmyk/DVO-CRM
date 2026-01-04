"""
DVO-CRM: Production-Ready Streamlit Application
A customer relationship management system with robust error handling and data validation.

Author: moda30430-cmyk
Date: 2026-01-04
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from typing import Optional, Dict, List, Any
import json
from pathlib import Path

# ============================================================================
# Configuration and Logging Setup
# ============================================================================

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Streamlit page configuration
st.set_page_config(
    page_title="DVO-CRM",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://github.com",
        "Report a bug": "https://github.com/issues",
        "About": "DVO-CRM v1.0 - Production Ready"
    }
)

# ============================================================================
# Constants
# ============================================================================

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

CUSTOMERS_FILE = DATA_DIR / "customers.csv"
INTERACTIONS_FILE = DATA_DIR / "interactions.csv"

CUSTOMER_FIELDS = ["id", "name", "email", "phone", "company", "status", "created_date", "last_contact"]
INTERACTION_TYPES = ["Call", "Email", "Meeting", "Note", "Support Ticket"]
CUSTOMER_STATUS = ["Active", "Inactive", "Prospect", "Lead", "Churned"]

# ============================================================================
# Utility Functions
# ============================================================================

@st.cache_resource
def initialize_session_state():
    """Initialize session state variables safely."""
    if "customers_data" not in st.session_state:
        st.session_state.customers_data = None
    if "interactions_data" not in st.session_state:
        st.session_state.interactions_data = None
    if "refresh_flag" not in st.session_state:
        st.session_state.refresh_flag = False


def validate_email(email: str) -> bool:
    """
    Validate email format.
    
    Args:
        email: Email address to validate
        
    Returns:
        bool: True if email is valid, False otherwise
    """
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_phone(phone: str) -> bool:
    """
    Validate phone number format.
    
    Args:
        phone: Phone number to validate
        
    Returns:
        bool: True if phone is valid, False otherwise
    """
    import re
    # Accept various phone formats
    pattern = r'^[\d\s\-\+\(\)]{10,}$'
    return re.match(pattern, phone.replace(" ", "")) is not None


def sanitize_string(value: str, max_length: int = 255) -> str:
    """
    Sanitize string input.
    
    Args:
        value: String to sanitize
        max_length: Maximum allowed length
        
    Returns:
        str: Sanitized string
    """
    if not isinstance(value, str):
        return ""
    return value.strip()[:max_length]


def load_data(file_path: Path, expected_columns: Optional[List[str]] = None) -> Optional[pd.DataFrame]:
    """
    Load CSV data with error handling.
    
    Args:
        file_path: Path to CSV file
        expected_columns: Expected column names for validation
        
    Returns:
        pd.DataFrame or None: Loaded data or None if error occurs
    """
    try:
        if not file_path.exists():
            logger.info(f"File {file_path} does not exist. Creating empty dataframe.")
            return pd.DataFrame(columns=expected_columns or [])
        
        df = pd.read_csv(file_path)
        
        # Validate columns if expected
        if expected_columns:
            missing_cols = set(expected_columns) - set(df.columns)
            if missing_cols:
                logger.warning(f"Missing columns: {missing_cols}")
                return None
        
        logger.info(f"Successfully loaded {len(df)} rows from {file_path}")
        return df
        
    except pd.errors.EmptyDataError:
        logger.warning(f"File {file_path} is empty")
        return pd.DataFrame(columns=expected_columns or [])
    except Exception as e:
        logger.error(f"Error loading data from {file_path}: {str(e)}")
        return None


def save_data(df: pd.DataFrame, file_path: Path) -> bool:
    """
    Save dataframe to CSV with error handling.
    
    Args:
        df: DataFrame to save
        file_path: Path where to save
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        df.to_csv(file_path, index=False)
        logger.info(f"Successfully saved data to {file_path}")
        return True
    except Exception as e:
        logger.error(f"Error saving data to {file_path}: {str(e)}")
        return False


def generate_customer_id() -> str:
    """Generate a unique customer ID."""
    return f"CUST-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"


# ============================================================================
# Data Management Functions
# ============================================================================

def get_customers_data() -> pd.DataFrame:
    """Load or initialize customers data."""
    if st.session_state.customers_data is None or st.session_state.refresh_flag:
        data = load_data(CUSTOMERS_FILE, CUSTOMER_FIELDS)
        if data is None or data.empty:
            data = pd.DataFrame(columns=CUSTOMER_FIELDS)
        st.session_state.customers_data = data
        st.session_state.refresh_flag = False
    return st.session_state.customers_data


def get_interactions_data() -> pd.DataFrame:
    """Load or initialize interactions data."""
    if st.session_state.interactions_data is None or st.session_state.refresh_flag:
        columns = ["id", "customer_id", "type", "notes", "date", "duration_minutes"]
        data = load_data(INTERACTIONS_FILE, columns)
        if data is None or data.empty:
            data = pd.DataFrame(columns=columns)
        st.session_state.interactions_data = data
        st.session_state.refresh_flag = False
    return st.session_state.interactions_data


def add_customer(name: str, email: str, phone: str, company: str, status: str) -> bool:
    """
    Add a new customer with validation.
    
    Args:
        name: Customer name
        email: Customer email
        phone: Customer phone
        company: Company name
        status: Customer status
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Validate inputs
        if not name or len(name.strip()) < 2:
            st.error("Name must be at least 2 characters long")
            return False
        
        if not email or not validate_email(email):
            st.error("Please enter a valid email address")
            return False
        
        if not phone or not validate_phone(phone):
            st.error("Please enter a valid phone number")
            return False
        
        if status not in CUSTOMER_STATUS:
            st.error(f"Invalid status. Must be one of: {', '.join(CUSTOMER_STATUS)}")
            return False
        
        # Check for duplicate email
        customers = get_customers_data()
        if not customers.empty and email in customers['email'].values:
            st.error("A customer with this email already exists")
            return False
        
        # Create new customer record
        new_customer = pd.DataFrame({
            "id": [generate_customer_id()],
            "name": [sanitize_string(name)],
            "email": [email.lower()],
            "phone": [sanitize_string(phone)],
            "company": [sanitize_string(company)],
            "status": [status],
            "created_date": [datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")],
            "last_contact": [""]
        })
        
        # Append and save
        customers = pd.concat([customers, new_customer], ignore_index=True)
        if save_data(customers, CUSTOMERS_FILE):
            st.session_state.customers_data = customers
            st.success("Customer added successfully!")
            logger.info(f"New customer added: {email}")
            return True
        else:
            st.error("Failed to save customer data")
            return False
            
    except Exception as e:
        logger.error(f"Error adding customer: {str(e)}")
        st.error(f"An error occurred: {str(e)}")
        return False


def record_interaction(customer_id: str, interaction_type: str, notes: str, duration_minutes: int = 0) -> bool:
    """
    Record a customer interaction with validation.
    
    Args:
        customer_id: Customer ID
        interaction_type: Type of interaction
        notes: Interaction notes
        duration_minutes: Duration in minutes
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Validate inputs
        if not customer_id or not customer_id.startswith("CUST-"):
            st.error("Invalid customer ID")
            return False
        
        if interaction_type not in INTERACTION_TYPES:
            st.error(f"Invalid interaction type. Must be one of: {', '.join(INTERACTION_TYPES)}")
            return False
        
        if not notes or len(notes.strip()) < 5:
            st.error("Notes must be at least 5 characters long")
            return False
        
        if duration_minutes < 0 or duration_minutes > 1440:  # Max 24 hours
            st.error("Duration must be between 0 and 1440 minutes")
            return False
        
        # Verify customer exists
        customers = get_customers_data()
        if customer_id not in customers['id'].values:
            st.error("Customer not found")
            return False
        
        # Create interaction record
        new_interaction = pd.DataFrame({
            "id": [f"INT-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"],
            "customer_id": [customer_id],
            "type": [interaction_type],
            "notes": [sanitize_string(notes, max_length=500)],
            "date": [datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")],
            "duration_minutes": [duration_minutes]
        })
        
        # Append and save
        interactions = get_interactions_data()
        interactions = pd.concat([interactions, new_interaction], ignore_index=True)
        
        # Update last_contact in customers
        customers.loc[customers['id'] == customer_id, 'last_contact'] = datetime.utcnow().strftime("%Y-%m-%d")
        
        if save_data(interactions, INTERACTIONS_FILE) and save_data(customers, CUSTOMERS_FILE):
            st.session_state.interactions_data = interactions
            st.session_state.customers_data = customers
            st.success("Interaction recorded successfully!")
            logger.info(f"Interaction recorded for customer: {customer_id}")
            return True
        else:
            st.error("Failed to save interaction data")
            return False
            
    except Exception as e:
        logger.error(f"Error recording interaction: {str(e)}")
        st.error(f"An error occurred: {str(e)}")
        return False


# ============================================================================
# UI Components
# ============================================================================

def render_sidebar():
    """Render sidebar navigation."""
    with st.sidebar:
        st.title("🎯 DVO-CRM")
        st.write("Customer Relationship Management System")
        st.divider()
        
        page = st.radio(
            "Navigation",
            ["Dashboard", "Customers", "Interactions", "Analytics", "Settings"],
            key="page_selector"
        )
        
        st.divider()
        
        # Display stats
        customers = get_customers_data()
        if not customers.empty:
            st.metric("Total Customers", len(customers))
            active_count = len(customers[customers['status'] == 'Active'])
            st.metric("Active Customers", active_count)
        
        st.divider()
        
        if st.button("🔄 Refresh Data"):
            st.session_state.refresh_flag = True
            st.rerun()
        
        return page


def render_dashboard():
    """Render dashboard page."""
    st.title("📊 Dashboard")
    
    customers = get_customers_data()
    interactions = get_interactions_data()
    
    if customers.empty:
        st.info("No customer data available. Start by adding customers.")
        return
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Customers", len(customers))
    
    with col2:
        active = len(customers[customers['status'] == 'Active'])
        st.metric("Active Customers", active)
    
    with col3:
        if not interactions.empty:
            recent = len(interactions[
                (pd.to_datetime(interactions['date'], errors='coerce') > 
                 datetime.utcnow() - timedelta(days=30))
            ])
            st.metric("Interactions (30 days)", recent)
        else:
            st.metric("Interactions (30 days)", 0)
    
    with col4:
        st.metric("Total Companies", customers['company'].nunique())
    
    st.divider()
    
    # Status distribution
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Customer Status Distribution")
        status_counts = customers['status'].value_counts()
        st.bar_chart(status_counts)
    
    with col2:
        st.subheader("Top Companies")
        company_counts = customers['company'].value_counts().head(10)
        st.bar_chart(company_counts)
    
    st.divider()
    
    # Recent customers
    st.subheader("Recent Customers")
    recent_customers = customers.sort_values('created_date', ascending=False).head(5)
    st.dataframe(recent_customers, use_container_width=True)


def render_customers_page():
    """Render customers management page."""
    st.title("👥 Customers")
    
    tab1, tab2, tab3 = st.tabs(["View All", "Add New", "Search & Edit"])
    
    with tab1:
        st.subheader("All Customers")
        customers = get_customers_data()
        
        if customers.empty:
            st.info("No customers found. Add your first customer using the 'Add New' tab.")
        else:
            # Filter options
            col1, col2 = st.columns(2)
            
            with col1:
                status_filter = st.multiselect(
                    "Filter by Status",
                    CUSTOMER_STATUS,
                    default=CUSTOMER_STATUS
                )
            
            with col2:
                company_filter = st.multiselect(
                    "Filter by Company",
                    customers['company'].unique() if not customers.empty else [],
                    default=customers['company'].unique() if not customers.empty else []
                )
            
            # Apply filters
            filtered = customers[
                (customers['status'].isin(status_filter)) &
                (customers['company'].isin(company_filter))
            ]
            
            st.dataframe(
                filtered.sort_values('created_date', ascending=False),
                use_container_width=True,
                height=400
            )
            
            st.caption(f"Showing {len(filtered)} of {len(customers)} customers")
    
    with tab2:
        st.subheader("Add New Customer")
        
        with st.form("add_customer_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input(
                    "Full Name *",
                    max_chars=100,
                    help="Customer's full name (2-100 characters)"
                )
                email = st.text_input(
                    "Email Address *",
                    help="Valid email address"
                )
            
            with col2:
                phone = st.text_input(
                    "Phone Number *",
                    help="Valid phone number"
                )
                company = st.text_input(
                    "Company",
                    max_chars=100,
                    help="Company name (optional)"
                )
            
            status = st.selectbox(
                "Status *",
                CUSTOMER_STATUS,
                help="Customer status"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                submitted = st.form_submit_button("➕ Add Customer", use_container_width=True)
            with col2:
                st.form_submit_button("Clear", use_container_width=True, disabled=True)
            
            if submitted:
                add_customer(name, email, phone, company, status)
    
    with tab3:
        st.subheader("Search & Edit Customer")
        
        customers = get_customers_data()
        
        if customers.empty:
            st.info("No customers available")
        else:
            # Search functionality
            search_term = st.text_input("Search by name or email")
            
            if search_term:
                filtered = customers[
                    (customers['name'].str.contains(search_term, case=False, na=False)) |
                    (customers['email'].str.contains(search_term, case=False, na=False))
                ]
            else:
                filtered = customers
            
            if not filtered.empty:
                selected_customer = st.selectbox(
                    "Select a customer",
                    filtered.index,
                    format_func=lambda x: f"{filtered.loc[x, 'name']} ({filtered.loc[x, 'email']})"
                )
                
                customer = filtered.loc[selected_customer]
                
                st.subheader(f"Details - {customer['name']}")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.text_input("Name", value=customer['name'], disabled=True)
                    st.text_input("Email", value=customer['email'], disabled=True)
                
                with col2:
                    st.text_input("Phone", value=customer['phone'], disabled=True)
                    st.text_input("Company", value=customer['company'], disabled=True)
                
                st.text_input("Created Date", value=customer['created_date'], disabled=True)
                st.text_input("Last Contact", value=customer['last_contact'], disabled=True)
            else:
                st.info("No customers match your search")


def render_interactions_page():
    """Render interactions management page."""
    st.title("💬 Interactions")
    
    tab1, tab2 = st.tabs(["Record Interaction", "View History"])
    
    with tab1:
        st.subheader("Record New Interaction")
        
        customers = get_customers_data()
        
        if customers.empty:
            st.warning("No customers found. Please add customers first.")
        else:
            with st.form("record_interaction_form"):
                # Customer selection
                customer_options = {
                    f"{row['name']} ({row['email']})": row['id']
                    for _, row in customers.iterrows()
                }
                
                selected_customer = st.selectbox(
                    "Select Customer *",
                    list(customer_options.keys())
                )
                
                customer_id = customer_options[selected_customer]
                
                col1, col2 = st.columns(2)
                
                with col1:
                    interaction_type = st.selectbox(
                        "Interaction Type *",
                        INTERACTION_TYPES
                    )
                
                with col2:
                    duration = st.number_input(
                        "Duration (minutes)",
                        min_value=0,
                        max_value=1440,
                        value=0,
                        step=5
                    )
                
                notes = st.text_area(
                    "Notes *",
                    max_chars=500,
                    height=100,
                    help="Minimum 5 characters"
                )
                
                submitted = st.form_submit_button("✅ Record Interaction", use_container_width=True)
                
                if submitted:
                    record_interaction(customer_id, interaction_type, notes, duration)
    
    with tab2:
        st.subheader("Interaction History")
        
        interactions = get_interactions_data()
        customers = get_customers_data()
        
        if interactions.empty:
            st.info("No interactions recorded yet")
        else:
            # Merge with customer info for better display
            merged = interactions.merge(
                customers[['id', 'name']],
                left_on='customer_id',
                right_on='id',
                how='left'
            )
            
            # Filter options
            col1, col2 = st.columns(2)
            
            with col1:
                type_filter = st.multiselect(
                    "Filter by Type",
                    INTERACTION_TYPES,
                    default=INTERACTION_TYPES
                )
            
            with col2:
                days_back = st.slider("Last N days", 1, 365, 30)
            
            # Apply filters
            cutoff_date = (datetime.utcnow() - timedelta(days=days_back)).strftime("%Y-%m-%d")
            filtered = merged[
                (merged['type'].isin(type_filter)) &
                (merged['date'] >= cutoff_date)
            ]
            
            if not filtered.empty:
                display_df = filtered[['name', 'type', 'date', 'duration_minutes', 'notes']].copy()
                display_df.columns = ['Customer', 'Type', 'Date', 'Duration (min)', 'Notes']
                
                st.dataframe(
                    display_df.sort_values('Date', ascending=False),
                    use_container_width=True,
                    height=400
                )
                
                st.caption(f"Showing {len(filtered)} interactions from last {days_back} days")
            else:
                st.info("No interactions found for the selected filters")


def render_analytics_page():
    """Render analytics page."""
    st.title("📈 Analytics")
    
    customers = get_customers_data()
    interactions = get_interactions_data()
    
    if customers.empty:
        st.info("Insufficient data for analytics. Add customers and interactions first.")
        return
    
    # Customer metrics
    st.subheader("Customer Metrics")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total = len(customers)
        st.metric("Total Customers", total)
    
    with col2:
        if not customers['created_date'].empty:
            try:
                last_30_days = len(customers[
                    pd.to_datetime(customers['created_date']) > 
                    datetime.utcnow() - timedelta(days=30)
                ])
                st.metric("New (30 days)", last_30_days)
            except:
                st.metric("New (30 days)", 0)
        else:
            st.metric("New (30 days)", 0)
    
    with col3:
        avg_company_size = customers.groupby('company').size().mean()
        st.metric("Avg Company Size", f"{avg_company_size:.1f}")
    
    st.divider()
    
    # Interaction metrics
    if not interactions.empty:
        st.subheader("Interaction Metrics")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_interactions = len(interactions)
            st.metric("Total Interactions", total_interactions)
        
        with col2:
            try:
                avg_duration = interactions['duration_minutes'].mean()
                st.metric("Avg Duration (min)", f"{avg_duration:.1f}")
            except:
                st.metric("Avg Duration (min)", 0)
        
        with col3:
            customers_with_interactions = interactions['customer_id'].nunique()
            pct = (customers_with_interactions / len(customers)) * 100
            st.metric("Engaged Customers", f"{pct:.1f}%")
        
        st.divider()
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Interactions by Type")
            type_counts = interactions['type'].value_counts()
            st.bar_chart(type_counts)
        
        with col2:
            st.subheader("Interaction Trends (Last 30 days)")
            try:
                interactions['date'] = pd.to_datetime(interactions['date'])
                last_30 = interactions[
                    interactions['date'] > datetime.utcnow() - timedelta(days=30)
                ].copy()
                
                if not last_30.empty:
                    daily_counts = last_30.groupby(last_30['date'].dt.date).size()
                    st.line_chart(daily_counts)
                else:
                    st.info("No interactions in the last 30 days")
            except Exception as e:
                logger.error(f"Error creating trend chart: {str(e)}")
                st.error("Could not create trend chart")


def render_settings_page():
    """Render settings page."""
    st.title("⚙️ Settings")
    
    st.subheader("Data Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Refresh All Data", use_container_width=True):
            st.session_state.refresh_flag = True
            st.session_state.customers_data = None
            st.session_state.interactions_data = None
            st.rerun()
    
    with col2:
        if st.button("📥 Export Data", use_container_width=True):
            customers = get_customers_data()
            interactions = get_interactions_data()
            
            # Create export data
            export_data = {
                "customers": customers.to_dict(orient='records') if not customers.empty else [],
                "interactions": interactions.to_dict(orient='records') if not interactions.empty else [],
                "export_date": datetime.utcnow().isoformat()
            }
            
            st.download_button(
                label="💾 Download JSON",
                data=json.dumps(export_data, indent=2),
                file_name=f"dvo_crm_export_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
    
    st.divider()
    
    st.subheader("Database Statistics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Customers File", CUSTOMERS_FILE.stat().st_size if CUSTOMERS_FILE.exists() else 0, "bytes")
    
    with col2:
        st.metric("Interactions File", INTERACTIONS_FILE.stat().st_size if INTERACTIONS_FILE.exists() else 0, "bytes")
    
    st.divider()
    
    st.subheader("Application Info")
    
    info_col = st.container()
    with info_col:
        st.write(f"**Version:** 1.0.0")
        st.write(f"**Last Updated:** 2026-01-04")
        st.write(f"**Data Directory:** {DATA_DIR.absolute()}")
        st.write(f"**Current Time (UTC):** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}")


# ============================================================================
# Main Application
# ============================================================================

def main():
    """Main application entry point."""
    try:
        # Initialize session state
        initialize_session_state()
        
        # Render sidebar and get selected page
        page = render_sidebar()
        
        # Route to appropriate page
        if page == "Dashboard":
            render_dashboard()
        elif page == "Customers":
            render_customers_page()
        elif page == "Interactions":
            render_interactions_page()
        elif page == "Analytics":
            render_analytics_page()
        elif page == "Settings":
            render_settings_page()
        
    except Exception as e:
        logger.error(f"Application error: {str(e)}", exc_info=True)
        st.error(f"An unexpected error occurred: {str(e)}")
        st.info("Please refresh the page or contact support if the problem persists.")


if __name__ == "__main__":
    main()
