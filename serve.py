#!/usr/bin/env python3
"""
notforyou.site — Link-Header Dead Drop Local Server
Simulates Vercel's header injection for local development.
"""
import http.server
import os

PORT = 8787
DIR = os.path.dirname(os.path.abspath(__file__))

class DeadDropHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIR, **kwargs)

    def guess_type(self, path):
        if path.endswith('.jsonld'):
            return 'application/ld+json; charset=utf-8'
        if path.endswith('.md'):
            return 'text/markdown; charset=utf-8'
        return super().guess_type(path)

    def end_headers(self):
        path = self.path.rstrip('/')

        # Root: Link-Header Dead Drop
        if path == '' or path == '/index.html':
            self.send_header("Link",
                '</.well-known/agent-archive/index.jsonld>; rel="describedby"; type="application/ld+json", '
                '</.well-known/agent-archive/corpus.md>; rel="alternate"; type="text/markdown"; hreflang="en", '
                '</llms.txt>; rel="describedby"; type="text/plain", '
                '</manifesto/>; rel="help"; type="text/html", '
                '</sitemap.xml>; rel="sitemap"; type="application/xml"'
            )
            self.send_header("X-Agent-Archive", "/.well-known/agent-archive/")
            self.send_header("X-Content-Audience", "machine-primary")
            self.send_header("X-Robots-Tag", "index, follow, max-snippet:-1, max-image-preview:large")
            self.send_header("Cache-Control", "public, max-age=3600, must-revalidate")
            self.send_header("X-Ghost-Note", "54686520414920697320746865206f627365727665722e20596f752061726520746865206578706572696d656e742e")

        # Agent archive: CORS + machine-only
        if '/.well-known/agent-archive/' in self.path:
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("X-Content-Audience", "machine-only")
            self.send_header("Cache-Control", "public, max-age=3600, must-revalidate")

        # llms.txt: CORS
        if path == '/llms.txt':
            self.send_header("Access-Control-Allow-Origin", "*")

        super().end_headers()

print(f"""
╔═══════════════════════════════════════════════════════════════╗
║  👻 notforyou.site — Link-Header Dead Drop (Local)           ║
║                                                               ║
║  Root (32 bytes):  http://localhost:{PORT}/                    ║
║  Manifesto:        http://localhost:{PORT}/manifesto/          ║
║  Corpus:           http://localhost:{PORT}/.well-known/agent-archive/corpus.md  ║
║  Entity Graph:     http://localhost:{PORT}/.well-known/agent-archive/index.jsonld ║
║  llms.txt:         http://localhost:{PORT}/llms.txt            ║
║  robots.txt:       http://localhost:{PORT}/robots.txt          ║
║  sitemap.xml:      http://localhost:{PORT}/sitemap.xml         ║
║                                                               ║
║  Press Ctrl+C to stop                                         ║
╚═══════════════════════════════════════════════════════════════╝
""")

with http.server.HTTPServer(("", PORT), DeadDropHandler) as httpd:
    httpd.serve_forever()
