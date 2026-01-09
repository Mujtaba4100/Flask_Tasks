from flask import Flask, request

app = Flask(__name__)

@app.route('/')
def home():
    """
    Home page:
    - Reads 'name' from the URL query
    - Shows instructions if no name is provided
    - Displays the name in UPPERCASE if provided
    """

    name = request.args.get('name', '').strip()

    if not name:
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Uppercase Name Converter</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    max-width: 600px;
                    margin: 50px auto;
                    padding: 20px;
                    text-align: center;
                }
                h1 { color: #333; }
                p { font-size: 1.1em; }
                .example {
                    background: #f2f2f2;
                    padding: 15px;
                    border-radius: 6px;
                    margin-top: 25px;
                }
                code {
                    background: #e0e0e0;
                    padding: 6px 10px;
                    border-radius: 4px;
                    font-size: 1em;
                }
            </style>
        </head>
        <body>
            <h1>Uppercase Name Converter 🔤</h1>
            <p>Just add your name in the URL to see it in uppercase.</p>

            <div class="example">
                <strong>Example:</strong><br><br>
                <code>http://127.0.0.1:5000/?name=hamza</code>
            </div>
        </body>
        </html>
        """
    
    uppercase_name = name.upper()

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Your Name in Uppercase</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                max-width: 600px;
                margin: 50px auto;
                padding: 20px;
                text-align: center;
            }}
            h1 {{ color: #333; }}
            .result {{
                background: #4CAF50;
                color: white;
                padding: 30px;
                border-radius: 10px;
                margin: 30px 0;
                font-size: 2em;
                font-weight: bold;
                letter-spacing: 3px;
            }}
            a {{
                display: inline-block;
                margin-top: 20px;
                padding: 10px 22px;
                background: #333;
                color: white;
                text-decoration: none;
                border-radius: 5px;
            }}
            a:hover {{ background: #555; }}
        </style>
    </head>
    <body>
        <h1>Your Name in Uppercase 🎉</h1>
        <div class="result">{uppercase_name}</div>
        <a href="/">Try another name</a>
    </body>
    </html>
    """

if __name__ == '__main__':
    print("🚀 Flask app is running...")
    print("👉 Open: http://127.0.0.1:5000/?name=YourName")
    app.run(debug=True, host='0.0.0.0', port=5000)
