#!/usr/bin/env python3
"""
EVEZ Forecaster - Time series prediction, trends, forecasting
ARIMA-like models, moving averages, exponential smoothing
"""

import json
import random
import math
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from collections import deque

@dataclass
class Forecast:
    predictions: List[float]
    confidence_interval: Tuple[float, float]
    horizon: int
    model: str

class ForecasterEngine:
    """EVEZ Forecaster - Time series forecasting"""
    
    def __init__(self):
        self.model_name = "EVEZ-Forecaster-v1"
        self.time_series: Dict[str, List[float]] = {}
        self.models: Dict[str, str] = {}
    
    def add_data(self, series_name: str, values: List[float]):
        """Add time series data"""
        self.time_series[series_name] = values
    
    def moving_average(self, series: List[float], window: int = 3) -> List[float]:
        """Simple moving average"""
        result = []
        for i in range(len(series)):
            if i < window - 1:
                result.append(sum(series[:i+1]) / (i+1))
            else:
                result.append(sum(series[i-window+1:i+1]) / window)
        return result
    
    def exponential_smoothing(self, series: List[float], alpha: float = 0.3) -> List[float]:
        """Exponential smoothing"""
        result = [series[0]]
        for i in range(1, len(series)):
            smoothed = alpha * series[i] + (1 - alpha) * result[-1]
            result.append(smoothed)
        return result
    
    def linear_trend(self, series: List[float]) -> Dict:
        """Fit linear trend"""
        n = len(series)
        x_mean = sum(range(n)) / n
        y_mean = sum(series) / n
        
        numerator = sum((i - x_mean) * (series[i] - y_mean) for i in range(n))
        denominator = sum((i - x_mean) ** 2 for i in range(n))
        
        slope = numerator / denominator if denominator != 0 else 0
        intercept = y_mean - slope * x_mean
        
        return {"slope": slope, "intercept": intercept}
    
    def forecast(self, series_name: str, horizon: int = 5, method: str = "auto") -> Forecast:
        """Generate forecast"""
        if series_name not in self.time_series:
            return Forecast([], (0, 0), horizon, "none")
        
        series = self.time_series[series_name]
        
        # Auto-select method based on data
        if method == "auto":
            if len(series) < 10:
                method = "ma"
            else:
                method = "exp_smooth"
        
        if method == "ma":
            ma = self.moving_average(series, window=min(5, len(series) // 2))
            last_ma = ma[-1]
            predictions = [last_ma] * horizon
            
        elif method == "exp_smooth":
            smoothed = self.exponential_smoothing(series)
            # Simple projection
            trend = self.linear_trend(smoothed)
            predictions = []
            for h in range(1, horizon + 1):
                pred = trend["intercept"] + trend["slope"] * (len(series) + h)
                predictions.append(pred)
        
        else:  # linear
            trend = self.linear_trend(series)
            predictions = []
            for h in range(1, horizon + 1):
                pred = trend["intercept"] + trend["slope"] * (len(series) + h)
                predictions.append(pred)
        
        # Confidence interval (simplified)
        std_dev = math.sqrt(sum((s - sum(series)/len(series))**2 for s in series) / len(series))
        confidence = (std_dev * 1.96, std_dev * 2.58)  # 95% and 99%
        
        self.models[series_name] = method
        
        return Forecast(
            predictions=predictions,
            confidence_interval=confidence,
            horizon=horizon,
            model=method
        )
    
    def detect_anomalies(self, series_name: str, threshold: float = 2.0) -> List[int]:
        """Detect anomalies using z-score"""
        if series_name not in self.time_series:
            return []
        
        series = self.time_series[series_name]
        mean = sum(series) / len(series)
        std = math.sqrt(sum((s - mean)**2 for s in series) / len(series))
        
        anomalies = []
        for i, s in enumerate(series):
            z_score = abs((s - mean) / std) if std > 0 else 0
            if z_score > threshold:
                anomalies.append(i)
        
        return anomalies
    
    def get_status(self) -> Dict:
        return {
            "model": self.model_name,
            "series": len(self.time_series),
            "models": self.models
        }


# Demo
if __name__ == "__main__":
    fc = ForecasterEngine()
    print("=== EVEZ Forecaster ===")
    
    # Add data
    data = [10, 12, 11, 14, 13, 16, 15, 18, 17, 20, 19, 22, 21, 24, 23]
    fc.add_data("revenue", data)
    
    # Forecast
    forecast = fc.forecast("revenue", horizon=5)
    print(f"Forecast: {forecast.predictions}")
    print(f"Model: {forecast.model}, CI: {forecast.confidence_interval}")
    
    # Anomalies
    anomalies = fc.detect_anomalies("revenue", threshold=2.0)
    print(f"Anomalies at indices: {anomalies}")
    
    print(json.dumps(fc.get_status(), indent=2))