import os
import streamlit as st
from sqlalchemy import create_engine, Column, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from sqlalchemy.sql import func
import uuid
from typing import List, Optional, Dict, Any
from utils.encryption import encrypt_data, decrypt_data, is_encryption_enabled

Base = declarative_base()

class Notebook(Base):
    __tablename__ = 'notebooks'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_email = Column(String, nullable=False, index=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    sections = relationship("Section", back_populates="notebook", cascade="all, delete-orphan")

class Section(Base):
    __tablename__ = 'sections'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    notebook_id = Column(String, ForeignKey('notebooks.id'), nullable=False)
    name = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    notebook = relationship("Notebook", back_populates="sections")
    pages = relationship("Page", back_populates="section", cascade="all, delete-orphan")

class Page(Base):
    __tablename__ = 'pages'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    section_id = Column(String, ForeignKey('sections.id'), nullable=False)
    name = Column(String, nullable=False)
    content = Column(Text, default="")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    section = relationship("Section", back_populates="pages")

def get_db_url():
    # Check secrets first
    if "NEON_DATABASE_URL" in st.secrets:
        return st.secrets["NEON_DATABASE_URL"]
    if "DATABASE_URL" in st.secrets:
        return st.secrets["DATABASE_URL"]
        
    # Check environment variables
    if os.getenv("NEON_DATABASE_URL"):
        return os.getenv("NEON_DATABASE_URL")
    return os.getenv("DATABASE_URL")

def init_db():
    url = get_db_url()
    if not url:
        print("DEBUG: No DATABASE_URL found in secrets or env vars")
        return None
    print(f"DEBUG: Found DATABASE_URL: {url[:10]}...")
    
    # Fix for streamlit cloud usage of postgresql dialect
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
        
    engine = create_engine(url)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)

# Global session factory
SessionLocal = init_db()

def get_session():
    if SessionLocal:
        return SessionLocal()
    print("DEBUG: SessionLocal is None - DB not initialized")
    return None

# --- CRUD Operations ---

def get_user_notebooks(user_email: str) -> List[Dict[str, Any]]:
    session = get_session()
    if not session:
        return []
    
    try:
        notebooks = session.query(Notebook).filter(Notebook.user_email == user_email).order_by(Notebook.created_at).all()
        result = []
        for nb in notebooks:
            # Build the nested structure expected by the app
            nb_dict = {
                "id": nb.id,
                "name": nb.name,
                "sections": {}
            }
            
            # Fetch sections and pages eagerly or lazily (here lazily but structured)
            for section in nb.sections:
                section_dict = {
                    "id": section.id,
                    "name": section.name,
                    "pages": {}
                }
                
                for page in section.pages:
                    # Decrypt content if needed
                    content = page.content
                    if is_encryption_enabled() and content:
                        try:
                            # Assuming content is stored as hex or base64 string in DB if encrypted?
                            # Actually, encrypt_data returns bytes. We need to store as string in Text column.
                            # Let's assume we store base64 encoded string of the encrypted bytes.
                            # But wait, the existing app logic handles encryption at the file level.
                            # Here we want to encrypt specific fields.
                            # Let's handle encryption/decryption in the save/load functions specifically.
                            pass 
                        except:
                            pass
                            
                    section_dict["pages"][page.name] = { 
                        "name": page.name,
                        "content": content
                    }
                
                nb_dict["sections"][section.name] = section_dict
            
            result.append(nb_dict)
            
        # Convert list to dict keyed by ID to match app expectation
        return {nb["id"]: nb for nb in result}
    finally:
        session.close()

def create_notebook_db(user_email: str, name: str) -> bool:
    print(f"DEBUG: create_notebook_db called for {user_email}, name={name}")
    session = get_session()
    if not session: 
        print("DEBUG: create_notebook_db failed - no session")
        return False
    try:
        # Check if name exists for user
        exists = session.query(Notebook).filter(Notebook.user_email == user_email, Notebook.name == name).first()
        if exists: return False
        
        new_nb = Notebook(user_email=user_email, name=name)
        session.add(new_nb)
        session.commit()
        return True
    except Exception as e:
        print(f"Error creating notebook: {e}")
        session.rollback()
        return False
    finally:
        session.close()

