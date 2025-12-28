"""
Convert Keras H5 model to TFLite format (Float32)
Usage: python convert_h5_to_tflite.py --h5_path <path_to_h5> --output <output_path>
"""

import tensorflow as tf
import argparse
import os


def convert_h5_to_tflite(h5_path, output_path):
    """
    Convert Keras H5 model to TFLite Float32 format
    
    Args:
        h5_path: Path to the .h5 model file
        output_path: Path to save the .tflite model
    """
    try:
        print(f"[*] Loading H5 model from {h5_path}...")
        model = tf.keras.models.load_model(h5_path)
        print("[+] Model loaded successfully")
        
        print("[*] Converting to TFLite...")
        converter = tf.lite.TFLiteConverter.from_keras_model(model)
        converter.target_spec.supported_ops = [
            tf.lite.OpsSet.TFLITE_BUILTINS,
            tf.lite.OpsSet.SELECT_TF_OPS
        ]
        converter.optimizations = []  # No quantization for Float32
        
        tflite_model = converter.convert()
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'wb') as f:
            f.write(tflite_model)
        
        file_size = os.path.getsize(output_path) / (1024 * 1024)
        print(f"[+] TFLite model saved to {output_path}")
        print(f"[+] Model size: {file_size:.2f} MB")
        
    except Exception as e:
        print(f"[!] Error: {e}")
        return False
    
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert Keras H5 to TFLite")
    parser.add_argument("--h5_path", type=str, required=True, help="Path to H5 model")
    parser.add_argument("--output", type=str, default="models/arcface.tflite", help="Output path")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.h5_path):
        print(f"[!] H5 file not found: {args.h5_path}")
        exit(1)
    
    success = convert_h5_to_tflite(args.h5_path, args.output)
    exit(0 if success else 1)
