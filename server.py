from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "TennisQ v2.0 - Sistema Online"

@app.route('/health')
def health():
    return {"status": "ok"}

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
