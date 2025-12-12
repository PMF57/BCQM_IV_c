from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Any
import yaml

@dataclass
class SimulationConfig:
    dt: float
    n_steps: int
    n_ensembles: int
    seed: int

@dataclass
class ScanConfig:
    wcoh_values: List[float]
    label: str

@dataclass
class SlipConfig:
    law: str
    params: Dict[str, Any]

@dataclass
class OutputConfig:
    base_dir: str

@dataclass
class Config:
    simulation: SimulationConfig
    scan: ScanConfig
    slip: SlipConfig
    output: OutputConfig

def load_config(path: str | Path) -> Config:
    path = Path(path)
    with path.open("r") as f:
        data = yaml.safe_load(f)

    sim = data.get("simulation", {})
    scan = data.get("scan", {})
    slip = data.get("slip", {})
    out = data.get("output", {})

    simulation = SimulationConfig(
        dt=float(sim.get("dt", 1.0)),
        n_steps=int(sim.get("n_steps", 16384)),
        n_ensembles=int(sim.get("n_ensembles", 64)),
        seed=int(sim.get("seed", 12345)),
    )
    scan_cfg = ScanConfig(
        wcoh_values=[float(x) for x in scan.get("wcoh_values", [5.0, 10.0, 20.0, 40.0, 80.0, 160.0])],
        label=str(scan.get("label", "soft_rudder_wcoh_scan")),
    )
    slip_cfg = SlipConfig(
        law=str(slip.get("law", "exp")),
        params=slip.get("params", {}),
    )
    out_cfg = OutputConfig(
        base_dir=str(out.get("base_dir", "outputs_soft_rudder")),
    )
    return Config(
        simulation=simulation,
        scan=scan_cfg,
        slip=slip_cfg,
        output=out_cfg,
    )
