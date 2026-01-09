from flask import Flask, render_template, request

app = Flask(__name__)

# Store notes in a list (will persist during server runtime)
notes = []

@app.route('/', methods=["GET", "POST"])  # Bug Fix #1: Added GET method
def index():
    if request.method == "POST":  # Bug Fix #2: Check method before processing
        note = request.form.get("note")  # Bug Fix #3: Changed from request.args to request.form
        if note and note.strip():  # Bug Fix #4: Validate note is not empty
            notes.append(note.strip())
    return render_template("home_fixed.html", notes=notes)


if __name__ == '__main__':
    app.run(debug=True)
