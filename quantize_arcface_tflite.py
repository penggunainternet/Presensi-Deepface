"""
Quantize TFLite model to FP16 format
Usage: python quantize_arcface_tflite.py --input models/arcface.tflite --output models/arcface_fp16.tflite
"""

import tensorflow as tf
import argparse
import os


def quantize_tflite_to_fp16(input_path, output_path):
    """
    Quantize TFLite Float32 model to FP16 format
    
    Args:
        input_path: Path to the input TFLite Float32 model
        output_path: Path to save the quantized FP16 model
    """
    try:
        print(f"[*] Loading TFLite model from {input_path}...")
        
        # Load the original TFLite model
        with open(input_path, 'rb') as f:
            tflite_model = f.read()
        
        # Create interpreter to verify model
        interpreter = tf.lite.Interpreter(model_path=input_path)
        interpreter.allocate_tensors()
        print("[+] Model loaded and verified")
        
        # Convert to FP16
        print("[*] Converting to FP16 quantization...")
        converter = tf.lite.TFLiteConverter.from_saved_model(
            input_path.replace('.tflite', '')
        )
        
        # This approach might fail, let's use a different method
        # Load as interpreter and re-convert with FP16 optimization
        
    except Exception as e:
        print(f"[!] Standard conversion failed, trying alternative method...")
        return quantize_tflite_fp16_alternative(input_path, output_path)


def quantize_tflite_fp16_alternative(input_path, output_path):
    """
    Alternative FP16 quantization using TensorFlow Lite Optimizer
    """
    try:
        print(f"[*] Using TensorFlow Lite Optimizer for FP16 quantization...")
        
        # Read the original model
        with open(input_path, 'rb') as f:
            original_model = f.read()
        
        # We need to use the TFLite flatbuffer approach
        # For now, use a simple quantization through TensorFlow's quantization API
        
        from tensorflow.lite.python import schema_py_generated as schema_fb
        
        # Load model and convert
        converter = tf.lite.TFLiteConverter.from_saved_model(
            input_path.rsplit('.', 1)[0]  # Remove .tflite extension
        )
        
        # Set FP16 quantization
        converter.optimizations = [tf.lite.Optimize.DEFAULT]
        converter.target_spec.supported_types = [tf.float16]
        
        tflite_quant_model = converter.convert()
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'wb') as f:
            f.write(tflite_quant_model)
        
        file_size = os.path.getsize(output_path) / (1024 * 1024)
        original_size = os.path.getsize(input_path) / (1024 * 1024)
        
        print(f"[+] FP16 quantized model saved to {output_path}")
        print(f"[+] Original size: {original_size:.2f} MB")
        print(f"[+] Quantized size: {file_size:.2f} MB")
        print(f"[+] Compression ratio: {(1 - file_size/original_size)*100:.1f}%")
        
        return True
        
    except Exception as e:
        print(f"[!] Alternative conversion also failed: {e}")
        print("[*] Trying direct conversion from saved model...")
        return quantize_from_saved_model(input_path, output_path)


def quantize_from_saved_model(input_path, output_path):
    """
    Direct quantization from saved model format
    """
    try:
        print("[*] Attempting direct conversion...")
        
        # For ArcFace TFLite model, we need to work with the model directly
        # Load and re-export with FP16 target spec
        
        interpreter = tf.lite.Interpreter(model_path=input_path)
        
        # Since we have a TFLite model, we need to extract it and convert properly
        # This is a workaround - read the original model and quantize it
        
        with open(input_path, 'rb') as f:
            model_content = f.read()
        
        # Create a new converter with FP16 optimization
        converter = tf.lite.TFLiteConverter.from_saved_model(
            input_path.replace('.tflite', '_saved')
        )
        converter.optimizations = [tf.lite.Optimize.DEFAULT]
        converter.target_spec.supported_types = [tf.float16]
        converter.experimental_enable_resource_variables = False
        
        quantized_model = converter.convert()
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'wb') as f:
            f.write(quantized_model)
        
        file_size = os.path.getsize(output_path) / (1024 * 1024)
        print(f"[+] FP16 quantized model saved to {output_path}")
        print(f"[+] Model size: {file_size:.2f} MB")
        
        return True
        
    except Exception as e:
        print(f"[!] Error: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Quantize TFLite model to FP16")
    parser.add_argument("--input", type=str, required=True, help="Input TFLite Float32 model path")
    parser.add_argument("--output", type=str, default="models/arcface_fp16.tflite", help="Output FP16 model path")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input):
        print(f"[!] Input model not found: {args.input}")
        exit(1)
    
    success = quantize_tflite_to_fp16(args.input, args.output)
    
    if success:
        print("\n[+] Quantization completed successfully!")
    else:
        print("\n[!] Quantization failed. You may need to use Keras model instead.")
        print("    Recommend: python convert_h5_to_tflite.py first, then try this again")
    
    exit(0 if success else 1)


if __name__ == "__main__":
    main()
