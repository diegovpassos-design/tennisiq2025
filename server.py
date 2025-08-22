from flask import Flask
import os

app = Flask(__name__)

@app.route('/')
def home():
    return """
    <h1>🎾 TennisQ v2.0 - Sistema Online</h1>
    <p>Status: <strong>ATIVO</strong></p>
    <p>Deploy: <strong>SUCESSO</strong></p>
    <p>Hora: <strong>2025-08-22</strong></p>
    <hr>
    <p><a href="/health">Health Check</a></p>
    <p><a href="/status">Status Completo</a></p>
    """

@app.route('/health')
def health():
    return {"status": "ok", "service": "TennisQ", "version": "2.0"}

@app.route('/status')
def status():
    return {
        "status": "online",
        "service": "TennisQ Pre-Live",
        "version": "2.0", 
        "timestamp": "2025-08-22",
        "port": os.environ.get("PORT", "8080"),
        "message": "Sistema funcionando!"
    }

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    print(f"🚀 TennisQ iniciando na porta {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
