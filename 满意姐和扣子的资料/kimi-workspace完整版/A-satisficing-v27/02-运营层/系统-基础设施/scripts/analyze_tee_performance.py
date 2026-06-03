#!/usr/bin/env python3
"""
TEE Performance Analysis Script
Compares performance metrics for confidential computing (TEE) vs non-TEE environments
"""

import json
import sys
import re
from datetime import datetime

# Expected performance baseline (non-TEE Standard_D8s_v3)
NON_TEE_BASELINE = {
    "llama2_7b": {
        "tokens_per_sec": 8.5,  # Expected tokens/sec on Standard_D8s_v3
        "memory_bandwidth_gb_s": 25.0,
        "model_load_time_sec": 45.0,
    }
}

# TEE overhead threshold (< 10% as per requirements)
TEE_OVERHEAD_THRESHOLD = 0.10  # 10%

def parse_benchmark_results(result_file):
    """Parse benchmark results from text file"""
    results = {
        "tokens_per_sec": None,
        "memory_bandwidth_gb_s": None,
        "model_load_time_sec": None
    }
    
    with open(result_file, 'r') as f:
        content = f.read()
    
    # Parse tokens per second
    tokens_match = re.search(r'Tokens per second: ([\d.]+)', content)
    if tokens_match:
        results["tokens_per_sec"] = float(tokens_match.group(1))
    
    # Parse memory bandwidth
    bw_match = re.search(r'Memory bandwidth test: ([\d.]+) GB/s', content)
    if bw_match:
        results["memory_bandwidth_gb_s"] = float(bw_match.group(1))
    
    # Parse model load time
    load_match = re.search(r'Model load time: ([\d.]+)s', content)
    if load_match:
        results["model_load_time_sec"] = float(load_match.group(1))
    
    return results

def calculate_overhead(tee_value, baseline_value):
    """Calculate performance overhead percentage"""
    if tee_value is None or baseline_value is None:
        return None
    # For metrics where higher is better (tokens/sec, bandwidth)
    if baseline_value > 0:
        overhead = (baseline_value - tee_value) / baseline_value
        return overhead
    return None

def analyze_performance(tee_results):
    """Analyze TEE performance vs baseline"""
    baseline = NON_TEE_BASELINE["llama2_7b"]
    
    analysis = {
        "timestamp": datetime.now().isoformat(),
        "metrics": {},
        "passed_threshold": True,
        "summary": ""
    }
    
    # Analyze tokens per second
    if tee_results["tokens_per_sec"]:
        overhead = calculate_overhead(tee_results["tokens_per_sec"], baseline["tokens_per_sec"])
        analysis["metrics"]["tokens_per_sec"] = {
            "tee_value": tee_results["tokens_per_sec"],
            "baseline": baseline["tokens_per_sec"],
            "overhead": overhead,
            "overhead_percent": overhead * 100 if overhead else None,
            "within_threshold": overhead < TEE_OVERHEAD_THRESHOLD if overhead else None
        }
        if overhead and overhead >= TEE_OVERHEAD_THRESHOLD:
            analysis["passed_threshold"] = False
    
    # Analyze memory bandwidth
    if tee_results["memory_bandwidth_gb_s"]:
        overhead = calculate_overhead(tee_results["memory_bandwidth_gb_s"], baseline["memory_bandwidth_gb_s"])
        analysis["metrics"]["memory_bandwidth_gb_s"] = {
            "tee_value": tee_results["memory_bandwidth_gb_s"],
            "baseline": baseline["memory_bandwidth_gb_s"],
            "overhead": overhead,
            "overhead_percent": overhead * 100 if overhead else None,
            "within_threshold": overhead < TEE_OVERHEAD_THRESHOLD if overhead else None
        }
        if overhead and overhead >= TEE_OVERHEAD_THRESHOLD:
            analysis["passed_threshold"] = False
    
    # Analyze model load time (lower is better)
    if tee_results["model_load_time_sec"]:
        # For load time, overhead = (tee - baseline) / baseline
        overhead = (tee_results["model_load_time_sec"] - baseline["model_load_time_sec"]) / baseline["model_load_time_sec"]
        analysis["metrics"]["model_load_time_sec"] = {
            "tee_value": tee_results["model_load_time_sec"],
            "baseline": baseline["model_load_time_sec"],
            "overhead": overhead,
            "overhead_percent": overhead * 100,
            "within_threshold": overhead < TEE_OVERHEAD_THRESHOLD
        }
        if overhead >= TEE_OVERHEAD_THRESHOLD:
            analysis["passed_threshold"] = False
    
    # Generate summary
    if analysis["passed_threshold"]:
        analysis["summary"] = "✓ TEE Performance Validation PASSED: All metrics within 10% overhead threshold"
    else:
        analysis["summary"] = "✗ TEE Performance Validation FAILED: Some metrics exceeded 10% overhead threshold"
    
    return analysis

def print_analysis(analysis):
    """Print formatted analysis results"""
    print("\n" + "="*70)
    print(" TEE PERFORMANCE VALIDATION REPORT")
    print("="*70)
    print(f"Timestamp: {analysis['timestamp']}")
    print(f"Threshold: {TEE_OVERHEAD_THRESHOLD*100}% overhead")
    print("-"*70)
    
    for metric, data in analysis["metrics"].items():
        print(f"\n{metric}:")
        print(f"  TEE Value:    {data['tee_value']:.2f}")
        print(f"  Baseline:     {data['baseline']:.2f}")
        if data['overhead_percent'] is not None:
            print(f"  Overhead:     {data['overhead_percent']:.1f}%")
            status = "✓ PASS" if data['within_threshold'] else "✗ FAIL"
            print(f"  Status:       {status}")
    
    print("\n" + "-"*70)
    print(analysis["summary"])
    print("="*70)

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 analyze_tee_performance.py <benchmark_result_file>")
        sys.exit(1)
    
    result_file = sys.argv[1]
    
    try:
        tee_results = parse_benchmark_results(result_file)
        analysis = analyze_performance(tee_results)
        print_analysis(analysis)
        
        # Save detailed report
        report_file = result_file.replace('.txt', '_analysis.json')
        with open(report_file, 'w') as f:
            json.dump(analysis, f, indent=2)
        print(f"\nDetailed report saved to: {report_file}")
        
        # Exit with appropriate code
        sys.exit(0 if analysis["passed_threshold"] else 1)
        
    except FileNotFoundError:
        print(f"Error: Could not find benchmark result file: {result_file}")
        sys.exit(1)
    except Exception as e:
        print(f"Error analyzing results: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
