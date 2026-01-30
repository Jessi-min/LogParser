import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

def extract_ddr_prime_data(log_file_path):
    """
    Extract DDR_Prime event data from the log file
    """
    data = []
    
    try:
        with open(log_file_path, 'r') as file:
            for line in file:
                # Skip lines containing "kworker"
                if "kworker" in line:
                    continue
                
                # Find ddr:prime events
                match = re.search(r'ddr:prime CPU:(\d+), CF:(\d+), MF:(\d+), IPM:(\d+), STL:(\d+) SSI:(\d+), IT:(\d+), CT:(\d+), M:(\d+)', line)
                if match:
                    cpu, cf, mf, ipm, stl, ssi, it, ct, m = map(int, match.groups())
                    
                    # Extract timestamp from the format [188704574]
                    timestamp_match = re.search(r'\[(\d{9})\].*ddr:prime', line)
                    if timestamp_match:
                        # Extract first 3 digits as timestamp
                        timestamp_str = timestamp_match.group(1)
                        timestamp = int(timestamp_str[:3])
                        data.append({
                            'Timestamp': timestamp,
                            'CPU': cpu,
                            'CF': cf,
                            'MF': mf,
                            'IPM': ipm,
                            'STL': stl,
                            'SSI': ssi,
                            'IT': it,
                            'CT': ct,
                            'M': m
                        })
    except FileNotFoundError:
        print(f"Error: File {log_file_path} not found")
        return pd.DataFrame()
    
    return pd.DataFrame(data)

def create_broken_axis_plot(df):
    """
    Create a plot with broken axis for better visualization of metrics with different scales
    """
    if df.empty:
        print("No data to plot")
        return
    
    # Sort by timestamp to ensure correct order
    df = df.sort_values('Timestamp')
    
    # Create figure with multiple subplots for different value ranges
    fig = plt.figure(figsize=(14, 10))
    gs = GridSpec(3, 1, height_ratios=[1, 1, 1], hspace=0.3)
    
    # Create three subplots for different value ranges
    ax1 = fig.add_subplot(gs[0])  # High range (SSI)
    ax2 = fig.add_subplot(gs[1])  # Mid range (MF, IPM)
    ax3 = fig.add_subplot(gs[2])  # Low range (CF, IT, CT, M)
    
    # Plot SSI in high range subplot
    ax1.plot(df['Timestamp'], df['SSI'], 'r-', label='SSI')
    ax1.plot(df['Timestamp'], df['STL'], 'b--', label='STL')
    ax1.set_title('High Range: System Status Indicator & Stall')
    ax1.legend()
    ax1.grid(True)
    
    # Plot MF and IPM in mid range subplot
    ax2.plot(df['Timestamp'], df['MF'], 'g-', label='MF')
    ax2.plot(df['Timestamp'], df['IPM'], 'b-', label='IPM')
    ax2.set_title('Mid Range: Memory Frequency and Instructions Per Millisecond')
    ax2.legend()
    ax2.grid(True)
    
    # Plot CF, IT, CT, M in low range subplot
    ax3.plot(df['Timestamp'], df['CF'], 'c-', label='CF')
    ax3.plot(df['Timestamp'], df['IT'], 'm-', label='IT')
    ax3.plot(df['Timestamp'], df['CT'], 'y-', label='CT')
    ax3.plot(df['Timestamp'], df['M'], 'k-', label='M')
    ax3.set_title('Low Range: Clock Frequency, Idle Time, Compute Time, Miscellaneous')
    ax3.set_xlabel('Timestamp (first 3 digits)')
    ax3.legend()
    ax3.grid(True)
    
    # Add a common y-label
    fig.text(0.04, 0.5, 'Value', va='center', rotation='vertical', fontsize=12)
    
    # Add main title
    fig.suptitle('DDR_Prime Event Metrics by Value Range', fontsize=16)
    
    plt.tight_layout(rect=[0.05, 0, 1, 0.95])  # Adjust layout
    plt.savefig('ddr_prime_broken_trend.png')
    plt.show()

def main():
    # Log file path
    log_file_path = 'ftrace/adcvs_memlat_v2/cpucp_log.txt'
    
    # Extract data
    df = extract_ddr_prime_data(log_file_path)
    
    if not df.empty:
        print(f"Extracted {len(df)} data points")
        
        # Save data to CSV file
        df.to_csv('ddr_prime_data.csv', index=False)
        print("Data saved to ddr_prime_data.csv")
        
        # Create broken axis plot
        create_broken_axis_plot(df)
    else:
        print("No data extracted from the log file")

if __name__ == "__main__":
    main()