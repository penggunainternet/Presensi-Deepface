import os
import warnings
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Suppress TensorFlow warnings
os.environ['TF_CPP_LOGGING_LEVEL'] = '2'  # 0=all, 1=info, 2=warning, 3=error
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'  # Disable oneDNN custom ops warnings
warnings.filterwarnings('ignore')

# Model cache directory
MODEL_CACHE_DIR = os.path.join(os.path.dirname(__file__), 'models')

# Buat folder jika belum ada
os.makedirs(MODEL_CACHE_DIR, exist_ok=True)

# Database Configuration
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_NAME = os.getenv('DB_NAME', 'presensi_db')
DB_PORT = int(os.getenv('DB_PORT', 3306))

# Database connection config
DB_CONFIG = {
    'host': DB_HOST,
    'user': DB_USER,
    'password': DB_PASSWORD,
    'database': DB_NAME,
    'port': DB_PORT,
    'autocommit': False
}

