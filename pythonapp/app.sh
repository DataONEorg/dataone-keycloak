echo "Creating python environment..."

# Set up environment
export VIRTUAL_ENV=/data/venv
python -m pip install uv --root-user-action ignore
cd /app
uv venv --allow-existing ${VIRTUAL_ENV}
source ${VIRTUAL_ENV}/bin/activate
uv sync --active

echo "Starting app..."
python app.py
