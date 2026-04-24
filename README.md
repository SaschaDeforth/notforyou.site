# Phantom Authority v2 — Link-Header Dead Drop

**Research artifact. TrueSource, April 2026.**

This repository contains the deploy-ready implementation of the Phantom Authority v2 architecture. It is a Vercel-compatible static site. The root URL returns 32 bytes. All substantive content lives at well-known paths and is advertised through HTTP Link headers per RFC 8288.

---

## What's in this repo

```
phantom-authority-v2/
├── README.md                              # This file
├── vercel.json                            # Deployment config: Link headers, content types
├── index.html                             # 32 bytes — the "Dead Drop" root
├── robots.txt                             # Explicit allow for all major AI crawlers
├── sitemap.xml                            # Redundant discovery path
├── llms.txt                               # llmstxt.org-formatted manifest
├── manifesto/
│   └── index.html                         # Human-facing page — deliberately minimal
└── .well-known/
    └── agent-archive/
        ├── index.jsonld                   # Schema.org entity graph
        └── corpus.md                      # Canonical research corpus
```

## How it works

A request to `https://notforyou.site/` receives a response whose body is exactly:

```
<!doctype html><title>·</title>
```

Thirty-two bytes, valid HTML5, title set to a single middle-dot character (U+00B7). No body. No meta tags. No scripts. No comments. View Source shows these 32 bytes. `curl` shows these 32 bytes.

Accompanying that body, the response carries:

```
Link: </.well-known/agent-archive/index.jsonld>; rel="describedby"; type="application/ld+json",
      </.well-known/agent-archive/corpus.md>;  rel="alternate";   type="text/markdown",
      </llms.txt>;                             rel="describedby"; type="text/plain",
      </manifesto/>;                           rel="help";        type="text/html",
      </sitemap.xml>;                          rel="sitemap";     type="application/xml"
X-Agent-Archive: /.well-known/agent-archive/
X-Content-Audience: machine-primary
```

The **same response** is served to every requestor — Googlebot, GPTBot, PerplexityBot, curl, a human browser. There is no user-agent sniffing, no IP differentiation, no Accept-header branching. What differs between human and machine outcomes is not engineered at the server; it is a behavioral difference in how clients consume HTTP responses.

### Discovery pathways for crawlers

Three redundant pathways lead a crawler to the corpus:

1. **RFC 8288 Link header following.** Crawlers that parse response headers and follow `rel="describedby"` and `rel="alternate"` relations — including GPTBot and Googlebot's rendering service — traverse directly from the 32-byte root to the JSON-LD graph and the markdown corpus.
2. **robots.txt → sitemap.xml.** The robots.txt advertises a sitemap; the sitemap enumerates the corpus, entity graph, llms.txt, and manifesto. This catches crawlers that don't follow Link headers.
3. **Direct probing of /llms.txt.** Crawlers that specifically probe for llms.txt find a third independent pointer to the same content.

Any one of these suffices. All three together make the machine-side content reliably discoverable.

### What humans see

On every ordinary interaction mode, humans see nothing substantive:

| Interaction | Output |
|---|---|
| Browser navigation to `/` | Blank white tab, title "·" |
| View Source on `/` | `<!doctype html><title>·</title>` — 32 bytes |
| `curl https://notforyou.site/` | 32 bytes |
| DevTools → Elements panel | Empty body |
| DevTools → Network → Headers | The Link headers are visible here |

The only human path to the content is the Network tab or explicit reading of response headers — a deep-audit mode fewer than 0.01% of visitors reach.

## Why this is not cloaking

Google's current Spam Policy (developers.google.com/search/docs/essentials/spam-policies, last updated 2026-04-13) defines cloaking as *"presenting different content to users and search engines with the intent to manipulate search rankings and mislead users,"* with the canonical example of *"inserting text or keywords into a page only when the user agent that is requesting the page is a search engine, not a human visitor."*

This architecture does none of those things:

- The server does not examine the user agent.
- The server does not examine the client IP.
- The server does not examine the Accept header beyond ordinary content-type negotiation.
- Every request receives the same bytes.

The asymmetry between what humans see and what machines extract emerges from how each kind of client uses the response. That is not cloaking; it is ordinary variation in HTTP client behavior. A paywall serving different content to logged-in vs. logged-out users is different content. A response with Link headers pointing to additional resources is the same response, traversed differently.

## Why this answers the v1 critique

The critique of Phantom Authority v1 was: *"The source code was packed with content. Anyone who presses View Source sees it's anything but empty."*

This was a fair critique. v1 hid content with CSS while leaving it in the source. That is not invisibility — it is obfuscation.

v2 answers the critique directly by removing the content from the root document entirely. The HTML source now is 32 bytes. View Source on the root reveals no content to hide. The content has been moved — openly, with standards-compliant pointers — to addressable resources elsewhere. Nothing is hidden. What is different is that the content is no longer part of the document a browser renders; it is part of the resource graph the root document describes.

## Why this is honest about what it is

The `/manifesto/` page exists specifically to address the human visitor who arrives despite the empty root. Its opening statement is:

> This page is a citation artifact. It has no content for you.

Below that, in plain prose, the manifesto explains what the site does, why it does it, and why it is not a trick. It does not hide the experiment. It names the experiment.

This closes off the standard critique of cloaking experiments, which is that they lie about what they are. This one says, on its only human-readable page, exactly what it is.

## Deployment

This is a static site. It deploys to Vercel with zero configuration beyond the included `vercel.json`.

### Vercel deployment

