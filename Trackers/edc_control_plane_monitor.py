#!/usr/bin/env python3
"""
EDC Enhanced Timing Monitor - Policy Verification and Contract Signature
Monitors EDC control plane logs and extracts policy verification and contract signature timing
with detailed timestamps for calculation transparency
"""

import re
import csv
import subprocess
import sys
import threading
import time
from datetime import datetime
from collections import defaultdict
import argparse
import signal
import os

class EDCEnhancedTimingTracker:
    def __init__(self, csv_file='edc_enhanced_timing.csv'):
        self.csv_file = csv_file
        self.contract_negotiations = defaultdict(dict)  # {negotiation_id: {state: timestamp}}
        self.completed_flows = set()  # Track complete flows that have been saved
        self.lock = threading.Lock()
        
        # Initialize CSV file with headers
        self.init_csv()
        
    def init_csv(self):
        """Initialize CSV file with headers"""
        try:
            with open(self.csv_file, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([
                    'contract_id',
                    'requested_timestamp',          # Base timestamp for contract signature calculation
                    'agreed_timestamp',             # End timestamp for contract signature / Base for policy verification
                    'verified_timestamp',           # End timestamp for policy verification calculation
                    'contract_signature_time_seconds',  # REQUESTED -> AGREED
                    'policy_verification_time_seconds'  # AGREED -> VERIFIED
                ])
            print(f"Initialized CSV file: {self.csv_file}")
        except Exception as e:
            print(f"Error initializing CSV file: {e}")
            sys.exit(1)
    
    def parse_log_line(self, line):
        """Parse a log line and extract EDC contract negotiation information"""
        
        # Pattern for Contract Negotiation state changes
        contract_pattern = r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+).*ContractNegotiation\s+([a-f0-9-]+)\s+is\s+now\s+in\s+state\s+(\w+)'
        
        # Check for contract negotiation
        match = re.search(contract_pattern, line)
        if match:
            timestamp_str, process_id, state = match.groups()
            timestamp = self.parse_timestamp(timestamp_str)
            if timestamp:
                return 'CONTRACT', process_id, state, timestamp
        
        return None, None, None, None
    
    def parse_timestamp(self, timestamp_str):
        """Parse timestamp string to datetime object"""
        try:
            # Handle microseconds with more than 6 digits
            timestamp_str = re.sub(r'\.(\d{6})\d*', r'.\1', timestamp_str)
            return datetime.fromisoformat(timestamp_str.rstrip('Z'))
        except ValueError as e:
            print(f"Error parsing timestamp {timestamp_str}: {e}")
            return None
    
    def process_contract_event(self, process_id, state, timestamp):
        """Process a Contract Negotiation state change event"""
        with self.lock:
            # Store the state timestamp
            if state not in self.contract_negotiations[process_id]:
                self.contract_negotiations[process_id][state] = timestamp
                print(f"[{timestamp}] Contract {process_id[:8]}... -> {state}")
            
            # Check if we have enough data to calculate timings
            if state == 'VERIFIED' and process_id not in self.completed_flows:
                self.try_save_timing(process_id)
    
    def try_save_timing(self, contract_id):
        """Try to save timing data when we have REQUESTED, AGREED, and VERIFIED states"""
        contract_data = self.contract_negotiations[contract_id]
        
        # Check if we have all required states
        if all(state in contract_data for state in ['REQUESTED', 'AGREED', 'VERIFIED']):
            self.save_timing(contract_id, contract_data)
            self.completed_flows.add(contract_id)
    
    def save_timing(self, contract_id, contract_data):
        """Save contract signature and policy verification timing with detailed timestamps"""
        try:
            requested_time = contract_data['REQUESTED']
            agreed_time = contract_data['AGREED']
            verified_time = contract_data['VERIFIED']
            
            # Calculate specific timings
            contract_signature_time = (agreed_time - requested_time).total_seconds()
            policy_verification_time = (verified_time - agreed_time).total_seconds()
            
            with open(self.csv_file, 'a', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([
                    contract_id,
                    requested_time.isoformat(),     # Base timestamp for contract signature
                    agreed_time.isoformat(),        # End timestamp for contract signature / Base for policy verification
                    verified_time.isoformat(),      # End timestamp for policy verification
                    round(contract_signature_time, 3),
                    round(policy_verification_time, 3)
                ])
            
            print(f"Contract {contract_id[:8]}... - Signature: {contract_signature_time:.3f}s, Policy Verification: {policy_verification_time:.3f}s")
            print(f"  Requested: {requested_time.isoformat()}")
            print(f"  Agreed: {agreed_time.isoformat()}")
            print(f"  Verified: {verified_time.isoformat()}")
            
        except Exception as e:
            print(f"Error saving timing for contract {contract_id}: {e}")

class KubernetesPodLogMonitor:
    def __init__(self, pod_name, namespace='default', container=None):
        self.pod_name = pod_name
        self.namespace = namespace
        self.container = container
        self.tracker = EDCEnhancedTimingTracker()
        self.running = False
        self.process = None
        
    def build_kubectl_command(self):
        """Build kubectl logs command"""
        cmd = ['kubectl', 'logs', '-f', self.pod_name, '-n', self.namespace]
        if self.container:
            cmd.extend(['-c', self.container])
        return cmd
    
    def start_monitoring(self):
        """Start monitoring pod logs"""
        cmd = self.build_kubectl_command()
        print(f"Starting log monitoring with command: {' '.join(cmd)}")
        print("Monitoring EDC Contract Signature and Policy Verification timings... Press Ctrl+C to stop")
        print("Calculation details:")
        print("  - contract_signature_time_seconds = agreed_timestamp - requested_timestamp")
        print("  - policy_verification_time_seconds = verified_timestamp - agreed_timestamp")
        print()
        
        self.running = True
        
        try:
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                bufsize=1
            )
            
            # Monitor stdout
            for line in iter(self.process.stdout.readline, ''):
                if not self.running:
                    break
                    
                line = line.strip()
                if line:
                    process_type, process_id, state, timestamp = self.tracker.parse_log_line(line)
                    if process_type == 'CONTRACT' and process_id and state and timestamp:
                        self.tracker.process_contract_event(process_id, state, timestamp)
            
        except subprocess.CalledProcessError as e:
            print(f"Error running kubectl command: {e}")
        except Exception as e:
            print(f"Error monitoring logs: {e}")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources"""
        self.running = False
        if self.process:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
        
        # Print summary
        with self.tracker.lock:
            completed_count = len(self.tracker.completed_flows)
            pending_contracts = len([c for c in self.tracker.contract_negotiations.keys() 
                                   if c not in self.tracker.completed_flows])
            
        print(f"\nMonitoring stopped.")
        print(f"Completed contract timings saved: {completed_count}")
        print(f"Pending contracts (incomplete): {pending_contracts}")
        print(f"CSV file: {self.tracker.csv_file}")
        print("\nCSV Structure:")
        print("  - contract_id: Unique identifier for the contract negotiation")
        print("  - requested_timestamp: When contract entered REQUESTED state")
        print("  - agreed_timestamp: When contract entered AGREED state")
        print("  - verified_timestamp: When contract entered VERIFIED state")
        print("  - contract_signature_time_seconds: Time from REQUESTED to AGREED")
        print("  - policy_verification_time_seconds: Time from AGREED to VERIFIED")

def signal_handler(signum, frame):
    """Handle interrupt signals"""
    print("\nReceived interrupt signal. Stopping monitor...")
    global monitor
    if monitor:
        monitor.cleanup()
    sys.exit(0)

def main():
    parser = argparse.ArgumentParser(description='Monitor Kubernetes pod logs for EDC Contract Signature and Policy Verification timing')
    parser.add_argument('pod_name', help='Name of the Kubernetes pod')
    parser.add_argument('-n', '--namespace', default='default', help='Kubernetes namespace (default: default)')
    parser.add_argument('-c', '--container', help='Container name (if pod has multiple containers)')
    parser.add_argument('-o', '--output', default='edc_enhanced_timing.csv', help='Output CSV file (default: edc_enhanced_timing.csv)')
    
    args = parser.parse_args()
    
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    global monitor
    monitor = KubernetesPodLogMonitor(
        pod_name=args.pod_name,
        namespace=args.namespace,
        container=args.container
    )
    
    # Set custom CSV file if specified
    monitor.tracker.csv_file = args.output
    monitor.tracker.init_csv()
    
    try:
        monitor.start_monitoring()
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    finally:
        monitor.cleanup()

if __name__ == '__main__':
    main()
