import streamlit as st
st.set_page_config(page_title="Dress Classifier", page_icon="👗", layout="wide")

import os
import uuid
import collections
from PIL import Image
from models import create_db_and_tables, engine, DressItem
from ai_classifier import classify_dress
from sqlmodel import Session, select
from dotenv import load_dotenv

load_dotenv()

# Ensure DB is created
create_db_and_tables()

# Ensure uploads directory exists
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class WardrobeCache:
    """
    LRU Cache implementation inspired by LeetCode 146
    Saves the most recently queried wardrobe statistics 
    to aviod recalculating stats unnecessarily.
    """
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

# Re-use cache for the whole session
if 'stats_cache' not in st.session_state:
    st.session_state.stats_cache = WardrobeCache(5)

st.title("👗 Dress Classifier & Wardrobe")

tab1, tab2, tab3 = st.tabs(["Upload & Classify", "My Wardrobe", "About (DSA Concepts)"])

with tab1:
    st.header("Upload or Snap a Dress Image")
    
    # Check for API key warning
    if not os.getenv("GEMINI_API_KEY"):
        st.warning("⚠️ GEMINI_API_KEY is not set in the environment or .env file! Classification will fail.")

    input_mode = st.radio("Choose Input Method", ["Upload File", "Take Photo"])
    uploaded_file = None
    
    if input_mode == "Upload File":
        uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
    else:
        uploaded_file = st.camera_input("Take a photo of the clothing item")
    
    if uploaded_file is not None:
        col1, col2 = st.columns(2)
        
        with col1:
            st.image(uploaded_file, caption="Image Preview", use_column_width=True)
            
        with col2:
            if st.button("Classify and Save", type="primary"):
                with st.spinner("Analyzing image..."):
                    # Save image locally securely using a unique UUID
                    unique_filename = f"{uuid.uuid4().hex}_{uploaded_file.name}"
                    file_path = os.path.join(UPLOAD_DIR, unique_filename)
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    # Classify using AI
                    classification = classify_dress(file_path)
                    
                    if classification.get("season") == "Unknown" and classification.get("style") == "Unknown":
                        st.error(f"Classification failed. \nError Message: {classification.get('error_msg', 'Unknown Error')}\nPlease try again or check your API key/billing constraints.")
                    else:
                        st.success("Successfully classified!")
                        st.write("**Season:**", classification["season"])
                        st.write("**Style:**", classification["style"])
                        st.write("**Color:**", classification["color"])
                        
                        # Save to database
                        dress_item = DressItem(
                            filename=uploaded_file.name,
                            image_path=file_path,
                            season=classification["season"],
                            style=classification["style"],
                            color=classification["color"]
                        )
                        
                        with Session(engine) as session:
                            session.add(dress_item)
                            session.commit()
                            
                        # Invalidate the cache by adding a new default key, we will re-run our grouping next time
                        st.session_state.stats_cache.put(-1, None)
                        st.toast("Saved to Wardrobe!")

with tab2:
    st.header("My Wardrobe Collection")
    
    with Session(engine) as session:
        items = session.exec(select(DressItem).order_by(DressItem.created_at.desc())).all()
    
    if not items:
        st.info("No items in your wardrobe yet. Go upload some!")
    else:
        # Dictionary grouping algorithm inspired by LeetCode 49 (Group Anagrams)
        # We group our items by Season. We use cache to not re-compute unless invalidated.
        cached_stats = st.session_state.stats_cache.get(len(items))
        if not cached_stats:
            season_groups = collections.defaultdict(list)
            for item in items:
                season_groups[item.season].append(item)
            st.session_state.stats_cache.put(len(items), season_groups)
        else:
            season_groups = cached_stats
            
        st.subheader("Filter by Season")
        selected_season = st.selectbox("Season", ["All"] + list(season_groups.keys()))
        
        display_items = items if selected_season == "All" else season_groups[selected_season]

        # Display items in a grid layout (4 columns)
        cols = st.columns(4)
        for index, item in enumerate(display_items):
            col = cols[index % 4]
            with col:
                st.container(border=True)
                try:
                    img = Image.open(item.image_path)
                    st.image(img, use_column_width=True)
                except Exception:
                    st.warning("Image file missing")
                    
                st.markdown(f"**Season:** {item.season}")
                st.markdown(f"**Style:** {item.style}")
                st.markdown(f"**Color:** {item.color}")
                st.caption(f"Added: {item.created_at.strftime('%Y-%m-%d')}")

with tab3:
    st.header("📚 About: DSA Concepts Inside")
    st.markdown('''
This project is built using modern full-stack methodologies and applies pure Data Structures and Algorithms (DSA). Below are the DSA concepts integrated into this app.

### 1. LRU Cache (Least Recently Used)
- **Inspired By**: [LeetCode 146: LRU Cache](https://leetcode.com/problems/lru-cache/)
- **Usage Here**: When computing the grouped wardrobe statistics and aggregations (e.g. gathering all Summer clothes vs. Winter clothes), iterating over the database items could be slow at a large scale. The `WardrobeCache` class utilizes Python's `collections.OrderedDict` to maintain an $O(1)$ time complexity for fetching and invalidating the most recent computations based on the total clothes count. 
    
### 2. Grouping by Hash Map
- **Inspired By**: [LeetCode 49: Group Anagrams](https://leetcode.com/problems/group-anagrams/)
- **Usage Here**: In the "My Wardrobe" tab, when filtering clothes by season, the application parses the 1D list of SQL models and groups the strings into a `collections.defaultdict(list)`. This $O(N)$ algorithm effectively organizes the dataset under hash keys (`Summer`, `Winter`, etc.) mapped to lists of elements.

### 3. $O(1)$ Array Indexing via Modulo
- **Inspired By**: Basic Array Manipulation and Circular Buffers.
- **Usage Here**: Streamlit’s column layout renders elements sequentially by accessing static columns utilizing the modulo operator (`col = cols[index % 4]`). This allows an unbounded collection of elements to wrap dynamically across fixed 4 columns at run-time without requiring nested iterative grouping logic.
    ''')
