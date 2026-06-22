#!/usr/bin/env python3
"""
Static file server + API
  GET /api/chapters        → 챕터 목록 JSON
  GET /api/chapter/<n>     → chapter<n>.md 파싱 JSON
  GET /tts?text=&gender=   → Microsoft Edge TTS 프록시
"""
import http.server
import urllib.parse
import asyncio
import io
import os
import json
import re
import glob
import edge_tts

PORT = 7823
DIRECTORY = os.path.dirname(os.path.abspath(__file__))
CHAPTERS_DIR = os.path.join(DIRECTORY, 'chapters')

VOICES = {
    'female': 'ka-GE-EkaNeural',
    'male':   'ka-GE-GiorgiNeural',
    'ko':     'ko-KR-SunHiNeural',
}


# ── MD 파서 ──────────────────────────────────────
def parse_chapter_md(path: str) -> dict:
    with open(path, encoding='utf-8') as f:
        lines = f.readlines()

    title = ''
    cards = []
    current_cat = ''

    for line in lines:
        line = line.rstrip('\n')
        if line.startswith('# '):
            title = line[2:].strip()
        elif line.startswith('## '):
            current_cat = line[3:].strip()
        elif '=' in line and not line.startswith('#'):
            parts = line.split('=', 1)
            geo = parts[0].strip()
            ko  = parts[1].strip()
            if geo and ko:
                cards.append({'geo': geo, 'ko': ko, 'cat': current_cat})

    return {'title': title, 'cards': cards}


def get_chapter_list() -> list:
    files = sorted(glob.glob(os.path.join(CHAPTERS_DIR, 'chapter*.md')))
    result = []
    for path in files:
        m = re.search(r'chapter(\d+)\.md$', path)
        if not m:
            continue
        num = int(m.group(1))
        data = parse_chapter_md(path)
        result.append({'num': num, 'title': data['title'], 'count': len(data['cards'])})
    return result


# ── TTS ──────────────────────────────────────────
async def synthesize(text: str, voice: str) -> bytes:
    buf = io.BytesIO()
    communicate = edge_tts.Communicate(text, voice)
    async for chunk in communicate.stream():
        if chunk['type'] == 'audio':
            buf.write(chunk['data'])
    return buf.getvalue()


# ── HTTP 핸들러 ───────────────────────────────────
class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path   = parsed.path
        params = urllib.parse.parse_qs(parsed.query)

        # GET /api/chapters
        if path == '/api/chapters':
            self.send_json(get_chapter_list())

        # GET /api/chapter/<n>
        elif path.startswith('/api/chapter/'):
            num_str = path.split('/')[-1]
            md_path = os.path.join(CHAPTERS_DIR, f'chapter{num_str}.md')
            if not os.path.isfile(md_path):
                self.send_json({'error': 'not found'}, 404)
            else:
                self.send_json(parse_chapter_md(md_path))

        # GET /tts
        elif path == '/tts':
            text   = params.get('text',   [''])[0].strip()
            lang   = params.get('lang',   [''])[0]
            if lang == 'ko':
                voice = VOICES['ko']
            else:
                gender = params.get('gender', ['female'])[0]
                voice  = VOICES.get(gender, VOICES['female'])

            if not text:
                self.send_error(400, 'text required')
                return
            try:
                audio = asyncio.run(synthesize(text, voice))
                self.send_response(200)
                self.send_header('Content-Type', 'audio/mpeg')
                self.send_header('Content-Length', str(len(audio)))
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Cache-Control', 'public, max-age=86400')
                self.end_headers()
                self.wfile.write(audio)
            except Exception as e:
                self.send_error(502, str(e))

        else:
            super().do_GET()

    def log_message(self, fmt, *args):
        pass


if __name__ == '__main__':
    with http.server.ThreadingHTTPServer(('', PORT), Handler) as httpd:
        print(f'서버 시작: http://localhost:{PORT}')
        httpd.serve_forever()
