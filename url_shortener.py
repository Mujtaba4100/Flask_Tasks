from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import string
import random
from urllib.parse import urlparse
import re

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here-change-in-production'
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
    # Add http:// if no scheme is provided
    if not url.startswith(('http://', 'https://')):
        url = 'http://' + url
    
    # Basic URL pattern validation
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # or IP
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    if url_pattern.match(url):
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False
    return False

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
            # Normalize the URL
            original_url = normalize_url(original_url)
            
            # Check if URL already exists in database
            existing_url = URL.query.filter_by(original_url=original_url).first()
            
            if existing_url:
                # URL already shortened, return existing short code
                short_code = existing_url.short_code
            else:
                # Generate new short code and save to database
                short_code = generate_short_code()
                new_url = URL(original_url=original_url, short_code=short_code)
                db.session.add(new_url)
                db.session.commit()
            
            # Create the shortened URL
            shortened_url = request.host_url + short_code
    
    return render_template('url_home.html', shortened_url=shortened_url, error=error)

@app.route('/history')
def history():
    """History page showing all shortened URLs"""
    urls = URL.query.order_by(URL.created_at.desc()).all()
    return render_template('url_history.html', urls=urls, host_url=request.host_url)

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
        flash('Invalid short URL', 'error')
        return redirect(url_for('home'))

@app.route('/api/stats/<short_code>')
def get_stats(short_code):
    """Get statistics for a shortened URL"""
    url = URL.query.filter_by(short_code=short_code).first()
    if url:
        return jsonify({
            'short_code': url.short_code,
            'original_url': url.original_url,
            'clicks': url.clicks,
            'created_at': url.created_at.strftime('%Y-%m-%d %H:%M:%S')
        })
    return jsonify({'error': 'URL not found'}), 404

@app.route('/delete/<int:id>', methods=['POST'])
def delete_url(id):
    """Delete a URL from history"""
    url = URL.query.get_or_404(id)
    db.session.delete(url)
    db.session.commit()
    flash('URL deleted successfully', 'success')
    return redirect(url_for('history'))

if __name__ == '__main__':
    print("=" * 60)
    print("🔗 URL Shortener Application Started")
    print("=" * 60)
    print("📍 Home: http://127.0.0.1:5000/")
    print("📜 History: http://127.0.0.1:5000/history")
    print("=" * 60)
    app.run(debug=True)
