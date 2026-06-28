"""
EVEZ Art Trainer — Pure NumPy Autoencoder
No PyTorch, no GPU, <500MB RAM
Trains on Steven art corpus, outputs eigenvalue-conditioned images
"""
import os, sys, json, random
import numpy as np
from PIL import Image

EIGENVALUES = [0.973, 0.03, 0.45, -0.333, -0.441, 0.93]
SIZE = 32
LATENT = 16  # tiny latent space
COND = 6

def load_images(root_dirs, max_images=80):
    images = []
    exts = {".png", ".jpg", ".jpeg", ".bmp"}
    for d in root_dirs:
        if not os.path.exists(d): continue
        for f in sorted(os.listdir(d)):
            if os.path.splitext(f)[1].lower() in exts:
                p = os.path.join(d, f)
                if os.path.getsize(p) > 1000:
                    try:
                        img = Image.open(p).convert("RGB").resize((SIZE, SIZE))
                        arr = np.array(img, dtype=np.float32) / 255.0
                        # EVEZ palette boost
                        arr[:,:,0] = np.clip(arr[:,:,0] * 1.1, 0, 1)
                        arr[:,:,2] = np.clip(arr[:,:,2] * 1.05, 0, 1)
                        images.append(arr.flatten())
                        if len(images) >= max_images:
                            break
                    except:
                        pass
    print(f"Loaded: {len(images)} images at {SIZE}x{SIZE}x3 = {SIZE*SIZE*3} dims")
    return np.array(images)

def train_pca_ae(X, latent_dim, epochs=500, lr=0.01):
    """Simple PCA-based autoencoder via SVD"""
    n, d = X.shape
    # Center
    mean = X.mean(axis=0)
    Xc = X - mean
    # SVD for PCA
    print(f"Computing SVD on {n}x{d} matrix...")
    U, S, Vt = np.linalg.svd(Xc, full_matrices=False)
    # Top-k components
    W = Vt[:latent_dim]  # (latent, d)
    print(f"PCA: top {latent_dim} components explain {sum(S[:latent_dim]**2)/sum(S**2)*100:.1f}% of variance")
    print(f"Eigenvalues (top {latent_dim}): {S[:latent_dim]}")
    
    # Encode: project onto components
    codes = Xc @ W.T  # (n, latent)
    
    # Decode: reconstruct
    X_recon = codes @ W + mean
    
    # Fine-tune with gradient descent on reconstruction loss
    W_dec = W.copy()
    bias = mean.copy()
    for ep in range(epochs):
        # Forward
        codes = (X - bias) @ W.T
        recon = codes @ W_dec + bias
        # Loss
        err = recon - X
        loss = np.mean(err**2)
        # Gradients
        grad_bias = err.mean(axis=0)
        grad_W_dec = codes.T @ err / n
        # Update
        bias -= lr * grad_bias
        W_dec -= lr * grad_W_dec
        if (ep+1) % 100 == 0 or ep == 0:
            print(f"Epoch {ep+1:4d}/{epochs} | MSE: {loss:.6f}")
    
    return W, W_dec, bias, S[:latent_dim]

def generate(W_enc, W_dec, bias, eigenvalues, n_samples=8, latent_dim=16):
    """Generate new images conditioned on eigenvalues"""
    os.makedirs("/home/openclaw/.openclaw/workspace/evez-generated", exist_ok=True)
    
    # Use eigenvalues to modulate latent codes
    ev = np.array(eigenvalues, dtype=np.float32)
    
    samples = [
        ("phi_dominant", [0.973, 0.03, 0.45, -0.333, -0.441, 0.93]),
        ("eta_flood", [0.5, 0.3, 0.45, -0.333, -0.441, 0.93]),
        ("critical_r", [0.973, 0.03, 0.5, -0.333, -0.441, 0.93]),
        ("suppressed", [0.973, 0.03, 0.45, -0.9, -0.441, 0.93]),
        ("i80_burns", [0.973, 0.03, 0.45, -0.333, -0.8, 0.95]),
        ("full_phi", [1.0, 0.01, 0.49, -0.1, -0.1, 0.99]),
        ("the_gap", [0.0, 1.0, 0.0, 0.0, 0.0, 0.0]),
        ("the_cube", [0.973, 0.03, 0.45, -0.333, -0.441, 0.93]),
    ]
    
    for name, evs in samples:
        # Sample latent code: random + eigenvalue modulation
        z = np.random.randn(latent_dim) * 0.1
        # Modulate first 6 dims with eigenvalues
        for i in range(min(6, latent_dim)):
            z[i] += evs[i] * 0.5
        # Decode
        img_flat = z @ W_dec + bias
        img = img_flat.reshape(SIZE, SIZE, 3)
        img = np.clip(img * 255, 0, 255).astype(np.uint8)
        Image.fromarray(img).save(f"/home/openclaw/.openclaw/workspace/evez-generated/{name}.png")
        print(f"  Generated: {name}.png")

def main():
    dirs = [
        "/home/openclaw/.openclaw/workspace/",
        "/home/openclaw/.openclaw/workspace/meme-media/",
        "/home/openclaw/.openclaw/workspace/evez-research-repo/visuals/",
    ]
    X = load_images(dirs, max_images=80)
    if len(X) == 0:
        print("No images found"); return
    
    print(f"\nTraining PCA autoencoder (latent_dim={LATENT})...")
    W_enc, W_dec, bias, eigvals = train_pca_ae(X, LATENT, epochs=500, lr=0.01)
    
    # Save model
    np.savez("/home/openclaw/.openclaw/workspace/evez-art-model.npz",
             W_enc=W_enc, W_dec=W_dec, bias=bias, eigenvalues=eigvals)
    print(f"Model saved: evez-art-model.npz")
    print(f"Latent eigenvalues: {eigvals}")
    
    # Generate
    print(f"\n=== GENERATING SAMPLES ===")
    generate(W_enc, W_dec, bias, EIGENVALUES)
    
    # Reconstruct a few training images
    print(f"\n=== RECONSTRUCTIONS ===")
    os.makedirs("/home/openclaw/.openclaw/workspace/evez-reconstructed", exist_ok=True)
    for i in range(min(8, len(X))):
        code = (X[i] - bias) @ W_enc.T
        recon = code @ W_dec + bias
        img = np.clip(recon.reshape(SIZE, SIZE, 3) * 255, 0, 255).astype(np.uint8)
        Image.fromarray(img).save(f"/home/openclaw/.openclaw/workspace/evez-reconstructed/recon_{i:02d}.png")
        print(f"  recon_{i:02d}.png")
    
    print(f"\nDone. 8 generated + 8 reconstructed images.")
    print(f"Model: evez-art-model.npz ({os.path.getsize('/home/openclaw/.openclaw/workspace/evez-art-model.npz')//1024}KB)")

if __name__ == "__main__":
    main()
