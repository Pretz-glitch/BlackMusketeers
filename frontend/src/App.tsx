import { useEffect, useMemo, useRef, useState } from "react";
import type { GarmentTag, OutfitSuggestion } from "./types";

const seedWardrobe: GarmentTag[] = [
  { name: "White Oxford Shirt", color: "white", fabric: "cotton", formality: "smart-casual", subcategory: "top" },
  { name: "Navy Chinos", color: "navy", fabric: "cotton", formality: "smart-casual", subcategory: "bottom" },
  { name: "Black Tee", color: "black", fabric: "jersey", formality: "casual", subcategory: "top" },
  { name: "Stone Overshirt", color: "beige", fabric: "linen", formality: "casual", subcategory: "layer" },
  { name: "White Sneakers", color: "white", fabric: "leather", formality: "casual", subcategory: "shoes" },
  { name: "Charcoal Blazer", color: "charcoal", fabric: "wool", formality: "formal", subcategory: "layer" },
  { name: "Pleated Trousers", color: "gray", fabric: "wool", formality: "formal", subcategory: "bottom" }
];

const colorPool = ["black", "white", "beige", "navy", "olive", "pink"];
const fabricPool = ["cotton", "linen", "denim", "wool", "silk"];
const formalityPool: GarmentTag["formality"][] = ["casual", "smart-casual", "formal"];
const subcategoryPool: GarmentTag["subcategory"][] = ["top", "bottom", "layer", "shoes", "dress"];

function getRandomFrom<T>(values: T[]): T {
  return values[Math.floor(Math.random() * values.length)];
}

function powerSet<T>(items: T[]): T[][] {
  const result: T[][] = [[]];
  for (const item of items) {
    const currentLength = result.length;
    for (let i = 0; i < currentLength; i += 1) {
      result.push([...result[i], item]);
    }
  }
  return result;
}

function isWearableOutfit(pieces: GarmentTag[]): boolean {
  const hasTop = pieces.some((piece) => piece.subcategory === "top");
  const hasBottom = pieces.some((piece) => piece.subcategory === "bottom");
  const hasDress = pieces.some((piece) => piece.subcategory === "dress");
  return hasDress || (hasTop && hasBottom);
}

function vibeScore(vibe: string, pieces: GarmentTag[]): number {
  const normalized = vibe.toLowerCase();
  let score = 0;

  if (normalized.includes("office") || normalized.includes("formal")) {
    score += pieces.filter((piece) => piece.formality !== "casual").length * 2;
  }
  if (normalized.includes("bright") || normalized.includes("summer")) {
    score += pieces.filter((piece) => ["white", "beige", "pink"].includes(piece.color)).length * 2;
  }
  if (normalized.includes("street") || normalized.includes("casual")) {
    score += pieces.filter((piece) => piece.formality === "casual").length * 2;
  }

  score += pieces.some((piece) => piece.subcategory === "layer") ? 1 : 0;
  score += pieces.some((piece) => piece.subcategory === "shoes") ? 1 : 0;

  return score;
}

function buildReason(vibe: string, pieces: GarmentTag[]): string {
  const colors = Array.from(new Set(pieces.map((piece) => piece.color))).join(", ");
  const formalMix = Array.from(new Set(pieces.map((piece) => piece.formality))).join(" + ");
  return `Matches ${vibe} using a ${colors} palette with a ${formalMix} balance.`;
}

function mockTagGarment(): GarmentTag {
  return {
    name: "Captured Garment",
    color: getRandomFrom(colorPool),
    fabric: getRandomFrom(fabricPool),
    formality: getRandomFrom(formalityPool),
    subcategory: getRandomFrom(subcategoryPool)
  };
}

