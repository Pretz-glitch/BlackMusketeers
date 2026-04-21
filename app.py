import streamlit as st
st.set_page_config(page_title="Wardrobe System", layout="wide")

import os
import uuid
import collections
import random
from PIL import Image
from models import create_db_and_tables, engine, DressItem
from ai_classifier import classify_dress
from sqlmodel import Session, select
from dotenv import load_dotenv

load_dotenv()
create_db_and_tables()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class LRUCache:
    def __init__(self, capacity: int):
        self.cache = collections.OrderedDict()
        self.capacity = capacity

    def get(self, key: int) -> dict:
        if key not in self.cache:
            return None
        self.cache.move_to_end(key)
        return self.cache[key]

    def put(self, key: int, value: dict) -> None:
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)

if 'stats_cache' not in st.session_state:
    st.session_state.stats_cache = LRUCache(5)

st.title("Wardrobe System")

tab1, tab2, tab3, tab4 = st.tabs(["Upload Item", "My Wardrobe", "Outfit Builder", "About"])

with tab1:
    st.header("Add to Wardrobe")
    
    if not os.getenv("GEMINI_API_KEY"):
        st.warning("API Key not found. Classification will fail.")

    input_mode = st.radio("Input Method", ["File Upload", "Camera"])
    uploaded_file = st.file_uploader("Select Image") if input_mode == "File Upload" else st.camera_input("Take Photo")
    
    if uploaded_file:
        col1, col2 = st.columns(2)
        with col1:
            st.image(uploaded_file, use_column_width=True)
            
        with col2:
            if st.button("Process and Save", type="primary"):
                with st.spinner("Processing..."):
                    file_path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4().hex}_{uploaded_file.name}")
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    c = classify_dress(file_path)
                    
                    if c.get("season") == "Unknown" and c.get("style") == "Unknown":
                        st.error(f"Failed to parse tags. Check API limits. Error: {c.get('error_msg')}")
                    else:
                        st.success("Item saved successfully.")
                        st.write("Type:", c["clothing_type"])
                        st.write("Style:", c["style"])
                        st.write("Season:", c["season"])
                        st.write("Aesthetic:", c["aesthetic"])
                        st.write("Theme:", c["color_theme"], "| Hue:", c["color_hue"])
                        st.write("Fabric:", c["fabric"])
                        
                        item = DressItem(
                            filename=uploaded_file.name,
                            image_path=file_path,
                            clothing_type=c["clothing_type"].title(),
                            season=c["season"].title(),
                            style=c["style"].title(),
                            aesthetic=c["aesthetic"].title(),
                            color_theme=c["color_theme"].title(),
                            color_hue=c["color_hue"].title(),
                            fabric=c["fabric"].title()
                        )
                        
                        with Session(engine) as session:
                            session.add(item)
                            session.commit()
                            
                        st.session_state.stats_cache.put(-1, None)

with tab2:
    st.header("Inventory Overview")
    
    with Session(engine) as session:
        items = session.exec(select(DressItem).order_by(DressItem.created_at.desc())).all()
    
    if not items:
        st.info("Inventory is empty.")
    else:
        # PCPartPicker style filtering
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            f_search = st.text_input("Fuzzy Search (Tags, Terms, Keywords, Colors)")
        
        col_f_a, col_f_b, col_f_c, col_f_d = st.columns(4)
        
        types = ["All"] + sorted(list(set([i.clothing_type for i in items])))
        styles = ["All"] + sorted(list(set([i.style for i in items])))
        seasons = ["All"] + sorted(list(set([i.season for i in items])))
        aesthetics = ["All"] + sorted(list(set([i.aesthetic for i in items])))
        
        with col_f_a: f_type = st.selectbox("Category", types)
        with col_f_b: f_style = st.selectbox("Style", styles)
        with col_f_c: f_season = st.selectbox("Season", seasons)
        with col_f_d: f_aesthetic = st.selectbox("Aesthetic", aesthetics)
        
        display_items = []
        for i in items:
            match = True
            if f_type != "All" and i.clothing_type != f_type: match = False
            if f_style != "All" and i.style != f_style: match = False
            if f_season != "All" and i.season != f_season: match = False
            if f_aesthetic != "All" and i.aesthetic != f_aesthetic: match = False
            
            # Fuzzy match check
            if f_search:
                q = f_search.lower()
                blob = f"{i.clothing_type} {i.season} {i.style} {i.aesthetic} {i.color_theme} {i.color_hue} {i.fabric}".lower()
                if not all(term in blob for term in q.split()):
                    match = False
                    
            if match:
                display_items.append(i)
                
        st.subheader(f"Results ({len(display_items)} items)")
        st.divider()
        
        cols = st.columns(4)
        for idx, item in enumerate(display_items):
            with cols[idx % 4]:
                with st.container(border=True):
                    try:
                        img = Image.open(item.image_path)
                        st.image(img, use_column_width=True)
                    except Exception:
                        st.warning("Missing media")
                    st.markdown(f"**{item.color_hue} {item.clothing_type}**")
                    st.caption(f"{item.fabric} | {item.aesthetic} | {item.style}")
                    if st.button("Delete", key=f"delete_{item.id}"):
                        with Session(engine) as d_session:
                            item_to_delete = d_session.get(DressItem, item.id)
                            if item_to_delete:
                                d_session.delete(item_to_delete)
                                d_session.commit()
                                try:
                                    if os.path.exists(item_to_delete.image_path):
                                        os.remove(item_to_delete.image_path)
                                except Exception:
                                    pass
                                st.rerun()

