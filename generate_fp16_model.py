"""
Generate FP16 quantized model from Keras H5
Complete pipeline: H5 -> TFLite Float32 -> TFLite FP16

Usage: python generate_fp16_model.py --h5_path <path_to_h5> [--output_dir models]
"""

import tensorflow as tf
import numpy as np
import argparse
import os
import sys


def convert_keras_to_tflite_fp16(h5_path, output_dir="models"):
    """
    Direct conversion from Keras H5 to TFLite FP16 in one step
    
    Args:
        h5_path: Path to Keras H5 model
        output_dir: Output directory for models
    
    Returns:
        bool: Success status
    """
    try:
        print(f"[*] Loading Keras model from {h5_path}...")
        model = tf.keras.models.load_model(h5_path, compile=False)
        print("[+] Model loaded successfully")
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Step 1: Convert to TFLite Float32 first (for verification)
        print("\n[Step 1/2] Converting to TFLite Float32...")
        converter_float = tf.lite.TFLiteConverter.from_keras_model(model)
        converter_float.target_spec.supported_ops = [
            tf.lite.OpsSet.TFLITE_BUILTINS,
            tf.lite.OpsSet.SELECT_TF_OPS
        ]
        converter_float.optimizations = []
        
        tflite_float_model = converter_float.convert()
        
        float32_path = os.path.join(output_dir, "arcface.tflite")
        with open(float32_path, 'wb') as f:
            f.write(tflite_float_model)
        
        float_size = os.path.getsize(float32_path) / (1024 * 1024)
        print(f"[+] Float32 model saved: {float32_path} ({float_size:.2f} MB)")
        
        # Step 2: Verify Float32 model works
        print("\n[*] Verifying Float32 model...")
        interpreter_float = tf.lite.Interpreter(model_path=float32_path)
        interpreter_float.allocate_tensors()
        print("[+] Float32 model verified")
        
        # Step 3: Convert to FP16 quantized
        print("\n[Step 2/2] Converting to TFLite FP16 (quantized)...")
        converter_fp16 = tf.lite.TFLiteConverter.from_keras_model(model)
        converter_fp16.target_spec.supported_ops = [
            tf.lite.OpsSet.TFLITE_BUILTINS,
            tf.lite.OpsSet.SELECT_TF_OPS
        ]
        # FP16 quantization
        converter_fp16.optimizations = [tf.lite.Optimize.DEFAULT]
        converter_fp16.target_spec.supported_types = [tf.float16]
        converter_fp16.experimental_enable_resource_variables = False
        
        tflite_fp16_model = converter_fp16.convert()
        
        fp16_path = os.path.join(output_dir, "arcface_fp16.tflite")
        with open(fp16_path, 'wb') as f:
            f.write(tflite_fp16_model)
        
        fp16_size = os.path.getsize(fp16_path) / (1024 * 1024)
        print(f"[+] FP16 model saved: {fp16_path} ({fp16_size:.2f} MB)")
        
        # Step 4: Verify FP16 model works
        print("\n[*] Verifying FP16 model...")
        interpreter_fp16 = tf.lite.Interpreter(model_path=fp16_path)
        interpreter_fp16.allocate_tensors()
        
        # Get input/output details
        input_details = interpreter_fp16.get_input_details()
        output_details = interpreter_fp16.get_output_details()
        print(f"[+] FP16 model verified")
        print(f"    Input shape: {input_details[0]['shape']}")
        print(f"    Output shape: {output_details[0]['shape']}")
        
        # Test with dummy input
        print("\n[*] Testing FP16 inference...")
        test_input = np.random.randn(*input_details[0]['shape']).astype(np.float32)
        interpreter_fp16.set_tensor(input_details[0]['index'], test_input)
        interpreter_fp16.invoke()
        output = interpreter_fp16.get_tensor(output_details[0]['index'])
        
        # Check for NaN
        if np.isnan(output).any():
            print("[!] Warning: Output contains NaN values!")
            return False
        else:
            print(f"[+] Inference successful, output shape: {output.shape}")
            print(f"[+] Output range: [{output.min():.4f}, {output.max():.4f}]")
        
        # Summary
        print("\n" + "="*60)
        print("QUANTIZATION SUMMARY")
        print("="*60)
        print(f"Float32 model: {float32_path}")
        print(f"  Size: {float_size:.2f} MB")
        print(f"\nFP16 model (quantized): {fp16_path}")
        print(f"  Size: {fp16_size:.2f} MB")
        print(f"  Compression: {(1 - fp16_size/float_size)*100:.1f}%")
        print("="*60)
        
        return True
        
    except Exception as e:
        print(f"\n[!] Error during conversion: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Generate FP16 quantized model from Keras H5"
    )
    parser.add_argument(
        "--h5_path",
        type=str,
        required=True,
        help="Path to Keras H5 model file"
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default="models",
        help="Output directory for TFLite models (default: models/)"
    )
    
    args = parser.parse_args()
    
    # Validate input
    if not os.path.exists(args.h5_path):
        print(f"[!] H5 file not found: {args.h5_path}")
        sys.exit(1)
    
    print(f"[*] H5 model path: {args.h5_path}")
    print(f"[*] Output directory: {args.output_dir}")
    print()
    
    success = convert_keras_to_tflite_fp16(args.h5_path, args.output_dir)
    
    if success:
        print("\n[✓] Models generated successfully!")
        print("[*] Ready to use in app.py")
        sys.exit(0)
    else:
        print("\n[✗] Model generation failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
