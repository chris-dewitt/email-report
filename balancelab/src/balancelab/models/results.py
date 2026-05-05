from __future__ import annotations

from pydantic import BaseModel, Field


class GapTableRow(BaseModel):
    bucket: str
    rsa: float = Field(description="Rate-sensitive assets in bucket")
    rsl: float = Field(description="Rate-sensitive liabilities in bucket")
    gap: float = Field(description="RSA - RSL")
    cumulative_gap: float = Field(description="Running sum of gaps")
    gap_ratio: float = Field(description="Gap / total assets")


class NIIResult(BaseModel):
    scenario_id: str
    scenario_name: str
    base_nii: float = Field(description="NII under current rates")
    shocked_nii: float = Field(description="NII after rate shock")
    delta_nii: float = Field(description="Change in NII")
    delta_nii_pct: float = Field(description="Percentage change in NII")
    horizon_months: int
    top_drivers: list[dict[str, object]] = Field(
        default_factory=list,
        description="Positions contributing most to NII change",
    )


class EVEResult(BaseModel):
    scenario_id: str
    scenario_name: str
    base_eve: float = Field(description="Economic value of equity at current rates")
    shocked_eve: float = Field(description="EVE after rate shock")
    delta_eve: float = Field(description="Change in EVE")
    delta_eve_pct: float = Field(description="Percentage change in EVE")
    asset_duration: float
    liability_duration: float
    duration_gap: float


class LiquidityGapResult(BaseModel):
    gap_table: list[GapTableRow]
    total_rsa: float
    total_rsl: float
    net_gap: float
    one_year_cumulative_gap: float
    one_year_gap_ratio: float


class ScenarioOutput(BaseModel):
    scenario_id: str
    scenario_name: str
    nii: NIIResult
    eve: EVEResult
    liquidity: LiquidityGapResult
    assumptions_summary: dict[str, object] = Field(default_factory=dict)