export default function App() {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [cameraOn, setCameraOn] = useState(false);
  const [isTagging, setIsTagging] = useState(false);
  const [taggedGarment, setTaggedGarment] = useState<GarmentTag | null>(null);
  const [vibe, setVibe] = useState("Office Casual");
  const [suggestions, setSuggestions] = useState<OutfitSuggestion[]>([]);

  const wardrobe = useMemo(
    () => (taggedGarment ? [...seedWardrobe, taggedGarment] : seedWardrobe),
    [taggedGarment]
  );

  useEffect(() => {
    return () => {
      if (streamRef.current) {
        streamRef.current.getTracks().forEach((track) => track.stop());
      }
    };
  }, []);

  async function startCamera() {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" }, audio: false });
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
      setCameraOn(true);
    } catch {
      setCameraOn(false);
      alert("Camera access failed. You can still upload a photo.");
    }
  }

  function stopCamera() {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
    setCameraOn(false);
  }

  function captureFrame() {
    if (!videoRef.current) {
      return;
    }
    const canvas = document.createElement("canvas");
    canvas.width = videoRef.current.videoWidth;
    canvas.height = videoRef.current.videoHeight;
    const context = canvas.getContext("2d");
    if (!context) {
      return;
    }
    context.drawImage(videoRef.current, 0, 0, canvas.width, canvas.height);
    setPreviewUrl(canvas.toDataURL("image/jpeg", 0.9));
  }

  function onUpload(event: React.ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) {
      return;
    }
    const nextUrl = URL.createObjectURL(file);
    setPreviewUrl(nextUrl);
  }

  async function tagCurrentImage() {
    if (!previewUrl) {
      return;
    }
    setIsTagging(true);

    // Mocked AI tagging for now. Replace with POST /tag when backend is ready.
    await new Promise((resolve) => setTimeout(resolve, 700));
    setTaggedGarment(mockTagGarment());

    setIsTagging(false);
  }

  function generateSuggestions() {
    // LeetCode 78 concept: enumerate subsets, then filter and rank.
    const candidates = powerSet(wardrobe)
      .filter((subset) => subset.length >= 2 && subset.length <= 4)
      .filter(isWearableOutfit)
      .map((subset, idx) => {
        const score = vibeScore(vibe, subset);
        return {
          id: `look-${idx}`,
          title: `Look ${idx + 1}`,
          pieces: subset,
          reason: buildReason(vibe, subset),
          vibeScore: score
        };
      })
      .sort((a, b) => b.vibeScore - a.vibeScore)
      .slice(0, 5);

    setSuggestions(candidates);
  }

  return (
    <div className="page-shell">
      <header className="hero">
        <p className="eyebrow">BlackMusketeers</p>
        <h1>Snap. Tag. Style.</h1>
        <p>
          Capture a garment, let AI extract attributes, then browse vibe-matched outfits generated with subset logic.
        </p>
      </header>

      <main className="grid-layout">
        <section className="card capture-card">
          <h2>Capture Studio</h2>
          <div className="camera-frame">
            {cameraOn ? (
              <video ref={videoRef} autoPlay playsInline muted />
            ) : previewUrl ? (
              <img src={previewUrl} alt="Selected garment" />
            ) : (
              <div className="placeholder">No image yet. Open camera or upload a photo.</div>
            )}
          </div>

          <div className="actions">
            {!cameraOn ? (
              <button onClick={startCamera}>Open Camera</button>
            ) : (
              <button onClick={stopCamera} className="secondary">
                Stop Camera
              </button>
            )}
            <button onClick={captureFrame} disabled={!cameraOn}>
              Snap Photo
            </button>
            <button onClick={() => fileInputRef.current?.click()} className="secondary">
              Upload
            </button>
            <button onClick={tagCurrentImage} disabled={!previewUrl || isTagging}>
              {isTagging ? "Tagging..." : "Tag Garment"}
            </button>
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              onChange={onUpload}
              hidden
            />
          </div>
        </section>

        <section className="card tags-card">
          <h2>Tagged Result</h2>
          {taggedGarment ? (
            <div className="tag-grid">
              <div><span>Name</span><strong>{taggedGarment.name}</strong></div>
              <div><span>Color</span><strong>{taggedGarment.color}</strong></div>
              <div><span>Fabric</span><strong>{taggedGarment.fabric}</strong></div>
              <div><span>Formality</span><strong>{taggedGarment.formality}</strong></div>
              <div><span>Subcategory</span><strong>{taggedGarment.subcategory}</strong></div>
            </div>
          ) : (
            <p className="helper">Tag any captured/uploaded garment to view structured attributes here.</p>
          )}

          <div className="vibe-row">
            <label htmlFor="vibe">Vibe</label>
            <input
              id="vibe"
              value={vibe}
              onChange={(event) => setVibe(event.target.value)}
              placeholder="Office Casual"
            />
            <button onClick={generateSuggestions}>Generate Outfits</button>
          </div>
        </section>

        <section className="card suggestions-card">
          <h2>Stylist Suggestions</h2>
          {suggestions.length === 0 ? (
            <p className="helper">Generate outfits to browse 3-5 ranked combinations.</p>
          ) : (
            <div className="suggestions-strip">
              {suggestions.map((suggestion) => (
                <article key={suggestion.id} className="look-card">
                  <h3>{suggestion.title}</h3>
                  <p className="score">Vibe score: {suggestion.vibeScore}</p>
                  <ul>
                    {suggestion.pieces.map((piece) => (
                      <li key={`${suggestion.id}-${piece.name}`}>
                        {piece.name} ({piece.color}, {piece.subcategory})
                      </li>
                    ))}
                  </ul>
                  <p>{suggestion.reason}</p>
                </article>
              ))}
            </div>
          )}
        </section>
      </main>
    </div>
  );
}
