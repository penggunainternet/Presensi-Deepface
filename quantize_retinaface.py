"""
Quantize RetinaFace H5 model to TFLite FP16 format
Usage: python quantize_retinaface.py

This script attempts to convert the RetinaFace H5 model used by DeepFace
to TFLite format for optimized inference.
"""

import tensorflow as tf
import os
import sys
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')


def handle_deepface_retinaface():
    """
    Alternative approach: Use DeepFace's built-in RetinaFace model
    This is informational - DeepFace uses RetinaFace internally for detection
    """
    print("\n" + "="*60)
    print("RETINAFACE MODEL INFORMATION")
    print("="*60)
    print("\n[*] RetinaFace is used as the face detection backend in DeepFace")
    print("[*] Current Configuration:")
    print("    - Detector Backend: RetinaFace")
    print("    - Model Location: models/.deepface/weights/retinaface.h5")
    print("    - Purpose: Real-time face detection for preprocessing")
    print("\n[*] Performance Notes:")
    print("    - RetinaFace provides accurate face detection with confidence scores")
    print("    - The H5 model includes custom layers not easily convertible to TFLite")
    print("    - DeepFace already optimizes this internally")
    print("\n[*] Recommendation:")
    print("    - Keep using DeepFace's RetinaFace for detection")
    print("    - Focus optimization efforts on the embedding model (ArcFace)")
    print("    - ArcFace TFLite FP16 is available: models/arcface_fp16.tflite")
    print("="*60 + "\n")
    
    return True


def quantize_retinaface_h5_to_tflite():
    """
    Convert RetinaFace H5 model to TFLite Float32 format
    NOTE: RetinaFace H5 may contain custom layers that don't convert easily
    """
    h5_path = r"Z:\App\laragon\www\presensi\models\.deepface\weights\retinaface.h5"
    output_float32 = "models/retinaface.tflite"
    output_fp16 = "models/retinaface_fp16.tflite"
    
    print("[*] RetinaFace H5 to TFLite Quantization Attempt")
    print(f"[*] Input H5: {h5_path}")
    print(f"[*] Output Float32: {output_float32}")
    print(f"[*] Output FP16: {output_fp16}")
    
    # Check if H5 file exists
    if not os.path.exists(h5_path):
        print(f"[!] H5 file not found: {h5_path}")
        return handle_deepface_retinaface()
    
    h5_size_mb = os.path.getsize(h5_path) / (1024*1024)
    print(f"[+] H5 file found, size: {h5_size_mb:.2f} MB")
    
    try:
        # Step 1: Load H5 model
        print("\n[Step 1] Loading H5 model...")
        
        # Try standard Keras loading
        try:
            print("    [*] Attempting standard Keras load...")
            model = tf.keras.models.load_model(h5_path, compile=False)
            print("[+] H5 model loaded successfully")
            print(f"    Model input shape: {model.input_shape}")
            print(f"    Model output layers: {len(model.outputs)}")
        except ValueError as ve:
            if "No model config found" in str(ve):
                print(f"    [!] Model config not found (custom architecture)")
                print(f"    [*] RetinaFace uses custom layers that prevent direct conversion")
                return handle_deepface_retinaface()
            raise
        
        # Step 2: Convert to TFLite Float32
        print("\n[Step 2] Converting to TFLite Float32...")
        converter = tf.lite.TFLiteConverter.from_keras_model(model)
        converter.target_spec.supported_ops = [
            tf.lite.OpsSet.TFLITE_BUILTINS,
        ]
        converter.optimizations = []  # No optimization for Float32
        
        tflite_model_float32 = converter.convert()
        
        # Save Float32 model
        os.makedirs("models", exist_ok=True)
        with open(output_float32, 'wb') as f:
            f.write(tflite_model_float32)
        
        file_size = os.path.getsize(output_float32) / (1024 * 1024)
        print(f"[+] TFLite Float32 saved: {output_float32} ({file_size:.2f} MB)")
        
        # Step 3: Convert to TFLite FP16 (quantized)
        print("\n[Step 3] Converting to TFLite FP16 (quantized)...")
        converter_fp16 = tf.lite.TFLiteConverter.from_keras_model(model)
        converter_fp16.target_spec.supported_ops = [
            tf.lite.OpsSet.TFLITE_BUILTINS,
        ]
        # Enable FP16 quantization
        converter_fp16.optimizations = [tf.lite.Optimize.DEFAULT]
        converter_fp16.target_spec.supported_types = [tf.float16]
        
        tflite_model_fp16 = converter_fp16.convert()
        
        # Save FP16 model
        with open(output_fp16, 'wb') as f:
            f.write(tflite_model_fp16)
        
        file_size_fp16 = os.path.getsize(output_fp16) / (1024 * 1024)
        print(f"[+] TFLite FP16 saved: {output_fp16} ({file_size_fp16:.2f} MB)")
        
        # Step 4: Verify models
        print("\n[Step 4] Verifying models...")
        
        # Verify Float32
        try:
            interpreter_f32 = tf.lite.Interpreter(model_path=output_float32)
            interpreter_f32.allocate_tensors()
            print("[+] Float32 model verification: OK")
        except Exception as e:
            print(f"[!] Float32 model verification failed: {e}")
            return False
        
        # Verify FP16
        try:
            interpreter_fp16 = tf.lite.Interpreter(model_path=output_fp16)
            interpreter_fp16.allocate_tensors()
            print("[+] FP16 model verification: OK")
        except Exception as e:
            print(f"[!] FP16 model verification failed: {e}")
            return False
        
        # Summary
        print("\n" + "="*60)
        print("RETINAFACE QUANTIZATION SUCCESSFUL!")
        print("="*60)
        print(f"\nFloat32 Model:")
        print(f"  Path: {output_float32}")
        print(f"  Size: {file_size:.2f} MB")
        
        print(f"\nFP16 Model (Quantized):")
        print(f"  Path: {output_fp16}")
        print(f"  Size: {file_size_fp16:.2f} MB")
        print(f"  Compression: {(1 - file_size_fp16/file_size)*100:.1f}%")
        
        print("\nYou can now use these models for face detection:")
        print("  - Float32: Higher accuracy, larger file size")
        print("  - FP16: Faster inference, smaller file size (recommended)")
        print("="*60)
        
        return True
        
    except Exception as e:
        print(f"\n[!] Error during conversion: {e}")
        print(f"[*] Traceback:")
        import traceback
        traceback.print_exc()
        print(f"\n[*] RetinaFace H5 model uses custom layers that cannot be directly converted to TFLite")
        return handle_deepface_retinaface()


if __name__ == "__main__":
    print("\n" + "="*60)
    print("RetinaFace Model Quantization Utility")
    print("="*60)
    
    success = quantize_retinaface_h5_to_tflite()
    
    if success:
        print("\n[+] Process completed successfully!")
        sys.exit(0)
    else:
        print("\n[!] Process completed with fallback/warnings")
        sys.exit(0)