def update_notebook_name_db(notebook_id: str, new_name: str) -> bool:
    session = get_session()
    if not session: return False
    try:
        nb = session.query(Notebook).filter(Notebook.id == notebook_id).first()
        if nb:
            nb.name = new_name
            session.commit()
            return True
        return False
    except:
        session.rollback()
        return False
    finally:
        session.close()

def delete_notebook_db(notebook_id: str) -> bool:
    session = get_session()
    if not session: return False
    try:
        nb = session.query(Notebook).filter(Notebook.id == notebook_id).first()
        if nb:
            session.delete(nb)
            session.commit()
            return True
        return False
    except:
        session.rollback()
        return False
    finally:
        session.close()

def create_section_db(notebook_id: str, name: str) -> bool:
    session = get_session()
    if not session: return False
    try:
        # Check for duplicate section name in this notebook
        exists = session.query(Section).filter(Section.notebook_id == notebook_id, Section.name == name).first()
        if exists: return False
        
        new_section = Section(notebook_id=notebook_id, name=name)
        session.add(new_section)
        session.commit()
        return True
    except:
        session.rollback()
        return False
    finally:
        session.close()

def delete_section_db(notebook_id: str, section_name: str) -> bool:
    session = get_session()
    if not session: return False
    try:
        section = session.query(Section).filter(Section.notebook_id == notebook_id, Section.name == section_name).first()
        if section:
            session.delete(section)
            session.commit()
            return True
        return False
    except:
        session.rollback()
        return False
    finally:
        session.close()

def create_page_db(notebook_id: str, section_name: str, page_name: str) -> bool:
    # Note: We need to find the section by name within the notebook
    session = get_session()
    if not session: return False
    try:
        section = session.query(Section).filter(Section.notebook_id == notebook_id, Section.name == section_name).first()
        if not section: return False
        
        exists = session.query(Page).filter(Page.section_id == section.id, Page.name == page_name).first()
        if exists: return False
        
        new_page = Page(section_id=section.id, name=page_name, content="")
        session.add(new_page)
        session.commit()
        return True
    except:
        session.rollback()
        return False
    finally:
        session.close()

def delete_page_db(notebook_id: str, section_name: str, page_name: str) -> bool:
    session = get_session()
    if not session: return False
    try:
        section = session.query(Section).filter(Section.notebook_id == notebook_id, Section.name == section_name).first()
        if not section: return False
        
        page = session.query(Page).filter(Page.section_id == section.id, Page.name == page_name).first()
        if page:
            session.delete(page)
            session.commit()
            return True
        return False
    except:
        session.rollback()
        return False
    finally:
        session.close()

def save_page_content_db(notebook_id: str, section_name: str, page_name: str, content: str):
    session = get_session()
    if not session: return
    try:
        section = session.query(Section).filter(Section.notebook_id == notebook_id, Section.name == section_name).first()
        if not section: return
        
        page = session.query(Page).filter(Page.section_id == section.id, Page.name == page_name).first()
        if page:
            # Encrypt content if enabled
            if is_encryption_enabled():
                # We need to store encrypted bytes as a string representation (e.g. hex)
                # encrypt_data returns bytes
                encrypted_bytes = encrypt_data(content.encode('utf-8'))
                # Store as hex string to be safe in Text column
                page.content = "ENC:" + encrypted_bytes.hex()
            else:
                page.content = content
            session.commit()
    except Exception as e:
        print(f"Error saving page: {e}")
        session.rollback()
    finally:
        session.close()

def load_page_content_db(notebook_id: str, section_name: str, page_name: str) -> str:
    session = get_session()
    if not session: return ""
    try:
        section = session.query(Section).filter(Section.notebook_id == notebook_id, Section.name == section_name).first()
        if not section: return ""
        
        page = session.query(Page).filter(Page.section_id == section.id, Page.name == page_name).first()
        if page:
            content = page.content
            if content and content.startswith("ENC:"):
                if is_encryption_enabled():
                    try:
                        encrypted_bytes = bytes.fromhex(content[4:])
                        decrypted_bytes = decrypt_data(encrypted_bytes)
                        return decrypted_bytes.decode('utf-8')
                    except Exception as e:
                        print(f"Decryption error: {e}")
                        return "Error decrypting content"
                else:
                    return "Content is encrypted but encryption is disabled."
            return content
        return ""
    finally:
        session.close()
