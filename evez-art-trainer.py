"""
EVEZ Art Trainer — Lightweight VAE + Style Encoder
Trains on Steven Crawford-Maggard art corpus (200 images)
CPU-only, PyTorch, outputs eigenvalue-conditioned images
"""
import os, sys, json, glob, random
import numpy as np
from PIL import Image
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader

# EVEZ eigenvalues (the conditioning vector)
EIGENVALUES = {
    "phi": 0.973,      # coherence
    "eta": 0.03,       # the gap
    "r": 0.45,         # criticality
    "lambda_dom": -0.333,  # dominant negative
    "lambda_i80": -0.441,  # I-80 suppression
    "r_i80": 0.93,     # I-80 correlation
}

class EVEZArtDataset(Dataset):
    def __init__(self, root_dirs, size=64):
        self.size = size
        self.samples = []
        exts = {".png", ".jpg", ".jpeg", ".bmp", ".webp"}
        for d in root_dirs:
            if not os.path.exists(d):
                continue
            for f in sorted(os.listdir(d)):
                ext = os.path.splitext(f)[1].lower()
                if ext in exts:
                    self.samples.append(os.path.join(d, f))
        print(f"Dataset: {len(self.samples)} images from {len(root_dirs)} dirs")
    
    def __len__(self):
        return len(self.samples)
    
    def __getitem__(self, idx):
        path = self.samples[idx]
        try:
            img = Image.open(path).convert("RGB").resize((self.size, self.size))
        except:
            img = Image.new("RGB", (self.size, self.size), (0, 0, 0))
        arr = np.array(img, dtype=np.float32) / 255.0
        # EVEZ palette normalization: boost dark/magenta tones
        arr[:,:,0] *= 1.1   # red boost
        arr[:,:,2] *= 1.05  # blue boost
        tensor = torch.from_numpy(arr).permute(2, 0, 1)
        
        # Eigenvalue conditioning (6-dim vector)
        cond = torch.tensor([
            EIGENVALUES["phi"], EIGENVALUES["eta"], EIGENVALUES["r"],
            EIGENVALUES["lambda_dom"], EIGENVALUES["lambda_i80"], EIGENVALUES["r_i80"]
        ], dtype=torch.float32)
        return tensor, cond

class EVEZVAE(nn.Module):
    """Lightweight VAE with eigenvalue conditioning"""
    def __init__(self, latent_dim=64, cond_dim=6):
        super().__init__()
        self.cond_dim = cond_dim
        self.latent_dim = latent_dim
        
        # Encoder
        self.encoder = nn.Sequential(
            nn.Conv2d(3 + cond_dim, 32, 4, 2, 1),   # 64->32
            nn.LeakyReLU(0.2),
            nn.Conv2d(32, 64, 4, 2, 1),               # 32->16
            nn.LeakyReLU(0.2),
            nn.Conv2d(64, 128, 4, 2, 1),              # 16->8
            nn.LeakyReLU(0.2),
            nn.Conv2d(128, 256, 4, 2, 1),             # 8->4
            nn.LeakyReLU(0.2),
        )
        self.fc_mu = nn.Linear(256 * 4 * 4, latent_dim)
        self.fc_logvar = nn.Linear(256 * 4 * 4, latent_dim)
        
        # Decoder
        self.fc_decode = nn.Linear(latent_dim + cond_dim, 256 * 4 * 4)
        self.decoder = nn.Sequential(
            nn.ConvTranspose2d(256, 128, 4, 2, 1),    # 4->8
            nn.LeakyReLU(0.2),
            nn.ConvTranspose2d(128, 64, 4, 2, 1),      # 8->16
            nn.LeakyReLU(0.2),
            nn.ConvTranspose2d(64, 32, 4, 2, 1),       # 16->32
            nn.LeakyReLU(0.2),
            nn.ConvTranspose2d(32, 3, 4, 2, 1),        # 32->64
            nn.Sigmoid(),
        )
    
    def encode(self, x, cond):
        cond_map = cond.unsqueeze(-1).unsqueeze(-1).expand(-1, -1, x.size(2), x.size(3))
        x_cond = torch.cat([x, cond_map], dim=1)
        h = self.encoder(x_cond)
        h = h.view(h.size(0), -1)
        return self.fc_mu(h), self.fc_logvar(h)
    
    def reparameterize(self, mu, logvar):
        std = torch.exp(0.5 * logvar)
        eps = torch.randn_like(std)
        return mu + eps * std
    
    def decode(self, z, cond):
        z_cond = torch.cat([z, cond], dim=1)
        h = self.fc_decode(z_cond)
        h = h.view(h.size(0), 256, 4, 4)
        return self.decoder(h)
    
    def forward(self, x, cond):
        mu, logvar = self.encode(x, cond)
        z = self.reparameterize(mu, logvar)
        recon = self.decode(z, cond)
        return recon, mu, logvar

