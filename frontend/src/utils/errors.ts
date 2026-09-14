export function getApiErrorMessage(error: unknown): string {
  if (typeof error === "object" && error !== null && "response" in error) {
    const responseError = error as { response?: { data?: { detail?: string } } };
    return responseError.response?.data?.detail ?? "The request could not be completed.";
  }
  return "The request could not be completed.";
}
