# GitHub 2GB Release Asset Limit Issue

## Problem

The CUDA server binary upload fails in CI with:
```
Error: File size (2543828017) is greater than 2 GiB
```

GitHub release assets have a hard limit of 2GB per file. Our CUDA binary is ~2.5GB, which exceeds this limit.

## Background

The dual-server binary system (see `dual-server-binaries.md`) creates two binaries:
- **CPU binary**: ~500MB ✅ Works fine
- **CUDA binary**: ~2.5GB ❌ Exceeds GitHub limit

## Attempted Solution: Compression

We're testing 7z compression with maximum settings to see if we can squeeze the CUDA binary under 2GB.

### Test Script

Run `backend/test_cuda_compression.py` to test compression locally:

```bash
cd backend
python test_cuda_compression.py
```

This will:
1. Find the CUDA binary in `dist/`
2. Compress it with 7z (maximum compression)
3. Report if the compressed size fits under 2GB

### Expected Compression

PyTorch CUDA binaries typically compress well since they contain:
- Repeated patterns in neural network weights
- Debug symbols and metadata
- Redundant CUDA libraries

Estimated compression: 30-40% reduction
- Original: ~2.5GB
- Target: <2GB
- Required compression: >20%

## Fallback: External Hosting

If compression doesn't work, we'll need to host the CUDA binary externally:

### Option 1: AWS S3
```yaml
- name: Upload CUDA binary to S3
  run: |
    aws s3 cp backend/cuda-release/voicebox-server-cuda-*.exe \
      s3://voicebox-releases/cuda-binaries/${{ github.ref_name }}/
```

### Option 2: Azure Blob Storage
```yaml
- name: Upload to Azure Blob
  run: |
    az storage blob upload \
      --account-name voiceboxreleases \
      --container-name cuda-binaries \
      --file backend/cuda-release/voicebox-server-cuda-*.exe
```

### Option 3: GitHub Packages (Container Registry)
Package as a container image, though this adds complexity for desktop app distribution.

## Implementation Plan

1. **Test compression locally** ← Current step
2. **If compression works (<2GB)**:
   - Update CI to compress before upload
   - Update app to handle .7z downloads
   - Add extraction step in download manager

3. **If compression fails (≥2GB)**:
   - Set up external storage (likely S3)
   - Update CI to upload to S3
   - Provide download URL in release notes
   - Update app download manager to fetch from S3

## CI Workflow Changes (if compression works)

```yaml
- name: Compress CUDA binary (Windows only)
  if: matrix.platform == 'windows-latest'
  shell: bash
  run: |
    cd backend/cuda-release
    7z a -t7z -m0=lzma2 -mx=9 -mfb=64 -md=32m -ms=on \
      voicebox-server-cuda-x86_64-pc-windows-msvc.7z \
      voicebox-server-cuda-*.exe

- name: Upload compressed CUDA server (Windows only)
  if: matrix.platform == 'windows-latest'
  uses: softprops/action-gh-release@v1
  with:
    files: backend/cuda-release/*.7z
```

## User Experience Impact

### With Compression
- Download: `voicebox-server-cuda-*.7z` (~1.5-1.8GB)
- App extracts automatically
- One extra step but manageable

### With External Hosting
- Download from S3/Azure URL
- No GitHub release asset dependency
- Potentially faster download speeds (CDN)

## Status

🔄 **Testing compression locally to determine viability**

Results pending from local test run.
