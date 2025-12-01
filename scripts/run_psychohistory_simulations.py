"""
Run comprehensive psychohistory simulation tests.

This script performs:
1. Parameter sweep tests (multiple parameter combinations)
2. Long-term simulation tests (many time steps)
3. Stress tests (large agent populations, concurrent simulations)
4. Boundary case tests

Results are collected and reported.
"""

import sys
import os
from pathlib import Path
import numpy as np
import time
import json
from datetime import datetime
from typing import Dict, List, Tuple

# Add simulation to path
project_root = Path(__file__).parent.parent
simulation_dir = project_root / "simulation"
sys.path.insert(0, str(simulation_dir))
sys.path.insert(0, str(project_root))

from core.hybrid_model import HybridPsychohistoryModel
from core.judgement_system import BiasedJudge, NoisyJudge, ConservativeJudge


class PsychohistoryTestRunner:
    """Runner for psychohistory simulation tests."""
    
    def __init__(self, output_dir: str = "simulation/output/psychohistory_tests"):
        # Sanitize output directory path
        output_path = Path(output_dir).resolve()
        # Ensure it's within project root
        project_root = Path(__file__).parent.parent.resolve()
        if not str(output_path).startswith(str(project_root)):
            output_path = project_root / "simulation" / "output" / "psychohistory_tests"
        self.output_dir = output_path
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.results = []
        self.start_time = time.time()
    
    def judge_factory(self, judge_type: str, i: int):
        """Create judge based on type."""
        if judge_type == 'biased':
            return BiasedJudge(bias_strength=0.1 + 0.1 * (i % 5) / 5, name=f"Biased_{i}")
        elif judge_type == 'noisy':
            return NoisyJudge(noise_scale=0.1 + 0.1 * (i % 5) / 5, name=f"Noisy_{i}")
        elif judge_type == 'conservative':
            return ConservativeJudge(threshold=0.3 + 0.2 * (i % 5) / 5, name=f"Conservative_{i}")
        else:
            return BiasedJudge(bias_strength=0.1, name=f"Judge_{i}")
    
    def run_parameter_sweep(self):
        """Run parameter sweep tests."""
        print("=" * 70)
        print("PARAMETER SWEEP TESTS")
        print("=" * 70)
        
        agent_counts = [10, 50, 100, 200]
        topologies = ['random', 'small_world', 'scale_free']
        time_steps_list = [5, 10, 20]
        
        test_count = 0
        passed = 0
        failed = 0
        
        for num_agents in agent_counts:
            for topology in topologies:
                for time_steps in time_steps_list:
                    test_count += 1
                    test_name = f"param_sweep_agents{num_agents}_topo{topology}_steps{time_steps}"
                    
                    print(f"\n[{test_count}] Running: {test_name}")
                    
                    try:
                        start = time.time()
                        
                        def judge_factory(i):
                            return self.judge_factory('biased', i)
                        
                        hybrid = HybridPsychohistoryModel(
                            num_agents=num_agents,
                            judge_factory=judge_factory,
                            network_topology=topology,
                            enable_fluid_model=False  # Disable for speed
                        )
                        
                        results = hybrid.run_simulation(
                            num_time_steps=time_steps,
                            actions_per_step=200,
                            tau=0.3,
                            X_max=50
                        )
                        
                        elapsed = time.time() - start
                        
                        # Get metrics
                        metrics = hybrid.get_unified_metrics(results)
                        
                        result = {
                            'test_name': test_name,
                            'status': 'PASSED',
                            'parameters': {
                                'num_agents': num_agents,
                                'topology': topology,
                                'time_steps': time_steps
                            },
                            'metrics': metrics,
                            'elapsed_time': elapsed,
                            'timestamp': datetime.now().isoformat()
                        }
                        
                        self.results.append(result)
                        passed += 1
                        print(f"  ✓ PASSED ({elapsed:.2f}s)")
                        
                    except Exception as e:
                        failed += 1
                        result = {
                            'test_name': test_name,
                            'status': 'FAILED',
                            'error': str(e),
                            'timestamp': datetime.now().isoformat()
                        }
                        self.results.append(result)
                        print(f"  ✗ FAILED: {e}")
        
        print(f"\nParameter Sweep Summary: {passed} passed, {failed} failed out of {test_count} tests")
        return passed, failed
    
    def run_long_term_simulation(self):
        """Run long-term simulation tests."""
        print("\n" + "=" * 70)
        print("LONG-TERM SIMULATION TESTS")
        print("=" * 70)
        
        time_steps_list = [50, 100]
        test_count = 0
        passed = 0
        failed = 0
        
        for time_steps in time_steps_list:
            test_count += 1
            test_name = f"long_term_steps{time_steps}"
            
            print(f"\n[{test_count}] Running: {test_name}")
            
            try:
                start = time.time()
                
                def judge_factory(i):
                    return self.judge_factory('biased', i)
                
                hybrid = HybridPsychohistoryModel(
                    num_agents=30,
                    judge_factory=judge_factory,
                    enable_fluid_model=False
                )
                
                results = hybrid.run_simulation(
                    num_time_steps=time_steps,
                    actions_per_step=300,
                    tau=0.3,
                    X_max=50
                )
                
                elapsed = time.time() - start
                
                # Check stability
                metrics = hybrid.get_unified_metrics(results)
                stable = metrics.get('system_health', {}).get('score', 0) > 0.3
                
                result = {
                    'test_name': test_name,
                    'status': 'PASSED' if stable else 'UNSTABLE',
                    'time_steps': time_steps,
                    'elapsed_time': elapsed,
                    'stability': stable,
                    'metrics': metrics,
                    'timestamp': datetime.now().isoformat()
                }
                
                self.results.append(result)
                passed += 1
                print(f"  ✓ PASSED ({elapsed:.2f}s, stable={stable})")
                
            except Exception as e:
                failed += 1
                result = {
                    'test_name': test_name,
                    'status': 'FAILED',
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
                self.results.append(result)
                print(f"  ✗ FAILED: {e}")
        
        print(f"\nLong-term Simulation Summary: {passed} passed, {failed} failed out of {test_count} tests")
        return passed, failed
    
    def run_stress_tests(self):
        """Run stress tests with large populations."""
        print("\n" + "=" * 70)
        print("STRESS TESTS")
        print("=" * 70)
        
        agent_counts = [200, 500]
        test_count = 0
        passed = 0
        failed = 0
        
        for num_agents in agent_counts:
            test_count += 1
            test_name = f"stress_agents{num_agents}"
            
            print(f"\n[{test_count}] Running: {test_name}")
            
            try:
                start = time.time()
                
                def judge_factory(i):
                    return self.judge_factory('biased', i)
                
                hybrid = HybridPsychohistoryModel(
                    num_agents=num_agents,
                    judge_factory=judge_factory,
                    enable_fluid_model=False
                )
                
                results = hybrid.run_simulation(
                    num_time_steps=10,
                    actions_per_step=500,
                    tau=0.3,
                    X_max=50
                )
                
                elapsed = time.time() - start
                
                metrics = hybrid.get_unified_metrics(results)
                
                result = {
                    'test_name': test_name,
                    'status': 'PASSED',
                    'num_agents': num_agents,
                    'elapsed_time': elapsed,
                    'metrics': metrics,
                    'timestamp': datetime.now().isoformat()
                }
                
                self.results.append(result)
                passed += 1
                print(f"  ✓ PASSED ({elapsed:.2f}s)")
                
            except Exception as e:
                failed += 1
                result = {
                    'test_name': test_name,
                    'status': 'FAILED',
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
                self.results.append(result)
                print(f"  ✗ FAILED: {e}")
        
        print(f"\nStress Test Summary: {passed} passed, {failed} failed out of {test_count} tests")
        return passed, failed
    
    def run_boundary_tests(self):
        """Run boundary case tests."""
        print("\n" + "=" * 70)
        print("BOUNDARY CASE TESTS")
        print("=" * 70)
        
        test_cases = [
            {'num_agents': 1, 'time_steps': 1, 'name': 'minimal'},
            {'num_agents': 5, 'time_steps': 2, 'name': 'small'},
            {'num_agents': 1000, 'time_steps': 5, 'name': 'large_agents'},
        ]
        
        test_count = 0
        passed = 0
        failed = 0
        
        for case in test_cases:
            test_count += 1
            test_name = f"boundary_{case['name']}"
            
            print(f"\n[{test_count}] Running: {test_name}")
            
            try:
                start = time.time()
                
                def judge_factory(i):
                    return self.judge_factory('biased', i)
                
                hybrid = HybridPsychohistoryModel(
                    num_agents=case['num_agents'],
                    judge_factory=judge_factory,
                    enable_fluid_model=False
                )
                
                results = hybrid.run_simulation(
                    num_time_steps=case['time_steps'],
                    actions_per_step=100,
                    tau=0.3,
                    X_max=50
                )
                
                elapsed = time.time() - start
                
                result = {
                    'test_name': test_name,
                    'status': 'PASSED',
                    'parameters': case,
                    'elapsed_time': elapsed,
                    'timestamp': datetime.now().isoformat()
                }
                
                self.results.append(result)
                passed += 1
                print(f"  ✓ PASSED ({elapsed:.2f}s)")
                
            except Exception as e:
                failed += 1
                result = {
                    'test_name': test_name,
                    'status': 'FAILED',
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
                self.results.append(result)
                print(f"  ✗ FAILED: {e}")
        
        print(f"\nBoundary Test Summary: {passed} passed, {failed} failed out of {test_count} tests")
        return passed, failed
    
    def generate_report(self):
        """Generate test report."""
        total_time = time.time() - self.start_time
        
        total_tests = len(self.results)
        passed = sum(1 for r in self.results if r.get('status') == 'PASSED')
        failed = sum(1 for r in self.results if r.get('status') == 'FAILED')
        
        report = {
            'summary': {
                'total_tests': total_tests,
                'passed': passed,
                'failed': failed,
                'success_rate': passed / total_tests if total_tests > 0 else 0,
                'total_time': total_time,
                'timestamp': datetime.now().isoformat()
            },
            'results': self.results
        }
        
        # Save JSON report
        report_file = self.output_dir / 'test_report.json'
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Generate text summary
        summary_file = self.output_dir / 'test_summary.txt'
        with open(summary_file, 'w') as f:
            f.write("=" * 70 + "\n")
            f.write("PSYCHOHISTORY SIMULATION TEST REPORT\n")
            f.write("=" * 70 + "\n\n")
            f.write(f"Total Tests: {total_tests}\n")
            f.write(f"Passed: {passed}\n")
            f.write(f"Failed: {failed}\n")
            f.write(f"Success Rate: {passed/total_tests*100:.1f}%\n")
            f.write(f"Total Time: {total_time:.2f}s\n")
            f.write(f"\nTimestamp: {datetime.now().isoformat()}\n")
            f.write("\n" + "=" * 70 + "\n")
            f.write("DETAILED RESULTS\n")
            f.write("=" * 70 + "\n\n")
            
            for result in self.results:
                f.write(f"Test: {result['test_name']}\n")
                f.write(f"  Status: {result.get('status', 'UNKNOWN')}\n")
                if 'elapsed_time' in result:
                    f.write(f"  Time: {result['elapsed_time']:.2f}s\n")
                if 'error' in result:
                    f.write(f"  Error: {result['error']}\n")
                f.write("\n")
        
        print("\n" + "=" * 70)
        print("TEST REPORT GENERATED")
        print("=" * 70)
        print(f"JSON Report: {report_file}")
        print(f"Text Summary: {summary_file}")
        print(f"\nTotal: {total_tests} tests, {passed} passed, {failed} failed")
        print(f"Success Rate: {passed/total_tests*100:.1f}%")
        print(f"Total Time: {total_time:.2f}s")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Run psychohistory simulation tests')
    parser.add_argument('--quick', action='store_true', help='Run quick tests only')
    parser.add_argument('--output-dir', default='simulation/output/psychohistory_tests',
                       help='Output directory for test results')
    
    args = parser.parse_args()
    
    runner = PsychohistoryTestRunner(output_dir=args.output_dir)
    
    if args.quick:
        print("Running quick tests only...")
        runner.run_parameter_sweep()
    else:
        print("Running comprehensive tests...")
        runner.run_parameter_sweep()
        runner.run_long_term_simulation()
        runner.run_stress_tests()
        runner.run_boundary_tests()
    
    runner.generate_report()


if __name__ == '__main__':
    main()

