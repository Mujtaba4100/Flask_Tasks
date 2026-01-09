from flask import Flask, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import string
import random
import re

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///urls.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Model
class URL(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.String(2048), nullable=False)
    short_code = db.Column(db.String(10), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    clicks = db.Column(db.Integer, default=0)
    
    def __repr__(self):
        return f'<URL {self.short_code}>'

# Create database tables
with app.app_context():
    db.create_all()

def generate_short_code(length=6):
    """Generate a random short code for the URL"""
    characters = string.ascii_letters + string.digits
    while True:
        short_code = ''.join(random.choice(characters) for _ in range(length))
        # Check if this code already exists
        if not URL.query.filter_by(short_code=short_code).first():
            return short_code

def validate_url(url):
    """Validate if the provided string is a valid URL"""
    if not url.startswith(('http://', 'https://')):
        url = 'http://' + url
    
    url_pattern = re.compile(
        r'^https?://'
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'
        r'localhost|'
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
        r'(?::\d+)?'
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    return bool(url_pattern.match(url))

def normalize_url(url):
    """Normalize URL by adding http:// if missing"""
    if not url.startswith(('http://', 'https://')):
        return 'http://' + url
    return url

@app.route('/', methods=['GET', 'POST'])
def home():
    """Home page with URL shortening form"""
    shortened_url = None
    error = None
    
    if request.method == 'POST':
        original_url = request.form.get('url', '').strip()
        
        if not original_url:
            error = "Please enter a URL"
        elif not validate_url(original_url):
            error = "Please enter a valid URL (e.g., https://example.com)"
        else:
            original_url = normalize_url(original_url)
            existing_url = URL.query.filter_by(original_url=original_url).first()
            
            if existing_url:
                short_code = existing_url.short_code
            else:
                short_code = generate_short_code()
                new_url = URL(original_url=original_url, short_code=short_code)
                db.session.add(new_url)
                db.session.commit()
            
            shortened_url = request.host_url + short_code
    
    # Simple HTML
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>URL Shortener</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                max-width: 600px;
                margin: 50px auto;
                padding: 20px;
                background: #f5f5f5;
            }}
            .container {{
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            h1 {{
                color: #333;
                text-align: center;
            }}
            form {{
                display: flex;
                gap: 10px;
                margin-bottom: 20px;
            }}
            input[type="text"] {{
                flex: 1;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 5px;
            }}
            button {{
                padding: 10px 20px;
                background: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                cursor: pointer;
            }}
            button:hover {{
                background: #45a049;
            }}
            .error {{
                color: #f44336;
                padding: 10px;
                background: #ffebee;
                border-radius: 5px;
                margin-bottom: 10px;
            }}
            .success {{
                color: #4CAF50;
                padding: 15px;
                background: #e8f5e9;
                border-radius: 5px;
                margin-bottom: 10px;
            }}
            .result {{
                background: #f9f9f9;
                padding: 20px;
                border-radius: 5px;
                margin-top: 20px;
            }}
            nav {{
                text-align: center;
                margin-top: 20px;
            }}
            nav a {{
                color: #4CAF50;
                text-decoration: none;
                margin: 0 10px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>URL Shortener</h1>
            <p style="text-align: center; color: #666;">Final Project - Innomatics Research Labs</p>
            
            {f'<div class="error">{error}</div>' if error else ''}
            {f'<div class="success">✓ Shortened URL: <strong>{shortened_url}</strong></div>' if shortened_url else ''}
            
            <form method="POST" action="/">
                <input type="text" name="url" placeholder="Enter URL (e.g., https://example.com)" required>
                <button type="submit">Shorten URL</button>
            </form>
            
            <nav>
                <a href="/history">View History</a>
            </nav>
        </div>
    </body>
    </html>
    """
    return html


@app.route('/<short_code>')
def redirect_to_url(short_code):
    """Redirect short code to original URL"""
    url = URL.query.filter_by(short_code=short_code).first()
    
    if url:
        # Increment click counter
        url.clicks += 1
        db.session.commit()
        return redirect(url.original_url)
    else:
        return "Invalid short URL", 404


@app.route('/history')
def history():
    """Show history of all shortened URLs"""
    urls = URL.query.all()
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>URL History</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                max-width: 1000px;
                margin: 50px auto;
                padding: 20px;
                background: #f5f5f5;
            }}
            .container {{
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            h1 {{
                color: #333;
                text-align: center;
            }}
            nav {{
                text-align: center;
                margin-bottom: 30px;
            }}
            nav a {{
                margin: 0 10px;
                color: #4CAF50;
                text-decoration: none;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
            }}
            th, td {{
                padding: 12px;
                text-align: left;
                border-bottom: 1px solid #ddd;
            }}
            th {{
                background: #4CAF50;
                color: white;
            }}
            tr:hover {{
                background: #f5f5f5;
            }}
            .empty {{
                text-align: center;
                padding: 40px;
                color: #666;
            }}
            a {{
                color: #4CAF50;
                text-decoration: none;
            }}
            a:hover {{
                text-decoration: underline;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <nav>
                <a href="/">Home</a>
            </nav>
            
            <h1>URL History</h1>
            <p style="text-align: center; color: #666;">All your shortened URLs</p>
    """
    
    if urls:
        html += """
            <table>
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Original URL</th>
                        <th>Short URL</th>
                        <th>Clicks</th>
                        <th>Created</th>
                    </tr>
                </thead>
                <tbody>
        """
        for i, url in enumerate(urls, 1):
            html += f"""
                    <tr>
                        <td>{i}</td>
                        <td style="max-width: 300px; overflow: hidden; text-overflow: ellipsis;">{url.original_url}</td>
                        <td><a href="/{url.short_code}" target="_blank">{request.host_url}{url.short_code}</a></td>
                        <td>{url.clicks}</td>
                        <td>{url.created_at.strftime('%Y-%m-%d %H:%M')}</td>
                    </tr>
            """
        html += """
                </tbody>
            </table>
        """
    else:
        html += """
            <div class="empty">
                <h3>No URLs yet</h3>
                <p><a href="/">Shorten your first URL</a></p>
            </div>
        """
    
    html += """
        </div>
    </body>
    </html>
    """
    return html

if __name__ == '__main__':
    print("=" * 60)
    print("🔗 URL Shortener Application Started")
    print("=" * 60)
    print("📍 Home: http://127.0.0.1:5000/")
    print("📜 History: http://127.0.0.1:5000/history")
    print("=" * 60)
    app.run(debug=True)
