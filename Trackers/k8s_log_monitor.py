#!/usr/bin/env python3
"""
Kubernetes Pod Log Monitor for DataFlow Timing
Monitors k8s pod logs and extracts DataFlow timing information to CSV
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

class DataFlowTracker:
    def __init__(self, csv_file='dataflow_timing.csv'):
        self.csv_file = csv_file
        self.dataflows = defaultdict(dict)  # {flow_id: {state: timestamp}}
        self.completed_flows = set()  # Track flows that have been saved to CSV
        self.lock = threading.Lock()
        
        # Initialize CSV file with headers
        self.init_csv()
        
    def init_csv(self):
        """Initialize CSV file with headers"""
        try:
            with open(self.csv_file, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['flow_id', 'received_time', 'started_time', 'completed_time', 'received_to_started_seconds', 'started_to_completed_seconds', 'total_duration_seconds'])
            print(f"Initialized CSV file: {self.csv_file}")
        except Exception as e:
            print(f"Error initializing CSV file: {e}")
            sys.exit(1)
    
    def parse_log_line(self, line):
        """Parse a log line and extract DataFlow information"""
        # Pattern to match DataFlow state changes
        pattern = r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+)\s+.*DataFlow\s+([a-f0-9-]+)\s+is\s+now\s+in\s+state\s+(\w+)'
        
        match = re.search(pattern, line)
        if match:
            timestamp_str, flow_id, state = match.groups()
            try:
                # Parse timestamp
                timestamp = datetime.fromisoformat(timestamp_str.rstrip('Z'))
                return flow_id, state, timestamp
            except ValueError:
                # Handle microseconds with more than 6 digits
                timestamp_str = re.sub(r'\.(\d{6})\d*', r'.\1', timestamp_str)
                timestamp = datetime.fromisoformat(timestamp_str.rstrip('Z'))
                return flow_id, state, timestamp
        
        return None, None, None
    
    def process_dataflow_event(self, flow_id, state, timestamp):
        """Process a DataFlow state change event"""
        with self.lock:
            # Skip if this flow has already been completed and saved
            if flow_id in self.completed_flows:
                return
            
            # Store the state timestamp
            if state not in self.dataflows[flow_id]:
                self.dataflows[flow_id][state] = timestamp
                print(f"[{timestamp}] Flow {flow_id[:8]}... -> {state}")
            
            # Check if we have all required states for this flow
            flow_data = self.dataflows[flow_id]
            if 'RECEIVED' in flow_data and 'STARTED' in flow_data and 'COMPLETED' in flow_data:
                self.save_to_csv(flow_id, flow_data)
                self.completed_flows.add(flow_id)
                # Clean up to save memory
                del self.dataflows[flow_id]
    
    def save_to_csv(self, flow_id, flow_data):
        """Save completed DataFlow timing to CSV"""
        try:
            received_time = flow_data['RECEIVED']
            started_time = flow_data['STARTED']
            completed_time = flow_data['COMPLETED']
            
            # Calculate durations in seconds
            received_to_started = (started_time - received_time).total_seconds()
            started_to_completed = (completed_time - started_time).total_seconds()
            total_duration = (completed_time - received_time).total_seconds()
            
            with open(self.csv_file, 'a', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([
                    flow_id,
                    received_time.isoformat(),
                    started_time.isoformat(),
                    completed_time.isoformat(),
                    round(received_to_started, 3),
                    round(started_to_completed, 3),
                    round(total_duration, 3)
                ])
            
            print(f"Saved flow {flow_id[:8]}... - Queue: {received_to_started:.3f}s, Process: {started_to_completed:.3f}s, Total: {total_duration:.3f}s")
            
        except Exception as e:
            print(f"Error saving to CSV: {e}")

class KubernetesPodLogMonitor:
    def __init__(self, pod_name, namespace='default', container=None):
        self.pod_name = pod_name
        self.namespace = namespace
        self.container = container
        self.tracker = DataFlowTracker()
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
        print("Monitoring DataFlow state changes... Press Ctrl+C to stop\n")
        
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
                    flow_id, state, timestamp = self.tracker.parse_log_line(line)
                    if flow_id and state and timestamp:
                        self.tracker.process_dataflow_event(flow_id, state, timestamp)
            
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
            pending_count = len(self.tracker.dataflows)
            
        print(f"\nMonitoring stopped.")
        print(f"Completed flows saved: {completed_count}")
        print(f"Pending flows (incomplete): {pending_count}")
        print(f"CSV file: {self.tracker.csv_file}")

def signal_handler(signum, frame):
    """Handle interrupt signals"""
    print("\nReceived interrupt signal. Stopping monitor...")
    global monitor
    if monitor:
        monitor.cleanup()
    sys.exit(0)

def main():
    parser = argparse.ArgumentParser(description='Monitor Kubernetes pod logs for DataFlow timing')
    parser.add_argument('pod_name', help='Name of the Kubernetes pod')
    parser.add_argument('-n', '--namespace', default='default', help='Kubernetes namespace (default: default)')
    parser.add_argument('-c', '--container', help='Container name (if pod has multiple containers)')
    parser.add_argument('-o', '--output', default='dataflow_timing.csv', help='Output CSV file (default: dataflow_timing.csv)')
    
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
