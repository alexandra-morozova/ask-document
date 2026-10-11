export function isAllowedEmail(email: string, domain: string | null): boolean {
  if (domain === null) {
    return true;
  }
  return email.trim().toLowerCase().endsWith(`@${domain}`);
}
