import streamlit as st
import json
import os
from datetime import datetime
from pathlib import Path

# Configuration
DATA_DIR = Path("data")
NOTEBOOKS_FILE = DATA_DIR / "notebooks.json"

# Initialize data directory
DATA_DIR.mkdir(exist_ok=True)

def load_notebooks():
    """Load all notebooks from storage"""
    if NOTEBOOKS_FILE.exists():
        with open(NOTEBOOKS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_notebooks(notebooks):
    """Save all notebooks to storage"""
    with open(NOTEBOOKS_FILE, 'w') as f:
        json.dump(notebooks, f, indent=2)

def initialize_session_state():
    """Initialize session state variables"""
    if 'notebooks' not in st.session_state:
        st.session_state.notebooks = load_notebooks()
    if 'selected_notebook' not in st.session_state:
        st.session_state.selected_notebook = None
    if 'selected_section' not in st.session_state:
        st.session_state.selected_section = None
    if 'selected_page' not in st.session_state:
        st.session_state.selected_page = None
    if 'page_content' not in st.session_state:
        st.session_state.page_content = ""
    if 'expanded_sections' not in st.session_state:
        st.session_state.expanded_sections = set()
    if 'editor_collapsed' not in st.session_state:
        st.session_state.editor_collapsed = False

def create_notebook(name):
    """Create a new notebook"""
    if name and name.strip():
        notebook_id = name.strip().lower().replace(' ', '_')
        if notebook_id not in st.session_state.notebooks:
            st.session_state.notebooks[notebook_id] = {
                'name': name.strip(),
                'sections': {},
                'created_at': datetime.now().isoformat()
            }
            save_notebooks(st.session_state.notebooks)
            return True
    return False

def create_section(notebook_id, section_name):
    """Create a new section in a notebook"""
    if section_name and section_name.strip():
        section_id = section_name.strip().lower().replace(' ', '_')
        if notebook_id in st.session_state.notebooks:
            if section_id not in st.session_state.notebooks[notebook_id]['sections']:
                st.session_state.notebooks[notebook_id]['sections'][section_id] = {
                    'name': section_name.strip(),
                    'pages': {},
                    'created_at': datetime.now().isoformat()
                }
                save_notebooks(st.session_state.notebooks)
                return True
    return False

def create_page(notebook_id, section_id, page_name):
    """Create a new page in a section"""
    if page_name and page_name.strip():
        page_id = page_name.strip().lower().replace(' ', '_')
        if (notebook_id in st.session_state.notebooks and 
            section_id in st.session_state.notebooks[notebook_id]['sections']):
            if page_id not in st.session_state.notebooks[notebook_id]['sections'][section_id]['pages']:
                st.session_state.notebooks[notebook_id]['sections'][section_id]['pages'][page_id] = {
                    'name': page_name.strip(),
                    'content': '',
                    'created_at': datetime.now().isoformat(),
                    'updated_at': datetime.now().isoformat()
                }
                save_notebooks(st.session_state.notebooks)
                return True
    return False

def update_notebook_name(notebook_id, new_name):
    """Update notebook name"""
    if notebook_id in st.session_state.notebooks and new_name and new_name.strip():
        st.session_state.notebooks[notebook_id]['name'] = new_name.strip()
        save_notebooks(st.session_state.notebooks)
        return True
    return False

def delete_notebook(notebook_id):
    """Delete a notebook"""
    if notebook_id in st.session_state.notebooks:
        del st.session_state.notebooks[notebook_id]
        save_notebooks(st.session_state.notebooks)
        if st.session_state.selected_notebook == notebook_id:
            st.session_state.selected_notebook = None
            st.session_state.selected_section = None
            st.session_state.selected_page = None

def delete_section(notebook_id, section_id):
    """Delete a section"""
    if (notebook_id in st.session_state.notebooks and 
        section_id in st.session_state.notebooks[notebook_id]['sections']):
        del st.session_state.notebooks[notebook_id]['sections'][section_id]
        save_notebooks(st.session_state.notebooks)
        if st.session_state.selected_section == section_id:
            st.session_state.selected_section = None
            st.session_state.selected_page = None

def delete_page(notebook_id, section_id, page_id):
    """Delete a page"""
    if (notebook_id in st.session_state.notebooks and 
        section_id in st.session_state.notebooks[notebook_id]['sections'] and
        page_id in st.session_state.notebooks[notebook_id]['sections'][section_id]['pages']):
        del st.session_state.notebooks[notebook_id]['sections'][section_id]['pages'][page_id]
        save_notebooks(st.session_state.notebooks)
        if st.session_state.selected_page == page_id:
            st.session_state.selected_page = None
            st.session_state.page_content = ""

def save_page_content(notebook_id, section_id, page_id, content):
    """Save page content"""
    if (notebook_id in st.session_state.notebooks and 
        section_id in st.session_state.notebooks[notebook_id]['sections'] and
        page_id in st.session_state.notebooks[notebook_id]['sections'][section_id]['pages']):
        st.session_state.notebooks[notebook_id]['sections'][section_id]['pages'][page_id]['content'] = content
        st.session_state.notebooks[notebook_id]['sections'][section_id]['pages'][page_id]['updated_at'] = datetime.now().isoformat()
        save_notebooks(st.session_state.notebooks)

def main():
    st.set_page_config(
        page_title="My OneNote",
        page_icon="📓",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    initialize_session_state()
    
    # Custom CSS for better styling - compact vertical spacing
    st.markdown("""
    <style>
    .main-header {
        font-size: 2rem;
        font-weight: bold;
        color: #0078d4;
        margin-bottom: 0.25rem;
    }
    .page-title {
        font-size: 2rem;
        font-weight: bold;
        margin-bottom: 0.25rem;
    }
    .section-item {
        padding: 0.4rem;
        margin: 0.05rem 0;
        cursor: pointer;
        border-radius: 4px;
        font-weight: 500;
        border-left: 4px solid transparent;
        text-align: left;
    }
    .section-item:hover {
        background-color: #f5f5f5;
    }
    .section-item.selected {
        background-color: #e8f5e9;
        border-left-color: #4caf50;
        font-weight: 600;
    }
    .page-item {
        padding: 0.3rem 0.4rem;
        margin: 0.02rem 0;
        cursor: pointer;
        border-radius: 4px;
        font-size: 0.95rem;
        text-align: left;
    }
    .page-item:hover {
        background-color: #fafafa;
    }
    .page-item.selected {
        background-color: #e3f2fd;
        font-weight: 500;
    }
    .column-header {
        font-weight: 600;
        font-size: 0.9rem;
        color: #666;
        margin-bottom: 0.25rem;
        padding-bottom: 0.25rem;
        border-bottom: 1px solid #e0e0e0;
        min-height: 1.5rem;
    }
    /* Ensure expanders are aligned */
    .streamlit-expanderHeader {
        font-size: 0.9rem !important;
        padding: 0.25rem 0.5rem !important;
    }
    /* Ensure consistent spacing in columns */
    [data-testid="column"] {
        padding-top: 0 !important;
    }
    /* Reduce spacing between buttons in sections and pages columns */
    [data-testid="column"] [data-testid="stVerticalBlock"] > div[data-testid="element-container"] {
        margin-bottom: 0.15rem !important;
    }
    [data-testid="column"] button {
        margin-top: 0 !important;
        margin-bottom: 0 !important;
    }
    /* Reduce vertical spacing in main content */
    .element-container {
        margin-bottom: 0.5rem !important;
    }
    /* Reduce spacing in markdown headers */
    h3 {
        margin-top: 0.5rem !important;
        margin-bottom: 0.25rem !important;
    }
    /* Compact spacing for text areas */
    [data-testid="stTextArea"] {
        margin-bottom: 0.5rem !important;
    }
    /* Reduce spacing between sections */
    hr {
        margin: 0.5rem 0 !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Top Bar - Notebook Selection
    notebooks = st.session_state.notebooks
    
    col_top1, col_top2, col_top3 = st.columns([3, 1, 1])
    with col_top1:
        st.markdown('<div class="main-header">📓 My OneNote</div>', unsafe_allow_html=True)
        
        # Display notebook name if one is selected
        if notebooks and st.session_state.selected_notebook and st.session_state.selected_notebook in notebooks:
            notebook = notebooks[st.session_state.selected_notebook]
            notebook_name = notebook['name']
            
            # Initialize edit state
            edit_key = f"edit_notebook_name_{st.session_state.selected_notebook}"
            if edit_key not in st.session_state:
                st.session_state[edit_key] = False
            
            if st.session_state[edit_key]:
                # Edit mode - input field with save/cancel buttons inline
                col_edit1, col_edit2, col_edit3 = st.columns([6, 1, 1])
                with col_edit1:
                    new_name = st.text_input(
                        "Notebook Name",
                        value=notebook_name,
                        key=f"notebook_name_input_{st.session_state.selected_notebook}",
                        label_visibility="collapsed"
                    )
                with col_edit2:
                    if st.button("✓", key=f"save_name_{st.session_state.selected_notebook}", use_container_width=True):
                        if new_name and new_name.strip() and new_name != notebook_name:
                            if update_notebook_name(st.session_state.selected_notebook, new_name):
                                st.success("Notebook name updated!")
                            else:
                                st.error("Failed to update notebook name")
                        st.session_state[edit_key] = False
                        st.rerun()
                with col_edit3:
                    if st.button("✗", key=f"cancel_name_{st.session_state.selected_notebook}", use_container_width=True):
                        st.session_state[edit_key] = False
                        st.rerun()
            else:
                # Display mode - name with edit button inline
                col_name, col_edit, _ = st.columns([1, 1, 10])
                with col_name:
                    st.markdown(f'<div style="font-size: 1.2rem; color: #666; margin-top: 0.5rem; white-space: nowrap;">{notebook_name}</div>', unsafe_allow_html=True)
                with col_edit:
                    if st.button("✏️", key=f"edit_trigger_{st.session_state.selected_notebook}", help="Edit notebook name"):
                        st.session_state[edit_key] = True
                        st.rerun()
    
    with col_top2:
        if notebooks:
            notebook_options = ["Select a notebook..."] + [notebooks[nb]['name'] for nb in notebooks.keys()]
            notebook_ids = ["None"] + list(notebooks.keys())
            selected_index = 0
            if st.session_state.selected_notebook in notebooks:
                selected_index = notebook_ids.index(st.session_state.selected_notebook)
            
            selected_notebook_name = st.selectbox(
                "Notebook",
                notebook_options,
                index=selected_index,
                key="notebook_selector_top",
                label_visibility="collapsed"
            )
            
            if selected_notebook_name != "Select a notebook...":
                selected_notebook_id = notebook_ids[notebook_options.index(selected_notebook_name)]
                if st.session_state.selected_notebook != selected_notebook_id:
                    st.session_state.selected_notebook = selected_notebook_id
                    st.session_state.selected_section = None
                    st.session_state.selected_page = None
                    # Reset edit state when switching notebooks
                    for key in list(st.session_state.keys()):
                        if key.startswith('edit_notebook_name_'):
                            st.session_state[key] = False
                    st.rerun()
        else:
            st.selectbox("Notebook", ["No notebooks"], key="notebook_selector_empty", label_visibility="collapsed", disabled=True)
    
    with col_top3:
        with st.expander("➕ Create Notebook", expanded=False):
            new_notebook_name = st.text_input("Notebook Name", key="new_notebook_top", label_visibility="collapsed")
            if st.button("Create", key="create_notebook_btn_top"):
                if create_notebook(new_notebook_name):
                    st.success(f"Notebook '{new_notebook_name}' created!")
                    st.rerun()
                else:
                    st.error("Please enter a valid notebook name or notebook already exists")
    
    st.markdown("---")
    
    # Three Column Layout: Sections | Pages | Content
    if notebooks and st.session_state.selected_notebook and st.session_state.selected_notebook in notebooks:
        notebook = notebooks[st.session_state.selected_notebook]
        sections = notebook.get('sections', {})
        
        # Generate all section styles at once - moved outside columns to prevent layout shift
        if sections:
            section_styles = []
            section_colors = {
                'management': '#9c27b0',
                'team': '#2196f3',
                'quick_notes': '#4caf50',
                'default': '#757575'
            }
            
            for section_id in sections.keys():
                color = section_colors.get(section_id, section_colors['default'])
                section_styles.append(f"""
                .section-btn-{section_id} {{
                    border-left: 4px solid {color} !important;
                }}
                """)
            
            # Inject all styles in one go
            if section_styles:
                st.markdown(f"<style>{''.join(section_styles)}</style>", unsafe_allow_html=True)
        
        # Create three columns
        col_sections, col_pages, col_content = st.columns([1, 1, 6])
        
        # Column 1: Sections
        with col_sections:
            st.markdown('<div class="column-header">Sections</div>', unsafe_allow_html=True)
            
            # Add Section button
            with st.expander("➕ Add Section", expanded=False):
                new_section_name = st.text_input("Section Name", key="new_section_col1", label_visibility="collapsed")
                if st.button("Create", key="create_section_btn_col1"):
                    if create_section(st.session_state.selected_notebook, new_section_name):
                        st.success(f"Section '{new_section_name}' created!")
                        st.rerun()
                    else:
                        st.error("Please enter a valid section name or section already exists")
            
            # Display sections
            if sections:
                for section_id, section in sections.items():
                    section_selected = st.session_state.selected_section == section_id
                    
                    if st.button(
                        f"📑 {section['name']}",
                        key=f"section_{section_id}_col1",
                        use_container_width=True,
                        type="primary" if section_selected else "secondary"
                    ):
                        st.session_state.selected_section = section_id
                        st.session_state.selected_page = None
                        st.rerun()
            else:
                st.info("No sections yet. Create one to get started!")
        
        # Column 2: Pages
        with col_pages:
            st.markdown('<div class="column-header">Pages</div>', unsafe_allow_html=True)

            # Add Page button - always show for consistent alignment
            if st.session_state.selected_section and st.session_state.selected_section in sections:
                with st.expander("➕ Add Page", expanded=False):
                    new_page_name = st.text_input("Page Name", key="new_page_col2", label_visibility="collapsed")
                    if st.button("Create", key="create_page_btn_col2"):
                        if create_page(st.session_state.selected_notebook, st.session_state.selected_section, new_page_name):
                            st.success(f"Page '{new_page_name}' created!")
                            st.rerun()
                        else:
                            st.error("Please enter a valid page name or page already exists")
            else:
                # Empty expander placeholder for alignment
                with st.expander("➕ Add Page", expanded=False):
                    st.info("Select a section first")

            # Display pages
            if st.session_state.selected_section and st.session_state.selected_section in sections:
                section = sections[st.session_state.selected_section]
                pages = section.get('pages', {})

                if pages:
                    for page_id, page in pages.items():
                        page_selected = st.session_state.selected_page == page_id

                        if st.button(
                            f"📄 {page['name']}",
                            key=f"page_{page_id}_col2",
                            use_container_width=True,
                            type="primary" if page_selected else "secondary"
                        ):
                            st.session_state.selected_page = page_id
                            # Load page content immediately
                            st.session_state.page_content = page.get('content', '')
                            # Reset save state when switching pages
                            st.session_state.save_clicked = False
                            # Reset delete confirmation state when switching pages
                            for key in list(st.session_state.keys()):
                                if key.startswith('delete_confirm_'):
                                    st.session_state[key] = False
                            st.rerun()
                else:
                    st.info("No pages yet. Create one to get started!")
            else:
                st.info("👈 Select a section to view pages")
        
        # Column 3: Content
        with col_content:
            if st.session_state.selected_notebook and st.session_state.selected_section and st.session_state.selected_page:
                notebook = notebooks[st.session_state.selected_notebook]
                section = notebook['sections'][st.session_state.selected_section]
                page = section['pages'][st.session_state.selected_page]
                
                # Load page content - always sync with page data when page changes
                current_content = page.get('content', '')
                # Update session state if content differs (handles page switching)
                if st.session_state.page_content != current_content:
                    st.session_state.page_content = current_content
                
                # Page Header
                col_header1, col_header2, col_header3 = st.columns([6, 1, 1])
                with col_header1:
                    st.markdown(f'<div class="page-title">{page["name"]}</div>', unsafe_allow_html=True)
                
                # Initialize save button state
                if 'save_clicked' not in st.session_state:
                    st.session_state.save_clicked = False
                
                with col_header2:
                    save_clicked = st.button("💾 Save", use_container_width=True, type="primary", key="save_page_btn")
                    if save_clicked:
                        st.session_state.save_clicked = True
                
                with col_header3:
                    # Initialize delete confirmation state
                    delete_key = f"delete_confirm_{st.session_state.selected_page}"
                    if delete_key not in st.session_state:
                        st.session_state[delete_key] = False
                    
                    if st.session_state[delete_key]:
                        # Second click - confirm deletion
                        if st.button("⚠️ Confirm Delete", use_container_width=True, type="primary"):
                            delete_page(st.session_state.selected_notebook, 
                                       st.session_state.selected_section, 
                                       st.session_state.selected_page)
                            st.session_state[delete_key] = False
                            st.rerun()
                        if st.button("❌ Cancel", use_container_width=True):
                            st.session_state[delete_key] = False
                            st.rerun()
                    else:
                        # First click - show confirmation
                        if st.button("🗑️ Delete Page", use_container_width=True):
                            st.session_state[delete_key] = True
                            st.rerun()
                
                st.markdown("---")
                
                # Toggle button for collapsing editor
                col_toggle1, col_toggle2 = st.columns([6, 1])
                with col_toggle1:
                    st.markdown("")  # Spacer
                with col_toggle2:
                    toggle_label = "👁️ Hide Editor" if not st.session_state.editor_collapsed else "📝 Show Editor"
                    if st.button(toggle_label, key="toggle_editor", use_container_width=True):
                        st.session_state.editor_collapsed = not st.session_state.editor_collapsed
                        st.rerun()
                
                # Container for both editor and preview
                content_container = st.container()
                with content_container:
                    if st.session_state.editor_collapsed:
                        # Only show preview when editor is collapsed
                        st.markdown("### 👁️ Preview")
                        content = st.session_state.page_content
                        if content:
                            st.markdown(content)
                        else:
                            st.info("Start typing in the editor to see the preview here.")
                    else:
                        # Split content area into Markdown Editor (left) and Preview (right)
                        col_editor, col_preview = st.columns([1, 1])
                        
                        with col_editor:
                            st.markdown("### 📝 Markdown Editor")
                            
                            # Markdown Editor
                            content = st.text_area(
                                "Markdown Content",
                                value=st.session_state.page_content,
                                height=650,
                                key=f"page_content_editor_{st.session_state.selected_page}",
                                help="Write your content in Markdown format. Use '- [ ]' for TODO items and '- [x]' for completed items.",
                                label_visibility="collapsed"
                            )
                        
                        with col_preview:
                            st.markdown("### 👁️ Preview")
                            
                            # Markdown Preview
                            if content:
                                st.markdown(content)
                            else:
                                st.info("Start typing in the editor to see the preview here.")
                
                # Update session state with current content
                st.session_state.page_content = content
                
                # Handle Save button click
                if st.session_state.save_clicked:
                    save_page_content(
                        st.session_state.selected_notebook,
                        st.session_state.selected_section,
                        st.session_state.selected_page,
                        content
                    )
                    st.session_state.page_content = content
                    st.session_state.save_clicked = False
                    st.success("✅ Page saved!")
                    st.rerun()
                
                # Auto-save on content change (optional - can be disabled if user prefers manual save)
                if content != current_content:
                    save_page_content(
                        st.session_state.selected_notebook,
                        st.session_state.selected_section,
                        st.session_state.selected_page,
                        content
                    )
                    st.session_state.page_content = content
            elif st.session_state.selected_section:
                st.info("👈 Select a page to start editing")
            elif st.session_state.selected_notebook:
                st.info("👈 Select a section to view pages")
            else:
                st.info("👈 Select a notebook, section, and page to start editing")
    else:
        # Welcome message when no notebook is selected
        st.info("👈 Create or select a notebook to get started!")
        
        st.markdown("""
        ## Welcome to My OneNote! 📓
        
        This is a Microsoft OneNote clone built with Streamlit.
        
        **Getting Started:**
        1. Create a new notebook using the button above
        2. Add sections to organize your notes
        3. Create pages within sections
        4. Start writing your notes!
        
        **Features:**
        - 📚 Multiple notebooks
        - 📑 Sections within notebooks
        - 📄 Pages within sections
        - ✏️ Markdown support for formatting
        - 💾 Auto-save functionality
        """)

if __name__ == "__main__":
    main()

