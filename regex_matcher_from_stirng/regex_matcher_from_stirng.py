from flask import Flask, request
import re

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    """Regex matcher - takes test string and regex pattern, displays all matches"""
    
    # Initialize variables
    matches = []
    error = None
    test_string = ''
    regex_pattern = ''
    
    # Handle form submission
    if request.method == 'POST':
        test_string = request.form.get('test_string', '')
        regex_pattern = request.form.get('regex_pattern', '')
        
        if test_string and regex_pattern:
            try:
                # Find all matches using regex
                matches = re.findall(regex_pattern, test_string)
            except re.error as e:
                error = f"Invalid regex pattern: {str(e)}"
    
    # Build HTML response
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Regex Matcher</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                max-width: 800px;
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
            .subtitle {{
                text-align: center;
                color: #666;
                margin-bottom: 30px;
            }}
            .form-group {{
                margin-bottom: 20px;
            }}
            label {{
                display: block;
                margin-bottom: 5px;
                font-weight: bold;
                color: #333;
            }}
            input, textarea {{
                width: 100%;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 5px;
                font-size: 1em;
                font-family: monospace;
            }}
            textarea {{
                min-height: 100px;
                resize: vertical;
            }}
            button {{
                background: #4CAF50;
                color: white;
                padding: 12px 30px;
                border: none;
                border-radius: 5px;
                font-size: 1.1em;
                cursor: pointer;
                width: 100%;
            }}
            button:hover {{
                background: #45a049;
            }}
            .results {{
                margin-top: 30px;
                padding: 20px;
                background: #e8f5e9;
                border-radius: 5px;
                border-left: 4px solid #4CAF50;
            }}
            .error {{
                margin-top: 20px;
                padding: 15px;
                background: #ffebee;
                border-radius: 5px;
                border-left: 4px solid #f44336;
                color: #c62828;
            }}
            .match-item {{
                background: white;
                padding: 10px;
                margin: 10px 0;
                border-radius: 5px;
                border-left: 3px solid #4CAF50;
            }}
            .match-count {{
                font-weight: bold;
                color: #4CAF50;
                margin-bottom: 15px;
            }}
            .info {{
                background: #e3f2fd;
                padding: 15px;
                border-radius: 5px;
                margin-bottom: 20px;
                font-size: 0.9em;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Regex Matcher</h1>
            <p class="subtitle">Backend Project 1 - Innomatics Research Labs</p>
            
            <div class="info">
                <strong>How to use:</strong> Enter a test string and regex pattern, then click Submit.<br>
                <strong>Example:</strong> Test String: "hello 123 world" | Regex: <code>\\d+</code> (finds numbers)
            </div>
            
            <form method="POST">
                <div class="form-group">
                    <label>Test String:</label>
                    <textarea name="test_string" required>{test_string}</textarea>
                </div>
                
                <div class="form-group">
                    <label>Regular Expression:</label>
                    <input type="text" name="regex_pattern" value="{regex_pattern}" 
                           placeholder="e.g., \\d+, [a-z]+, \\w+" required>
                </div>
                
                <button type="submit">Find Matches</button>
            </form>
            
            {_render_error(error) if error else ''}
            {_render_results(test_string, regex_pattern, matches) if request.method == 'POST' and not error else ''}
        </div>
    </body>
    </html>
    """
    
    return html

def _render_error(error):
    """Render error message"""
    return f'<div class="error"><strong>Error:</strong> {error}</div>'

def _render_results(test_string, regex_pattern, matches):
    """Render match results"""
    if not matches:
        return '''
        <div class="results">
            <div class="match-count">No matches found</div>
        </div>
        '''
    
    matches_html = '\n'.join([
        f'<div class="match-item">{i+1}. {match}</div>' 
        for i, match in enumerate(matches)
    ])
    
    return f'''
    <div class="results">
        <div class="match-count">Matches Found: {len(matches)}</div>
        <div><strong>Test String:</strong> {test_string}</div>
        <div style="margin-bottom: 15px;"><strong>Regex:</strong> <code>{regex_pattern}</code></div>
        {matches_html}
    </div>
    '''

if __name__ == '__main__':
    print("Starting Regex Matcher Application...")
    print("Visit: http://127.0.0.1:5000/")
    app.run(debug=True, host='0.0.0.0', port=5000)
