"""Static simulations built from real Edron application code."""

__version__ = "0.1.1"

from edron_sim.simulation import (
    EDRON_SIM_SCHEMA,
    Simulation,
    SimulationArtifact,
    SimulationBuildError,
    SimulationConfig,
)

__all__ = [
    "EDRON_SIM_SCHEMA",
    "Simulation",
    "SimulationArtifact",
    "SimulationBuildError",
    "SimulationConfig",
]
