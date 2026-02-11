"""
Advanced Feature Engineering for Stock Analysis
Creates composite scores and advanced financial metrics
"""

import os
import sys
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.utils.logger import logger


class FeatureEngineer:
    """Advanced feature engineering for stock analysis"""

    def __init__(self):
        self.features_created = []

    def engineer_all_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply all feature engineering transformations"""

        logger.info("Starting feature engineering...")
        df = df.copy()

        df = self._calculate_peg_ratio(df)
        df = self._create_quality_score(df)
        df = self._create_value_score(df)
        df = self._create_growth_score(df)
        df = self._create_momentum_score(df)
        df = self._calculate_altman_z_score(df)
        df = self._calculate_profitability_flag(df)
        df = self._categorize_risk(df)
        df = self._normalize_composite_scores(df)

        logger.info(
            f"Feature engineering complete. Created {len(self.features_created)} features"
        )
        return df

    # ------------------------------------------------------------------
    # Core Feature Builders
    # ------------------------------------------------------------------

    def _calculate_peg_ratio(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate PEG ratio where possible"""

        df["peg_ratio_calculated"] = np.where(
            (df["pe_ratio"].notna())
            & (df["earnings_growth"].notna())
            & (df["earnings_growth"] > 0),
            df["pe_ratio"] / (df["earnings_growth"] * 100),
            np.nan,
        )

        df["peg_ratio"] = df["peg_ratio"].fillna(df["peg_ratio_calculated"])

        self.features_created.append("peg_ratio_calculated")
        logger.info("Calculated PEG ratios")
        return df

    def _create_quality_score(self, df: pd.DataFrame) -> pd.DataFrame:
        """Business quality score"""

        roe = self._normalize_metric(df["roe"], True).fillna(50)
        margin = self._normalize_metric(df["profit_margin"], True).fillna(50)
        debt = self._normalize_metric(df["debt_to_equity"], False).fillna(50)
        cashflow = self._normalize_metric(df["free_cash_flow"], True).fillna(50)

        df["quality_score_raw"] = (
            0.30 * roe + 0.30 * margin + 0.25 * debt + 0.15 * cashflow
        )

        self.features_created.append("quality_score_raw")
        logger.info("Created quality score")
        return df

    def _create_value_score(self, df: pd.DataFrame) -> pd.DataFrame:
        """Valuation score"""

        pe = self._normalize_metric(df["pe_ratio"], False, cap_at=50).fillna(50)
        peg = self._normalize_metric(df["peg_ratio"], False, cap_at=3).fillna(50)
        pb = self._normalize_metric(df["price_to_book"], False, cap_at=10).fillna(50)
        ps = self._normalize_metric(df["price_to_sales"], False, cap_at=20).fillna(50)

        df["value_score_raw"] = 0.35 * pe + 0.30 * peg + 0.20 * pb + 0.15 * ps

        self.features_created.append("value_score_raw")
        logger.info("Created value score")
        return df

    def _create_growth_score(self, df: pd.DataFrame) -> pd.DataFrame:
        """Growth potential score"""

        revenue = self._normalize_metric(df["revenue_growth"], True).fillna(50)
        earnings = self._normalize_metric(df["earnings_growth"], True).fillna(50)
        returns = self._normalize_metric(df["return_1y"], True).fillna(50)

        df["growth_score_raw"] = (
            0.40 * revenue + 0.35 * earnings + 0.25 * returns
        )

        self.features_created.append("growth_score_raw")
        logger.info("Created growth score")
        return df

    def _create_momentum_score(self, df: pd.DataFrame) -> pd.DataFrame:
        """Momentum score"""

        m1 = self._normalize_metric(df["return_1m"], True).fillna(50)
        m3 = self._normalize_metric(df["return_3m"], True).fillna(50)
        m6 = self._normalize_metric(df["return_6m"], True).fillna(50)

        df["momentum_score_raw"] = 0.50 * m1 + 0.30 * m3 + 0.20 * m6

        self.features_created.append("momentum_score_raw")
        logger.info("Created momentum score")
        return df

    # ------------------------------------------------------------------
    # Financial Health & Risk
    # ------------------------------------------------------------------

    def _calculate_altman_z_score(self, df: pd.DataFrame) -> pd.DataFrame:
        """Simplified Altman Z-Score"""

        wc_ta = np.clip(df["current_ratio"].fillna(1) - 1, -2, 3)
        re_ta = np.clip(df["roe"].fillna(0) * 5, -5, 5)
        ebit_ta = np.clip(df["operating_margin"].fillna(0) * 3.3, -5, 5)
        mv_tl = np.clip(1 / (df["debt_to_equity"].fillna(0.5) + 0.01), 0, 10)

        df["altman_z_score"] = wc_ta + re_ta + ebit_ta + mv_tl

        df["financial_health"] = pd.cut(
            df["altman_z_score"],
            bins=[-np.inf, 1.8, 3.0, np.inf],
            labels=["High Risk", "Medium Risk", "Low Risk"],
        )

        self.features_created.extend(["altman_z_score", "financial_health"])
        logger.info("Calculated Altman Z-Score")
        return df

    def _calculate_profitability_flag(self, df: pd.DataFrame) -> pd.DataFrame:
        """Profitability flags"""

        df["is_profitable"] = df["profit_margin"] > 0
        df["profitability_status"] = np.where(
            df["profit_margin"] > 0.15,
            "Highly Profitable",
            np.where(
                df["profit_margin"] > 0.05,
                "Profitable",
                np.where(
                    df["profit_margin"] > 0,
                    "Marginally Profitable",
                    "Unprofitable",
                ),
            ),
        )

        self.features_created.extend(["is_profitable", "profitability_status"])
        logger.info("Created profitability flags")
        return df

    def _categorize_risk(self, df: pd.DataFrame) -> pd.DataFrame:
        """Overall risk categorization"""

        risk_score = (
            np.clip((df["beta"].fillna(1) - 0.5) * 2, 0, 3)
            + np.clip(df["volatility_90d"].fillna(0.3) * 10, 0, 3)
            + np.clip(df["debt_to_equity"].fillna(0.5) / 0.5, 0, 3)
            + np.where(df["profit_margin"] < 0, 1, 0)
        )

        df["risk_score"] = risk_score
        df["risk_category"] = pd.cut(
            df["risk_score"],
            bins=[0, 3, 6, np.inf],
            labels=["Low Risk", "Medium Risk", "High Risk"],
        )

        self.features_created.extend(["risk_score", "risk_category"])
        logger.info("Categorized risk levels")
        return df

    # ------------------------------------------------------------------
    # Normalization Helpers
    # ------------------------------------------------------------------

    def _normalize_composite_scores(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize composite scores to 0–100"""

        raw_scores = [
            "quality_score_raw",
            "value_score_raw",
            "growth_score_raw",
            "momentum_score_raw",
        ]

        for col in raw_scores:
            if col in df.columns:
                df[col.replace("_raw", "")] = self._scale_to_100(df[col])

        df["composite_score"] = (
            0.25 * df.get("quality_score", 0)
            + 0.25 * df.get("value_score", 0)
            + 0.25 * df.get("growth_score", 0)
            + 0.25 * df.get("momentum_score", 0)
        )

        self.features_created.append("composite_score")
        logger.info("Normalized composite scores")
        return df

    def _normalize_metric(
        self,
        series: pd.Series,
        higher_better: bool = True,
        cap_at: float | None = None,
    ) -> pd.Series:
        """Normalize a metric to 0–100 scale"""

        s = series.copy()

        if cap_at is not None:
            s = s.clip(upper=cap_at)

        min_val, max_val = s.min(), s.max()

        if pd.isna(min_val) or min_val == max_val:
            return pd.Series(50, index=s.index)

        normalized = (s - min_val) / (max_val - min_val) * 100

        if not higher_better:
            normalized = 100 - normalized

        return normalized

    @staticmethod
    def _scale_to_100(series: pd.Series) -> pd.Series:
        """Final scaling helper"""

        if series.max() == series.min():
            return pd.Series(50, index=series.index)

        return (series - series.min()) / (series.max() - series.min()) * 100