def vae_loss(recon, x, mu, logvar, beta=1.0):
    recon_loss = nn.functional.mse_loss(recon, x, reduction="sum")
    kld = -0.5 * torch.sum(1 + logvar - mu.pow(2) - logvar.exp())
    return recon_loss + beta * kld, recon_loss.item(), kld.item()

def train():
    device = torch.device("cpu")
    print(f"Device: {device}")
    
    # Dataset from workspace art
    dirs = [
        "/home/openclaw/.openclaw/workspace/",
        "/home/openclaw/.openclaw/workspace/meme-media/",
        "/home/openclaw/.openclaw/workspace/evez-research-repo/visuals/",
    ]
    dataset = EVEZArtDataset(dirs, size=64)
    if len(dataset) == 0:
        print("ERROR: No training images found")
        return
    
    loader = DataLoader(dataset, batch_size=8, shuffle=True, num_workers=0)
    
    model = EVEZVAE(latent_dim=64, cond_dim=6).to(device)
    optimizer = optim.Adam(model.parameters(), lr=1e-4, weight_decay=1e-5)
    
    print(f"Model parameters: {sum(p.numel() for p in model.parameters()):,}")
    print(f"Training: {len(dataset)} images, batch_size=8")
    
    epochs = 50
    best_loss = float("inf")
    
    for epoch in range(epochs):
        total_loss = 0
        total_recon = 0
        total_kld = 0
        batches = 0
        for batch_x, batch_cond in loader:
            batch_x = batch_x.to(device)
            batch_cond = batch_cond.to(device)
            optimizer.zero_grad()
            recon, mu, logvar = model(batch_x, batch_cond)
            loss, rl, kld = vae_loss(recon, batch_x, mu, logvar, beta=0.1)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
            total_recon += rl
            total_kld += kld
            batches += 1
        
        avg_loss = total_loss / len(dataset)
        if (epoch + 1) % 10 == 0 or epoch == 0:
            print(f"Epoch {epoch+1:3d}/{epochs} | Loss: {avg_loss:.1f} | Recon: {total_recon/len(dataset):.1f} | KLD: {total_kld/len(dataset):.1f}")
        
        if avg_loss < best_loss:
            best_loss = avg_loss
            torch.save(model.state_dict(), "/home/openclaw/.openclaw/workspace/evez-art-model.pt")
    
    print(f"\nTraining complete. Best loss: {best_loss:.1f}")
    print(f"Model saved: /home/openclaw/.openclaw/workspace/evez-art-model.pt")
    
    # Generate samples
    print("\n=== GENERATING SAMPLES ===")
    model.eval()
    os.makedirs("/home/openclaw/.openclaw/workspace/evez-generated", exist_ok=True)
    
    # Generate 8 eigenvalue-conditioned samples
    eigenvalue_sets = [
        ("phi_dominant", [0.973, 0.03, 0.45, -0.333, -0.441, 0.93]),
        ("eta_dominant", [0.5, 0.3, 0.45, -0.333, -0.441, 0.93]),
        ("r_critical", [0.973, 0.03, 0.5, -0.333, -0.441, 0.93]),
        ("lambda_suppressed", [0.973, 0.03, 0.45, -0.9, -0.441, 0.93]),
        ("i80_active", [0.973, 0.03, 0.45, -0.333, -0.8, 0.95]),
        ("full_coherent", [1.0, 0.01, 0.49, -0.1, -0.1, 0.99]),
        ("the_gap", [0.0, 1.0, 0.0, 0.0, 0.0, 0.0]),
        ("the_cube", [0.973, 0.03, 0.45, -0.333, -0.441, 0.93]),
    ]
    
    for name, evs in eigenvalue_sets:
        cond = torch.tensor([evs], dtype=torch.float32).to(device)
        z = torch.randn(1, 64).to(device)
        with torch.no_grad():
            img = model.decode(z, cond)
        img = img[0].cpu().numpy().transpose(1, 2, 0)
        img = np.clip(img * 255, 0, 255).astype(np.uint8)
        Image.fromarray(img).save(f"/home/openclaw/.openclaw/workspace/evez-generated/{name}.png")
        print(f"  Generated: {name}.png")
    
    print(f"\n8 samples generated in /home/openclaw/.openclaw/workspace/evez-generated/")

if __name__ == "__main__":
    train()