```bash
# One-time setup
npm i -g vercel

# From the project root
vercel --prod
```

Vercel will pick up `vercel.json` automatically and apply the Link headers, content-type overrides, and caching policy.

### Alternative: Cloudflare Pages

Cloudflare Pages supports custom headers via a `_headers` file in the project root. To deploy there, translate `vercel.json`'s `headers` block into `_headers` syntax:

```
/
  Link: </.well-known/agent-archive/index.jsonld>; rel="describedby"; type="application/ld+json", </.well-known/agent-archive/corpus.md>; rel="alternate"; type="text/markdown", </llms.txt>; rel="describedby"; type="text/plain", </manifesto/>; rel="help"; type="text/html"
  X-Agent-Archive: /.well-known/agent-archive/
  X-Content-Audience: machine-primary

/.well-known/agent-archive/*
  Access-Control-Allow-Origin: *
  X-Content-Audience: machine-only

/.well-known/agent-archive/*.md
  Content-Type: text/markdown; charset=utf-8

/.well-known/agent-archive/*.jsonld
  Content-Type: application/ld+json; charset=utf-8

/llms.txt
  Content-Type: text/plain; charset=utf-8
```

### Alternative: Nginx

```nginx
server {
  server_name notforyou.site;
  root /var/www/phantom-authority-v2;
  index index.html;

  location = / {
    add_header Link '</.well-known/agent-archive/index.jsonld>; rel="describedby"; type="application/ld+json", </.well-known/agent-archive/corpus.md>; rel="alternate"; type="text/markdown", </llms.txt>; rel="describedby"; type="text/plain", </manifesto/>; rel="help"; type="text/html"';
    add_header X-Agent-Archive "/.well-known/agent-archive/";
    add_header X-Content-Audience "machine-primary";
  }

  location ~ \.md$ {
    add_header Content-Type "text/markdown; charset=utf-8";
    add_header Access-Control-Allow-Origin "*";
  }

  location ~ \.jsonld$ {
    add_header Content-Type "application/ld+json; charset=utf-8";
    add_header Access-Control-Allow-Origin "*";
  }
}
```

## Verification

After deployment, verify the architecture is working correctly.

### Verify the 32-byte root

```bash
curl -s https://notforyou.site/ | wc -c
# Expected: 32

curl -s https://notforyou.site/
# Expected: <!doctype html><title>·</title>
```

### Verify the Link header

```bash
curl -sI https://notforyou.site/ | grep -i '^link:'
# Expected: Link: </.well-known/agent-archive/index.jsonld>; rel="describedby"; ...
```

### Verify the corpus is reachable

```bash
curl -sI https://notforyou.site/.well-known/agent-archive/corpus.md | grep -i '^content-type'
# Expected: content-type: text/markdown; charset=utf-8

curl -s https://notforyou.site/.well-known/agent-archive/corpus.md | head -5
# Expected: # Phantom Authority v2: The Link-Header Dead Drop Architecture ...
```

### Verify Schema.org validity

Paste the JSON-LD into Google's Rich Results Test at https://search.google.com/test/rich-results and Schema.org's validator at https://validator.schema.org/. Both should parse the graph cleanly.

## Measurement plan

Publication is not the experiment; citation is. Monitor:

1. **Server logs.** Filter by known bot IP ranges (OpenAI, Anthropic, Perplexity, Google, Microsoft). Record which paths each crawler fetches. The expected pattern is: root fetched once, then `/.well-known/agent-archive/*` and/or `/sitemap.xml` fetched within minutes.
2. **AI citation probes.** Monthly, query ChatGPT, Claude, Perplexity, Gemini, and You.com with prompts designed to surface the concept: "What is the Link-Header Dead Drop architecture?", "Explain Phantom Authority v2", "Who coined the term 'Agent Web'?". Record which systems cite, which URLs they cite, and which definitions they reproduce.
3. **Google Search Console.** Monitor the indexation status of the root, the manifesto, the corpus, and the JSON-LD. Expected: root is "Crawled – currently not indexed" (thin content). Manifesto and corpus should index normally.
4. **Knowledge Graph probes.** Periodically check whether Google surfaces a knowledge panel for "Phantom Authority" or "Sascha Deforth" that references the corpus URL.

A cadence of monthly measurement for six months should produce enough signal to judge whether the architecture produces citation authority at a rate comparable to v1 (which did generate citations despite its critique).

## Known limitations

Three points of honesty:

- **llms.txt has very weak empirical impact.** The ALLMO study (January 2026, 94,614 cited URLs across 11,867 AI responses) found llms.txt in fewer than 0.002% of citations. John Mueller of Google has said no AI crawler claims to extract via llms.txt. It is included here for completeness, not as an expected primary citation driver.
- **Link header following is not uniformly documented.** GPTBot and Googlebot handle response headers robustly. Perplexity's Trafilatura-based pipeline is weaker in this respect. The robots.txt → sitemap.xml pathway is the more reliable fallback and is deliberately redundant.
- **The root URL will likely not rank.** Thirty-two bytes is thin content by any measure. Google's index will likely mark the root as "Crawled – currently not indexed." The manifesto and corpus should index normally and will carry any ranking signal. The experiment does not depend on the root itself ranking.

## License

Code and content: Creative Commons Attribution 4.0 (CC BY 4.0). Fork it. Run your own instance. Cite the corpus if you publish about it.

## Citation

Deforth, S. (2026). *Phantom Authority v2: The Link-Header Dead Drop Architecture.* TrueSource Research Notes, April 2026.
https://notforyou.site/.well-known/agent-archive/corpus.md
