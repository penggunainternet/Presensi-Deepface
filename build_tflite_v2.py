"""
Extract ArcFace model dari DeepFace dan convert ke TFLite models
Nama: arcface_v2.tflite dan arcface_fp16_v2.tflite
"""

import tensorflow as tf
import numpy as np
import os
from deepface import DeepFace

def build_and_convert_arcface():
    """
    1. Load ArcFace model dari DeepFace
    2. Convert ke TFLite Float32
    3. Convert ke TFLite FP16
    """
    try:
        print("[*] Loading ArcFace model dari DeepFace...")
        
        # Build model - ini akan download jika belum ada
        model = DeepFace.build_model("ArcFace")
        
        # Ambil keras model dari client object
        if hasattr(model, 'model'):
            keras_model = model.model
        else:
            raise Exception("Cannot extract keras model from DeepFace")
        
        print(f"[+] Model loaded")
        print(f"    Input shape: {keras_model.input_shape}")
        print(f"    Output shape: {keras_model.output_shape}")
        
        # Create models directory
        os.makedirs("models", exist_ok=True)
        
        # ===== FLOAT32 VERSION =====
        print("\n[*] Converting to TFLite Float32 (arcface_v2.tflite)...")
        converter_float = tf.lite.TFLiteConverter.from_keras_model(keras_model)
        converter_float.target_spec.supported_ops = [
            tf.lite.OpsSet.TFLITE_BUILTINS,
            tf.lite.OpsSet.SELECT_TF_OPS
        ]
        
        tflite_float = converter_float.convert()
        
        float_path = "models/arcface_v2.tflite"
        with open(float_path, 'wb') as f:
            f.write(tflite_float)
        
        float_size = os.path.getsize(float_path) / (1024 * 1024)
        print(f"[+] Saved: {float_path} ({float_size:.2f} MB)")
        
        # ===== FP16 VERSION =====
        print("\n[*] Converting to TFLite FP16 (arcface_fp16_v2.tflite)...")
        converter_fp16 = tf.lite.TFLiteConverter.from_keras_model(keras_model)
        converter_fp16.target_spec.supported_ops = [
            tf.lite.OpsSet.TFLITE_BUILTINS,
            tf.lite.OpsSet.SELECT_TF_OPS
        ]
        converter_fp16.optimizations = [tf.lite.Optimize.DEFAULT]
        converter_fp16.target_spec.supported_types = [tf.float16]
        
        tflite_fp16 = converter_fp16.convert()
        
        fp16_path = "models/arcface_fp16_v2.tflite"
        with open(fp16_path, 'wb') as f:
            f.write(tflite_fp16)
        
        fp16_size = os.path.getsize(fp16_path) / (1024 * 1024)
        print(f"[+] Saved: {fp16_path} ({fp16_size:.2f} MB)")
        
        # ===== VERIFY =====
        print("\n[*] Verifying models...")
        
        # Test Float32
        print("\n  Testing Float32...")
        interp_float = tf.lite.Interpreter(model_path=float_path)
        interp_float.allocate_tensors()
        in_details = interp_float.get_input_details()
        out_details = interp_float.get_output_details()
        
        test_input = np.random.randn(*in_details[0]['shape']).astype(np.float32)
        interp_float.set_tensor(in_details[0]['index'], test_input)
        interp_float.invoke()
        output_float = interp_float.get_tensor(out_details[0]['index'])
        
        has_nan_float = np.isnan(output_float).any()
        print(f"    Output shape: {output_float.shape}")
        print(f"    Has NaN: {has_nan_float}")
        print(f"    Status: {'FAIL' if has_nan_float else 'OK'}")
        
        # Test FP16
        print("\n  Testing FP16...")
        interp_fp16 = tf.lite.Interpreter(model_path=fp16_path)
        interp_fp16.allocate_tensors()
        in_details_fp16 = interp_fp16.get_input_details()
        out_details_fp16 = interp_fp16.get_output_details()
        
        interp_fp16.set_tensor(in_details_fp16[0]['index'], test_input)
        interp_fp16.invoke()
        output_fp16 = interp_fp16.get_tensor(out_details_fp16[0]['index'])
        
        has_nan_fp16 = np.isnan(output_fp16).any()
        print(f"    Output shape: {output_fp16.shape}")
        print(f"    Has NaN: {has_nan_fp16}")
        print(f"    Status: {'FAIL' if has_nan_fp16 else 'OK'}")
        
        # Summary
        print("\n" + "="*60)
        print("SUMMARY")
        print("="*60)
        print(f"Float32: {float_path} ({float_size:.2f} MB) - {'PASS' if not has_nan_float else 'FAIL'}")
        print(f"FP16:    {fp16_path} ({fp16_size:.2f} MB) - {'PASS' if not has_nan_fp16 else 'FAIL'}")
        print("="*60)
        
        return not (has_nan_float or has_nan_fp16)
        
    except Exception as e:
        print(f"\n[!] Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("="*60)
    print("ArcFace Model Conversion (DeepFace -> TFLite)")
    print("="*60 + "\n")
    
    success = build_and_convert_arcface()
    
    if success:
        print("\n[OK] Models ready! Update app.py to use:")
        print("  - models/arcface_v2.tflite (Float32)")
        print("  - models/arcface_fp16_v2.tflite (FP16)")
    else:
        print("\n[FAIL] Model generation had issues")
