const rawBase = import.meta.env.VITE_API_BASE || "/api";

// Normalize to avoid accidental double slashes in endpoint URLs.
export const API_BASE = rawBase.endsWith("/") ? rawBase.slice(0, -1) : rawBase;
