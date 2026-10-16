// Subprocess-only test preload. Never imported by production CLI code.
// Public requests return fixtures; every other external hostname is rejected.
const nativeFetch = globalThis.fetch;
globalThis.fetch = (async (input: RequestInfo | URL, init?: RequestInit) => {
  const url = new URL(input instanceof Request ? input.url : String(input));
  if (["127.0.0.1", "localhost", "[::1]"].includes(url.hostname)) {
    return nativeFetch(input, init);
  }
  if (url.hostname === "www.linkedin.com") return new Response("", { status: 200 });
  throw new Error(`External network disabled in CLI tests: ${url.hostname}`);
}) as typeof fetch;