with tab3:
    st.header("Outfit Builder")
    st.write("Construct outfits manually or click randomize to generate combinations.")
    
    with Session(engine) as session:
        all_inv = session.exec(select(DressItem)).all()
        
    if not all_inv:
         st.info("No items found to build an outfit.")
    else:
        # Group logic
        tops = [i for i in all_inv if i.clothing_type.lower() == "top"]
        bottoms = [i for i in all_inv if i.clothing_type.lower() == "bottom"]
        fulls = [i for i in all_inv if i.clothing_type.lower() == "full"]
        footwear = [i for i in all_inv if i.clothing_type.lower() == "footwear"]
        accessories = [i for i in all_inv if i.clothing_type.lower() == "accessory"]
        
        col_ctrl1, col_ctrl2 = st.columns(2)
        with col_ctrl1:
            generator_type = st.radio("Outfit Type", ["Separates", "Full Body"])
        with col_ctrl2:
             if st.button("RANDOMIZE OUTFIT", type="primary"):
                 st.session_state.r_top = random.choice(tops) if tops else None
                 st.session_state.r_bottom = random.choice(bottoms) if bottoms else None
                 st.session_state.r_full = random.choice(fulls) if fulls else None
                 st.session_state.r_foot = random.choice(footwear) if footwear else None
                 st.session_state.r_acc = random.choice(accessories) if accessories else None

        st.subheader("Current Loadout")
        
        def dict_options(group):
            d = {"None": None}
            d.update({f"[{g.id}] {g.color_hue} {g.style}": g for g in group})
            return d
            
        t_opts = dict_options(tops)
        b_opts = dict_options(bottoms)
        f_opts = dict_options(fulls)
        s_opts = dict_options(footwear)
        a_opts = dict_options(accessories)
        
        s_c1, s_c2, s_c3, s_c4 = st.columns(4)

        with s_c1:
            if generator_type == "Separates":
                sel_t = st.selectbox("Slot: Top", list(t_opts.keys()))
                t_item = st.session_state.get("r_top") if st.session_state.get("r_top") and sel_t == "None" else t_opts[sel_t]
                if t_item:
                    st.image(Image.open(t_item.image_path), use_column_width=True)
                    st.caption(f"{t_item.color_hue} {t_item.fabric}")
            else:
                sel_f = st.selectbox("Slot: Full Body", list(f_opts.keys()))
                f_item = st.session_state.get("r_full") if st.session_state.get("r_full") and sel_f == "None" else f_opts[sel_f]
                if f_item:
                    st.image(Image.open(f_item.image_path), use_column_width=True)
                    st.caption(f"{f_item.color_hue} {f_item.fabric}")
                    
        with s_c2:
            if generator_type == "Separates":
                sel_b = st.selectbox("Slot: Bottom", list(b_opts.keys()))
                b_item = st.session_state.get("r_bottom") if st.session_state.get("r_bottom") and sel_b == "None" else b_opts[sel_b]
                if b_item:
                    st.image(Image.open(b_item.image_path), use_column_width=True)
                    st.caption(f"{b_item.color_hue} {b_item.fabric}")

        with s_c3:
            sel_s = st.selectbox("Slot: Footwear", list(s_opts.keys()))
            s_item = st.session_state.get("r_foot") if st.session_state.get("r_foot") and sel_s == "None" else s_opts[sel_s]
            if s_item:
                st.image(Image.open(s_item.image_path), use_column_width=True)
                st.caption(f"{s_item.color_hue} {s_item.fabric}")
                
        with s_c4:
            sel_a = st.selectbox("Slot: Accessory", list(a_opts.keys()))
            a_item = st.session_state.get("r_acc") if st.session_state.get("r_acc") and sel_a == "None" else a_opts[sel_a]
            if a_item:
                st.image(Image.open(a_item.image_path), use_column_width=True)
                st.caption(f"{a_item.color_hue} {a_item.fabric}")

with tab4:
    st.header("About")
    st.write("Application utilizes SQLModel for database modeling, handling multiple attribute vectors per item.")
    st.write("The Outfit Builder mirrors RPG-style loadout architectures allowing slot-based generation and manual overrides.")
    st.write("Search algorithms utilize continuous subset array matching for fuzzy criteria resolution.")
