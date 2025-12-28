"""
Build all model variants (DeepFace, TFLite Float32, TFLite FP16)
This is the main build script for quantization and model generation

Usage: python build_all_models.py --h5_path <path_to_arcface_h5>
"""

import subprocess
import sys
import os
import argparse


def run_command(cmd, description):
    """Run a shell command and return success status"""
    print(f"\n{'='*60}")
    print(f"[*] {description}")
    print(f"{'='*60}")
    print(f"Command: {' '.join(cmd)}\n")
    
    try:
        result = subprocess.run(cmd, check=True, cwd=os.getcwd())
        print(f"\n[+] {description} - SUCCESS")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n[!] {description} - FAILED")
        print(f"Error code: {e.returncode}")
        return False
    except Exception as e:
        print(f"\n[!] {description} - ERROR: {e}")
        return False


def build_all_models(h5_path):
    """
    Build all model variants
    
    Args:
        h5_path: Path to the Keras H5 model
    
    Returns:
        bool: True if all steps succeeded
    """
    
    if not os.path.exists(h5_path):
        print(f"[!] H5 model not found: {h5_path}")
        return False
    
    print("[*] Starting model build pipeline...")
    print(f"[*] Input H5 model: {h5_path}")
    
    # Step 1: Generate FP16 model (includes Float32 as intermediate)
    print("\n[Step 1/1] Generating TFLite models with FP16 quantization...")
    
    cmd = [
        sys.executable,
        "generate_fp16_model.py",
        "--h5_path", h5_path,
        "--output_dir", "models"
    ]
    
    if not run_command(cmd, "TFLite FP16 Generation"):
        return False
    
    # Verify output files
    print("\n[*] Verifying generated models...")
    
    float32_model = "models/arcface.tflite"
    fp16_model = "models/arcface_fp16.tflite"
    
    models_ok = True
    
    if os.path.exists(float32_model):
        size = os.path.getsize(float32_model) / (1024 * 1024)
        print(f"[+] Float32 model exists: {float32_model} ({size:.2f} MB)")
    else:
        print(f"[!] Float32 model not found: {float32_model}")
        models_ok = False
    
    if os.path.exists(fp16_model):
        size = os.path.getsize(fp16_model) / (1024 * 1024)
        print(f"[+] FP16 model exists: {fp16_model} ({size:.2f} MB)")
    else:
        print(f"[!] FP16 model not found: {fp16_model}")
        models_ok = False
    
    if models_ok:
        print("\n" + "="*60)
        print("ALL MODELS BUILT SUCCESSFULLY!")
        print("="*60)
        print("\nModels ready for use:")
        print("  - models/arcface.tflite (Float32, for reference)")
        print("  - models/arcface_fp16.tflite (FP16, recommended for production)")
        print("\nYou can now use these models in your app.py")
        print("="*60)
        return True
    else:
        print("\n[!] Some models are missing!")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Build all TFLite model variants with quantization"
    )
    parser.add_argument(
        "--h5_path",
        type=str,
        required=True,
        help="Path to Keras H5 ArcFace model"
    )
    
    args = parser.parse_args()
    
    success = build_all_models(args.h5_path)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
