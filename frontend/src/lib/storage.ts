export function getSavedReport(): any | null {
  if (typeof window === "undefined") return null;
  try {
    const data = localStorage.getItem("latest_report");
    if (!data || data === "undefined" || data === "null") return null;
    return JSON.parse(data);
  } catch {
    return null;
  }
}
