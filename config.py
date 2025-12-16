import os

# Model cache directory
MODEL_CACHE_DIR = os.path.join(os.path.dirname(__file__), 'models')

# Buat folder jika belum ada
os.makedirs(MODEL_CACHE_DIR, exist_ok=True)

# Set environment variable untuk cache model
os.environ['TF_CPP_LOGGING_LEVEL'] = '2'  # Kurangi TensorFlow logs
