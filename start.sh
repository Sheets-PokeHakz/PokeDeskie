echo "🚀 Starting Drums Dealer Bot..."
echo "=================================="

if ! command -v python3 &>/dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

if [ ! -d ".venv" ]; then
    echo "📦 Creating Virtual Environment ..."
    python3 -m venv .venv
fi

echo "🔄 Activating Virtual Environment ..."
source .env/bin/activate

echo "📥 Installing Dependencies ..."
pip install -r requirements.txt

if [ ! -f "Config.json" ]; then
    echo "⚠️  Warning : Config.json Not Found. Creating Default Config File ..."
    cat >Config.json <<EOF
{
    "trade_log": 0,
    "rand_channels": [],
    "trade_channels": [],
    "WEBHOOK_URL": ""
}
EOF
    echo "   Please Edit Config.json With Your Settings."
fi

if [ ! -f "PokeDex.json" ]; then
    echo "❌ PokeDex.json Not Found. This File Is Required For Pokemon Data."
    echo "   Please Ensure PoekeDex.json Is Present In The Current Directory."
    exit 1
fi

echo "✅ Setup Complete! Stating The Bot ..."
echo "=================================="

python bot.py
