"""Test CUDA detection in voicebox backend"""
import sys
import torch

print("=" * 60)
print("PyTorch CUDA Detection Test")
print("=" * 60)

# Basic torch info
print(f"\nPyTorch version: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")

if torch.cuda.is_available():
    print(f"CUDA version: {torch.version.cuda}")
    print(f"GPU count: {torch.cuda.device_count()}")
    print(f"Current GPU: {torch.cuda.current_device()}")
    print(f"GPU name: {torch.cuda.get_device_name(0)}")
    print(f"GPU memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")
else:
    print("\nNo CUDA available - would run on CPU")

# Test backend device selection
print("\n" + "=" * 60)
print("Backend Device Selection")
print("=" * 60)

# Simulate the _get_device method from pytorch_backend.py
def _get_device() -> str:
    """Get the best available device."""
    if torch.cuda.is_available():
        return "cuda"
    elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
        # MPS can have issues, use CPU for stability
        return "cpu"
    return "cpu"

selected_device = _get_device()
print(f"\nSelected device: {selected_device}")
print(f"Would use dtype: {'torch.bfloat16' if selected_device != 'cpu' else 'torch.float32'}")

# Test actual tensor creation on device
print("\n" + "=" * 60)
print("Testing Tensor Creation on Device")
print("=" * 60)

try:
    test_tensor = torch.randn(1000, 1000).to(selected_device)
    print(f"\n[OK] Successfully created tensor on {selected_device}")
    print(f"  Tensor device: {test_tensor.device}")
    print(f"  Tensor dtype: {test_tensor.dtype}")

    # Test computation
    result = test_tensor @ test_tensor.T
    print(f"[OK] Successfully performed computation on {selected_device}")

    if selected_device == "cuda":
        print(f"\nCUDA memory allocated: {torch.cuda.memory_allocated() / 1024**2:.2f} MB")
        print(f"CUDA memory reserved: {torch.cuda.memory_reserved() / 1024**2:.2f} MB")

except Exception as e:
    print(f"\n[ERROR] {e}")

print("\n" + "=" * 60)
print("Summary")
print("=" * 60)

if selected_device == "cuda":
    print("\n[SUCCESS] CUDA IS WORKING!")
    print("  The backend will use your NVIDIA GPU for inference")
    print(f"  GPU: {torch.cuda.get_device_name(0)}")
    print(f"  This will be significantly faster than CPU")
else:
    print("\n[FAIL] CUDA is not available")
    print("  The backend will use CPU for inference")
    print("  This will be slower than GPU")

print("\n" + "=" * 60)
