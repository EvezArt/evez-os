#!/usr/bin/env python3
"""
EVEZ Analyzer - Data analysis, statistics, reporting
Statistical tests, aggregation, metrics, report generation
"""

import json
import random
import math
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from collections import Counter

@dataclass
class Statistic:
    name: str
    value: float
    description: str

@dataclass
class AnalysisReport:
    title: str
    timestamp: str
    statistics: List[Statistic]
    insights: List[str]
    recommendations: List[str]

class AnalyzerEngine:
    """EVEZ Analyzer - Statistical analysis and reporting"""
    
    def __init__(self):
        self.model_name = "EVEZ-Analyzer-v1"
        self.datasets: Dict[str, List[float]] = {}
        self.reports: List[AnalysisReport] = []
    
    def add_dataset(self, name: str, values: List[float]):
        """Add a dataset for analysis"""
        self.datasets[name] = values
    
    def compute_statistics(self, data: List[float]) -> List[Statistic]:
        """Compute basic statistics"""
        if not data:
            return []
        
        n = len(data)
        mean = sum(data) / n
        sorted_data = sorted(data)
        median = sorted_data[n // 2] if n % 2 == 1 else (sorted_data[n//2 - 1] + sorted_data[n//2]) / 2
        
        # Standard deviation
        variance = sum((x - mean) ** 2 for x in data) / n
        std_dev = math.sqrt(variance)
        
        # Min/Max
        min_val = min(data)
        max_val = max(data)
        
        # Range
        range_val = max_val - min_val
        
        return [
            Statistic("count", n, "Number of observations"),
            Statistic("mean", mean, "Average value"),
            Statistic("median", median, "Middle value"),
            Statistic("std_dev", std_dev, "Standard deviation"),
            Statistic("min", min_val, "Minimum value"),
            Statistic("max", max_val, "Maximum value"),
            Statistic("range", range_val, "Range (max - min)")
        ]
    
    def correlation(self, data1: List[float], data2: List[float]) -> float:
        """Calculate Pearson correlation coefficient"""
        if len(data1) != len(data2) or len(data1) < 2:
            return 0.0
        
        n = len(data1)
        mean1 = sum(data1) / n
        mean2 = sum(data2) / n
        
        numerator = sum((data1[i] - mean1) * (data2[i] - mean2) for i in range(n))
        
        sum1 = math.sqrt(sum((x - mean1) ** 2 for x in data1))
        sum2 = math.sqrt(sum((x - mean2) ** 2 for x in data2))
        
        if sum1 == 0 or sum2 == 0:
            return 0.0
        
        return numerator / (sum1 * sum2)
    
    def percentile(self, data: List[float], p: float) -> float:
        """Calculate percentile"""
        sorted_data = sorted(data)
        k = (len(sorted_data) - 1) * p / 100
        f = math.floor(k)
        c = math.ceil(k)
        
        if f == c:
            return sorted_data[int(k)]
        
        d0 = sorted_data[int(f)] * (c - k)
        d1 = sorted_data[int(c)] * (k - f)
        return d0 + d1
    
    def frequency_analysis(self, data: List[Any]) -> Dict:
        """Frequency analysis for categorical data"""
        counter = Counter(data)
        total = len(data)
        
        return {
            "total": total,
            "unique": len(counter),
            "distribution": {k: {"count": v, "percentage": v/total*100} for k, v in counter.most_common(10)}
        }
    
    def chi_square_test(self, observed: List[float], expected: List[float]) -> Dict:
        """Chi-square test for independence"""
        if len(observed) != len(expected):
            return {"error": "Length mismatch"}
        
        chi_sq = sum((o - e) ** 2 / e for o, e in zip(observed, expected) if e > 0)
        df = len(observed) - 1
        
        # Simplified p-value approximation
        p_value = math.exp(-chi_sq / 2)  # Very rough approximation
        
        return {
            "chi_square": chi_sq,
            "degrees_of_freedom": df,
            "p_value": p_value,
            "significant": p_value < 0.05
        }
    
    def detect_outliers(self, data: List[float], method: str = "iqr") -> List[int]:
        """Detect outliers"""
        if method == "iqr":
            sorted_data = sorted(data)
            q1 = self.percentile(data, 25)
            q3 = self.percentile(data, 75)
            iqr = q3 - q1
            
            lower = q1 - 1.5 * iqr
            upper = q3 + 1.5 * iqr
            
            return [i for i, x in enumerate(data) if x < lower or x > upper]
        
        elif method == "zscore":
            mean = sum(data) / len(data)
            std = math.sqrt(sum((x - mean) ** 2 for x in data) / len(data))
            
            return [i for i, x in enumerate(data) if abs((x - mean) / std) > 3]
        
        return []
    
    def generate_report(self, dataset_name: str) -> AnalysisReport:
        """Generate comprehensive analysis report"""
        if dataset_name not in self.datasets:
            return AnalysisReport("Error", "", [], ["Dataset not found"], [])
        
        data = self.datasets[dataset_name]
        stats = self.compute_statistics(data)
        outliers = self.detect_outliers(data)
        
        # Generate insights
        insights = []
        insights.append(f"Dataset contains {len(data)} observations")
        
        mean_stat = next((s for s in stats if s.name == "mean"), None)
        if mean_stat:
            insights.append(f"Average value is {mean_stat.value:.2f}")
        
        if outliers:
            insights.append(f"Found {len(outliers)} potential outliers")
        
        # Recommendations
        recommendations = []
        if len(outliers) > len(data) * 0.1:
            recommendations.append("High outlier percentage - consider data cleaning")
        if len(data) < 30:
            recommendations.append("Small sample size - consider collecting more data")
        
        report = AnalysisReport(
            title=f"Analysis Report: {dataset_name}",
            timestamp=datetime.utcnow().isoformat() + "Z",
            statistics=stats,
            insights=insights,
            recommendations=recommendations
        )
        
        self.reports.append(report)
        return report
    
    def get_status(self) -> Dict:
        return {
            "model": self.model_name,
            "datasets": len(self.datasets),
            "reports": len(self.reports)
        }


# Demo
if __name__ == "__main__":
    an = AnalyzerEngine()
    print("=== EVEZ Analyzer ===")
    
    # Add dataset
    data = [random.randint(1, 100) for _ in range(50)]
    an.add_dataset("sales", data)
    
    # Statistics
    stats = an.compute_statistics(data)
    print("Statistics:")
    for s in stats[:5]:
        print(f"  {s.name}: {s.value:.2f}")
    
    # Outliers
    outliers = an.detect_outliers(data)
    print(f"Outliers: {len(outliers)} found")
    
    # Report
    report = an.generate_report("sales")
    print(f"\nInsights: {report.insights}")
    
    print(json.dumps(an.get_status(), indent=2))