function required(
  name: "VITE_API_BASE_URL" | "VITE_SUPABASE_URL" | "VITE_SUPABASE_ANON_KEY",
): string {
  const value = import.meta.env[name];
  if (typeof value !== "string" || value.trim() === "") {
    throw new Error(`Missing required env: ${name}`);
  }
  return value;
}

export const env = {
  apiBaseUrl: required("VITE_API_BASE_URL"),
  supabaseUrl: required("VITE_SUPABASE_URL"),
  supabaseAnonKey: required("VITE_SUPABASE_ANON_KEY"),
} as const;
