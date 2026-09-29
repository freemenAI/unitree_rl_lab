python - <<'PY'
from pathlib import Path
import torch

old = Path("logs/rsl_rl/unitree_g1_29dof_velocity_rough/2026-09-05_20-14-50/model_4400.pt")
new = old.with_name("model_4400_log.pt")

if new.exists():
    raise FileExistsError(f"Output already exists: {new}")

checkpoint = torch.load(old, map_location="cpu", weights_only=False)
state = checkpoint["model_state_dict"]
std = state["std"]

if not torch.isfinite(std).all() or not (std > 0).all():
    raise ValueError("Checkpoint std is invalid. Use an earlier checkpoint.")

state["log_std"] = std.log()
del state["std"]
checkpoint["optimizer_state_dict"]["state"] = {}

torch.save(checkpoint, new)
print(f"Saved: {new}")
print(f"Original std range: {std.min().item():.6f} to {std.max().item():.6f}")
PY
