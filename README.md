## The Vision
Most outfit pickers require tedious manual entry. **BlackMusketeers** flips the script:
1. **Snap a photo** of a garment.
2. **AI tags it** (Vision API) with fabric, color, sub-culture, and formality.
3. **The Stylist Engine** (LLM) suggests outfits based on vibes such as *Office Casual*, *Bright*, and *Pink*.

Based on Praanesh's quote:

> "I have so many clothes but nothing to wear"
>
> - Praanesh Balakrishnan Nair, circa October 2025

## Tech Stack

### Frontend
- React + Vite
- Bun (package manager + runtime for scripts)
- TypeScript
- Modern CSS (custom design system variables and responsive layout)

### Backend (planned)
- FastAPI (Python)
- Endpoints:
	- `POST /tag`: accepts image upload and returns structured garment attributes
	- `POST /suggest`: accepts wardrobe JSON + vibe string and returns outfit combinations

### AI Layer (planned)
- Vision model call (GPT-4o or Claude) for garment extraction:
	- color
	- fabric
	- formality
	- subcategory
- LLM stylist prompt that takes:
	- tagged wardrobe JSON
	- vibe string (example: `Office Casual`)
	- subset-based combination logic
	- output: 3-5 outfit suggestions with concise reasoning

## Subset Concept (LeetCode 78)
Outfit generation uses the same idea as LeetCode problem 78 (Subsets / Power Set).

Given a list of wardrobe items, generate all possible non-duplicate subsets, then filter by style constraints (occasion, vibe, color harmony, formality).

Reference problem:
- Input: `nums = [1,2,3]`
- Output: `[[],[1],[2],[1,2],[3],[1,3],[2,3],[1,2,3]]`

How it maps to this project:
1. Convert tagged garments into a normalized list.
2. Generate candidate subsets.
3. Keep only wearable outfit structures (top + bottom, optional layer, optional shoes).
4. Score by vibe match and reasoning quality.
5. Return top 3-5 suggestions.

## Current Status
- README and frontend foundation added first.
- Backend and AI integration will plug into this UI next.