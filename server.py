import json
import os
import smtplib
import ssl
import traceback
from email.message import EmailMessage
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent


def load_env(path: Path):
    if not path.exists():
        return {}
    values = {}
    for line in path.read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        key, value = line.split('=', 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


ENV = load_env(ROOT / '.env')
for key, value in ENV.items():
    os.environ.setdefault(key, value)


class Handler(BaseHTTPRequestHandler):
    def _send_json(self, payload, status=200):
        body = json.dumps(payload).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(body)

    def _serve_static(self, path):
        if path in ('/', '/index.html'):
            file_path = ROOT / 'index.html'
        else:
            file_path = ROOT / path.lstrip('/')

        if not file_path.exists() or not file_path.is_file():
            self._send_json({'success': False, 'message': 'Not found.'}, 404)
            return

        content = file_path.read_bytes()
        self.send_response(200)
        self.send_header('Content-Type', self._guess_mime(path))
        self.send_header('Content-Length', str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def _guess_mime(self, path):
        if path.endswith('.html'):
            return 'text/html; charset=utf-8'
        if path.endswith('.css'):
            return 'text/css; charset=utf-8'
        if path.endswith('.js'):
            return 'application/javascript; charset=utf-8'
        if path.endswith('.json'):
            return 'application/json; charset=utf-8'
        if path.endswith('.pdf'):
            return 'application/pdf'
        return 'text/plain; charset=utf-8'

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path.startswith('/api/'):
            self._send_json({'success': False, 'message': 'Use POST for this endpoint.'}, 405)
            return
        self._serve_static(parsed.path)

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path != '/api/contact':
            self._send_json({'success': False, 'message': 'Endpoint not found.'}, 404)
            return

        length = int(self.headers.get('Content-Length', '0'))
        body = self.rfile.read(length).decode('utf-8')
        print('DEBUG headers:', dict(self.headers))
        print('DEBUG body:', repr(body))

        try:
            payload = json.loads(body or '{}')
        except json.JSONDecodeError:
            payload = {}
        print('DEBUG payload:', payload)

        name = (payload.get('name') or '').strip()
        email = (payload.get('email') or '').strip()
        message = (payload.get('message') or '').strip()

        if not name or not email or not message:
            self._send_json({'success': False, 'message': 'Please fill in all fields.'}, 400)
            return

        gmail_user = os.getenv('GMAIL_USER', '').strip()
        gmail_password = os.getenv('GMAIL_APP_PASSWORD', '').strip()
        recipient = os.getenv('CONTACT_EMAIL', gmail_user).strip()

        email_configured = (
            gmail_user
            and gmail_password
            and gmail_user != 'your_email@gmail.com'
            and gmail_password != 'your_gmail_app_password'
        )

        if not email_configured:
            log_file = ROOT / 'contact-messages.log'
            log_file.parent.mkdir(parents=True, exist_ok=True)
            entry = {
                'name': name,
                'email': email,
                'message': message,
            }
            with log_file.open('a', encoding='utf-8') as f:
                f.write(json.dumps(entry, ensure_ascii=False) + '\n')

            self._send_json({
                'success': True,
                'message': 'Message received. Email is not configured, so the message was logged locally.'
            })
            return

        try:
            msg = EmailMessage()
            msg['Subject'] = f'New message from {name}'
            msg['From'] = gmail_user
            msg['To'] = recipient
            msg['Reply-To'] = email
            msg.set_content(f'You received a new message from your portfolio website:Name: {name}Email: {email}Message:{message}')

            context = ssl.create_default_context()
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls(context=context)
                server.login(gmail_user, gmail_password)
                server.send_message(msg)

            self._send_json({'success': True, 'message': 'Message sent successfully.'})
        except Exception as exc:
            traceback.print_exc()
            self._send_json({'success': False, 'message': f'Failed to send message: {exc}'}, 500)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()


if __name__ == '__main__':
    port = int(os.getenv('PORT', '8000'))
    server = ThreadingHTTPServer(('0.0.0.0', port), Handler)
    print(f'Serving portfolio on http://localhost:{port}')
    server.serve_forever()
