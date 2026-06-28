"""
EVEZ Art Trainer LITE — Ultra-lightweight VAE
32x32 images, batch_size=2, 4-channel latent
Trains on Steven art corpus, CPU-only, <2GB RAM
"""
import os, sys, json, glob, random
import numpy as np
from PIL import Image
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader

EIGENVALUES = [0.973, 0.03, 0.45, -0.333, -0.441, 0.93]

class EVEZDataset(Dataset):
    def __init__(self, root_dirs, size=32, max_images=100):
        self.size = size
        self.samples = []
        exts = {".png", ".jpg", ".jpeg", ".bmp"}
        for d in root_dirs:
            if not os.path.exists(d): continue
            for f in sorted(os.listdir(d)):
                if os.path.splitext(f)[1].lower() in exts:
                    p = os.path.join(d, f)
                    if os.path.getsize(p) > 1000:  # skip tiny files
                        self.samples.append(p)
        self.samples = self.samples[:max_images]
        print(f"Dataset: {len(self.samples)} images at {size}x{size}")
    
    def __len__(self): return len(self.samples)
    
    def __getitem__(self, idx):
        try:
            img = Image.open(self.samples[idx]).convert("RGB").resize((self.size, self.size))
        except:
            img = Image.new("RGB", (self.size, self.size), (10, 10, 15))
        arr = np.array(img, dtype=np.float32) / 255.0
        arr[:,:,0] = np.clip(arr[:,:,0] * 1.1, 0, 1)
        arr[:,:,2] = np.clip(arr[:,:,2] * 1.05, 0, 1)
        t = torch.from_numpy(arr).permute(2, 0, 1)
        cond = torch.tensor(EIGENVALUES, dtype=torch.float32)
        return t, cond

class TinyVAE(nn.Module):
    def __init__(self, latent_dim=32, cond_dim=6):
        super().__init__()
        self.enc = nn.Sequential(
            nn.Conv2d(3 + cond_dim, 16, 4, 2, 1),   # 32->16
            nn.LeakyReLU(0.2),
            nn.Conv2d(16, 32, 4, 2, 1),              # 16->8
            nn.LeakyReLU(0.2),
            nn.Conv2d(32, 64, 4, 2, 1),              # 8->4
            nn.LeakyReLU(0.2),
        )
        self.fc_mu = nn.Linear(64 * 4 * 4, latent_dim)
        self.fc_lv = nn.Linear(64 * 4 * 4, latent_dim)
        self.fc_dec = nn.Linear(latent_dim + cond_dim, 64 * 4 * 4)
        self.dec = nn.Sequential(
            nn.ConvTranspose2d(64, 32, 4, 2, 1),     # 4->8
            nn.LeakyReLU(0.2),
            nn.ConvTranspose2d(32, 16, 4, 2, 1),     # 8->16
            nn.LeakyReLU(0.2),
            nn.ConvTranspose2d(16, 3, 4, 2, 1),      # 16->32
            nn.Sigmoid(),
        )
    
    def forward(self, x, cond):
        cm = cond.unsqueeze(-1).unsqueeze(-1).expand(-1, -1, x.size(2), x.size(3))
        h = self.enc(torch.cat([x, cm], 1))
        h = h.view(h.size(0), -1)
        mu, lv = self.fc_mu(h), self.fc_lv(h)
        z = mu + torch.randn_like(mu) * torch.exp(0.5 * lv)
        h2 = self.fc_dec(torch.cat([z, cond], 1)).view(z.size(0), 64, 4, 4)
        return self.dec(h2), mu, lv

def train():
    dirs = [
        "/home/openclaw/.openclaw/workspace/",
        "/home/openclaw/.openclaw/workspace/meme-media/",
        "/home/openclaw/.openclaw/workspace/evez-research-repo/visuals/",
    ]
    ds = EVEZDataset(dirs, size=32, max_images=80)
    if len(ds) == 0:
        print("No images found"); return
    loader = DataLoader(ds, batch_size=2, shuffle=True, num_workers=0)
    model = TinyVAE(latent_dim=32, cond_dim=6)
    opt = optim.Adam(model.parameters(), lr=1e-4)
    params = sum(p.numel() for p in model.parameters())
    print(f"Model: {params:,} params")
    print(f"Training: {len(ds)} images, batch=2, 30 epochs")
    
    best = float("inf")
    for ep in range(30):
        tl, n = 0, 0
        for bx, bc in loader:
            opt.zero_grad()
            recon, mu, lv = model(bx, bc)
            rl = nn.functional.mse_loss(recon, bx, reduction="sum")
            kld = -0.5 * torch.sum(1 + lv - mu.pow(2) - lv.exp())
            loss = rl + 0.01 * kld
            loss.backward()
            opt.step()
            tl += loss.item(); n += bx.size(0)
        avg = tl / n
        if avg < best:
            best = avg
            torch.save(model.state_dict(), "/home/openclaw/.openclaw/workspace/evez-art-model-lite.pt")
        if (ep+1) % 5 == 0 or ep == 0:
            print(f"Epoch {ep+1:2d}/30 | Loss: {avg:.1f}")
    print(f"\nDone. Best: {best:.1f}")
    print(f"Saved: evez-art-model-lite.pt")
    
    # Generate samples
    print("\n=== SAMPLES ===")
    model.eval()
    os.makedirs("/home/openclaw/.openclaw/workspace/evez-generated", exist_ok=True)
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
        cond = torch.tensor([evs], dtype=torch.float32)
        z = torch.randn(1, 32)
        with torch.no_grad():
            img = model.dec(model.fc_dec(torch.cat([z, cond], 1)).view(1, 64, 4, 4))
        arr = img[0].numpy().transpose(1, 2, 0)
        arr = np.clip(arr * 255, 0, 255).astype(np.uint8)
        Image.fromarray(arr).save(f"/home/openclaw/.openclaw/workspace/evez-generated/{name}.png")
        print(f"  {name}.png")
    print(f"\n8 samples in evez-generated/")

if __name__ == "__main__":
    train()
