import re
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

def extract_ddr_gold_data(log_file_path):
    """
    Extract DDR_Gold event data from the log file
    """
    data = []
    
    try:
        with open(log_file_path, 'r') as file:
            for line in file:
                # Skip lines containing "kworker" or "flatfloor"
                if "kworker" in line or "flatfloor" in line:
                    continue
                
                # Check if this is a ddr:gold event line
                if "ddr:gold" not in line:
                    continue
                    
                # Extract timestamp from the format [188704574]
                # timestamp_match = re.search(r'\[(\d{9})\].*ddr:gold', line)
                timestamp_match = re.search(
                    r'\[(\d{6,})\].*ddr\s*:\s*prime',
                    line,
                    flags=re.IGNORECASE
                )
                if not timestamp_match:
                    print("timestamp")
                    continue
                    
                # Extract first 3 digits as timestamp
                timestamp_str = timestamp_match.group(1)
                timestamp = int(timestamp_str[:3])
                
                # Initialize an entry with timestamp
                entry = {'Timestamp': timestamp}
                
                # Extract all available metrics using individual regex patterns
                metrics = {
                    'CPU': r'CPU:(\d+)',
                    'CF': r'CF:(\d+)',
                    'MF': r'MF:(\d+)',
                    'IPM': r'IPM:(\d+)',
                    'STL': r'STL:(\d+)',
                    'SSI': r'SSI:(\d+)',
                    'IT': r'IT:(\d+)',
                    'CT': r'CT:(\d+)',
                    'M': r'M:(\d+)'
                }
                
                # Extract each metric if available
                for metric, pattern in metrics.items():
                    match = re.search(pattern, line)
                    if match:
                        entry[metric] = int(match.group(1))
                    else:
                        entry[metric] = np.nan  # Use NaN for missing metrics
                
                # Only add entry if at least one metric besides timestamp is present
                if len(entry) > 1:
                    data.append(entry)
    except FileNotFoundError:
        print(f"Error: File {log_file_path} not found")
        # Use sample data if file not found
        sample_data = generate_sample_data()
        if sample_data:
            return sample_data
        return pd.DataFrame()
    
    return pd.DataFrame(data)

def generate_sample_data():
    """
    Generate sample data if log file is not found
    """
    # Sample log lines with some missing metrics
    log_lines = [
        '行     17: [1][3612525147] I: [188694555] ddr:gold CPU:7, CF:866, MF:2092, IPM:1020, STL:100000 SSI:271, IT:55, CT:47, M:123',
        '行     21: [1][3612544378] I: [188695555] ddr:gold CPU:7, CF:866, MF:2092, IPM:1020, STL:100000 SSI:424, IT:44, CT:46, M:114',
        # Line with missing M metric
        '行     25: [1][3612564202] I: [188696573] ddr:gold CPU:7, CF:866, MF:2092, IPM:1020, STL:100000 SSI:115, IT:74, CT:46',
        '行     30: [0][3612582327] I: [188697592] ddr:gold CPU:7, CF:866, MF:2092, IPM:1020, STL:100000 SSI:304, IT:52, CT:46, M:120',
        # Line with missing IT and CT metrics
        '行     34: [1][3612602619] I: [188698574] ddr:gold CPU:7, CF:866, MF:2092, IPM:1020, STL:100000 SSI:165, M:131',
        '行     43: [1][3612645811] I: [188700637] ddr:gold CPU:6, CF:878, MF:2092, IPM:205, STL:100000 SSI:85, IT:79, CT:46, M:141',
        '行     47: [1][3612664364] I: [188701676] ddr:gold CPU:6, CF:878, MF:2092, IPM:205, STL:100000 SSI:182, IT:64, CT:46, M:130',
        # Line with only CPU and CF metrics
        '行     51: [1][3612682379] I: [188702613] ddr:gold CPU:6, CF:878',
        '行     60: [1][3612717807] I: [188704574] ddr:gold CPU:6, CF:878, MF:2092, IPM:205, STL:100000 SSI:195, IT:63, CT:59, M:143',
        '行     64: [1][3612736965] I: [188705572] ddr:gold CPU:6, CF:878, MF:2092, IPM:205, STL:100000 SSI:264, IT:55, CT:59, M:135',
        '行     68: [0][3612754663] I: [188706568] ddr:gold CPU:6, CF:878, MF:2092, IPM:205, STL:100000 SSI:313, IT:51, CT:63, M:134',
        '行     73: [1][3612775959] I: [188707603] ddr:gold CPU:6, CF:878, MF:1353, IPM:205, STL:100000 SSI:2720, IT:10, CT:61, M:90',
        '行     77: [1][3612796083] I: [188708650] ddr:gold CPU:6, CF:1045, MF:2092, IPM:345, STL:100000 SSI:2838, IT:10, CT:62, M:90',
        '行     81: [1][3612813802] I: [188709573] ddr:gold CPU:6, CF:1045, MF:2092, IPM:345, STL:100000 SSI:2725, IT:10, CT:62, M:90',
        '行     86: [0][3612831494] I: [188710570] ddr:gold CPU:6, CF:1045, MF:2092, IPM:345, STL:100000 SSI:6112, IT:5, CT:62, M:85',
        '行     90: [1][3612851577] I: [188711555] ddr:gold CPU:6, CF:1045, MF:2092, IPM:345, STL:100000 SSI:514, IT:39, CT:59, M:119',
        '行     94: [1][3612871654] I: [188712601] ddr:gold CPU:6, CF:1045, MF:3187, IPM:345, STL:100000 SSI:279, IT:54, CT:59, M:134',
        '行    103: [0][3612907692] I: [188714553] ddr:gold CPU:6, CF:1045, MF:2092, IPM:345, STL:100000 SSI:742, IT:30, CT:62, M:111',
        '行    107: [1][3612928992] I: [188715573] ddr:gold CPU:6, CF:1045, MF:2092, IPM:345, STL:100000 SSI:3534, IT:8, CT:62, M:88',
        '行    111: [1][3612949176] I: [188716624] ddr:gold CPU:6, CF:1053, MF:2092, IPM:632, STL:100000 SSI:352, IT:48, CT:49, M:119',
        '行    116: [1][3612967377] I: [188717572] ddr:gold CPU:6, CF:1053, MF:2092, IPM:632, STL:100000 SSI:357, IT:48, CT:59, M:128',
        '行    120: [0][3612985067] I: [188718568] ddr:gold CPU:6, CF:1053, MF:2092, IPM:632, STL:100000 SSI:373, IT:47, CT:59, M:127',
        '行    124: [1][3613005646] I: [188719580] ddr:gold CPU:6, CF:1053, MF:3187, IPM:632, STL:100000 SSI:158, IT:67, CT:71, M:160',
        '行    129: [1][3613024949] I: [188720581] ddr:gold CPU:6, CF:1053, MF:2092, IPM:632, STL:100000 SSI:397, IT:45, CT:65, M:129',
        '行    133: [1][3613044476] I: [188721603] ddr:gold CPU:6, CF:1053, MF:3187, IPM:632, STL:100000 SSI:212, IT:61, CT:65, M:147',
        '行    137: [0][3613061300] I: [188722553] ddr:gold CPU:6, CF:1053, MF:3187, IPM:632, STL:100000 SSI:254, IT:56, CT:65, M:141',
        '行    146: [1][3613102656] I: [188724619] ddr:gold CPU:7, CF:968, MF:2092, IPM:433, STL:100000 SSI:809, IT:29, CT:46, M:102'
    ]
    
    data = []
    for line in log_lines:
        # Check if this is a ddr:gold event line
        if "ddr:gold" not in line:
            continue
            
        # Extract timestamp from the format [188704574]
        timestamp_match = re.search(r'\[(\d{9})\].*ddr:gold', line)
        if not timestamp_match:
            continue
            
        # Extract first 3 digits as timestamp
        timestamp_str = timestamp_match.group(1)
        timestamp = int(timestamp_str[:3])
        
        # Initialize an entry with timestamp
        entry = {'Timestamp': timestamp}
        
        # Extract all available metrics using individual regex patterns
        metrics = {
            'CPU': r'CPU:(\d+)',
            'CF': r'CF:(\d+)',
            'MF': r'MF:(\d+)',
            'IPM': r'IPM:(\d+)',
            'STL': r'STL:(\d+)',
            'SSI': r'SSI:(\d+)',
            'IT': r'IT:(\d+)',
            'CT': r'CT:(\d+)',
            'M': r'M:(\d+)'
        }
        
        # Extract each metric if available
        for metric, pattern in metrics.items():
            match = re.search(pattern, line)
            if match:
                entry[metric] = int(match.group(1))
            else:
                entry[metric] = np.nan  # Use NaN for missing metrics
        
        # Only add entry if at least one metric besides timestamp is present
        if len(entry) > 1:
            data.append(entry)
    
    print("Using sample data instead of log file")
    return pd.DataFrame(data)

def create_interactive_web_plot(df, output_html="ddr_gold_interactive.html"):
    """
    Create an interactive web-based plot with broken axis visualization
    """
    if df.empty:
        print("No data to plot")
        return
    
    # Sort by timestamp to ensure correct order
    df = df.sort_values('Timestamp')
    
    # Check which metrics are available in the data
    available_metrics = [col for col in df.columns if col != 'Timestamp' and not df[col].isna().all()]
    
    # Determine which metrics go in which subplot based on their value ranges
    high_range_metrics = []
    low_range_metrics = []
    
    # Check which high range metrics are available
    for metric in ['SSI', 'STL', 'MF']:
        if metric in available_metrics:
            high_range_metrics.append(metric)
    
    # Check which low range metrics are available
    for metric in ['CPU', 'CF', 'IPM', 'IT', 'CT', 'M']:
        if metric in available_metrics:
            low_range_metrics.append(metric)
    
    # Create subplot titles based on available metrics
    high_range_title = f"High Range Values ({', '.join(high_range_metrics)})" if high_range_metrics else "High Range Values"
    low_range_title = f"Low Range Values ({', '.join(low_range_metrics)})" if low_range_metrics else "Low Range Values"
    
    # Create figure with subplots
    fig = make_subplots(
        rows=2, cols=1,
        row_heights=[0.45, 0.45],
        subplot_titles=(
            high_range_title,
            low_range_title
        ),
        vertical_spacing=0.25
    )
    
    # Define colors for better visibility
    colors = {
        'CPU': '#000000',  # Black
        'CF': '#1f77b4',   # Blue
        'MF': '#2ca02c',   # Green
        'IPM': '#d62728',  # Red
        'STL': '#17becf',  # Cyan
        'SSI': '#9467bd',  # Purple
        'IT': '#ff7f0e',   # Orange
        'CT': '#8c564b',   # Brown
        'M': '#e377c2'     # Pink
    }
    
    # Plot high range metrics (SSI, STL, MF) if available
    for metric in ['SSI', 'STL', 'MF']:
        if metric in available_metrics:
            fig.add_trace(
                go.Scatter(
                    x=df['Timestamp'], 
                    y=df[metric], 
                    mode='lines+markers',
                    name=metric,
                    line=dict(color=colors[metric], width=2),
                    marker=dict(size=6),
                    connectgaps=False  # Don't connect points with missing values
                ),
                row=1, col=1
            )
    
    # Plot low range metrics (CPU, CF, IPM, IT, CT, M) if available
    for metric in ['CPU', 'CF', 'IPM', 'IT', 'CT', 'M']:
        if metric in available_metrics:
            line_shape = 'hv' if metric == 'CPU' else None  # Special line shape for CPU
            marker_size = 8 if metric == 'CPU' else 6      # Larger markers for CPU
            
            fig.add_trace(
                go.Scatter(
                    x=df['Timestamp'], 
                    y=df[metric], 
                    mode='lines+markers',
                    name=metric,
                    line=dict(color=colors[metric], width=2, shape=line_shape),
                    marker=dict(size=marker_size),
                    connectgaps=False  # Don't connect points with missing values
                ),
                row=2, col=1
            )
    
    # Update layout
    fig.update_layout(
        title_text="DDR_Gold Event Metrics Analysis with Broken Axis",
        title=dict(
            y=0.98,
            x=0.5,
            xanchor='center',
            yanchor='top'
        ),
        height=1200,
        width=1200,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.05,
            xanchor="center",
            x=0.5
        ),
        margin=dict(t=150, b=100, l=100, r=50),
        template="plotly_white"
    )
    
    # Update x-axis titles
    fig.update_xaxes(title_text="", row=1, col=1)
    fig.update_xaxes(title_text="Timestamp (first 3 digits)", row=2, col=1, title_standoff=20)
    
    # Update y-axis titles
    fig.update_yaxes(title_text="Value (high range)", row=1, col=1, title_standoff=15)
    fig.update_yaxes(title_text="Value (low range)", row=2, col=1, title_standoff=15)
    
    # Add broken axis indicators
    fig.add_shape(
        type="line",
        x0=-0.02, y0=0, x1=-0.02, y1=1,
        xref='paper', yref='paper',
        line=dict(
            color="Black",
            width=2,
            dash="dot",
        )
    )
    
    # Add annotations
    fig.add_annotation(
        text="",
        xref="paper", yref="paper",
        x=0.5, y=1.15,
        showarrow=False,
        font=dict(size=14)
    )
    
    # Update subplot titles position
    fig.update_annotations(font_size=12, y=0.99, selector=dict(text=high_range_title))
    fig.update_annotations(font_size=12, y=0.48, selector=dict(text=low_range_title))
    
    # Add hover information
    fig.update_traces(
        hovertemplate="<b>%{fullData.name}</b><br>Timestamp: %{x}<br>Value: %{y}<extra></extra>"
    )
    
    # Save to HTML file - use the most reliable method
    fig.write_html(
        output_html,
        include_plotlyjs=True,  # Include Plotly.js in the HTML file
        full_html=True,         # Create a standalone HTML file
        auto_open=False         # Don't automatically open the file
    )
    
    print(f"Interactive plot saved to {output_html}")
    return fig

def main():
    # Log file path
    log_file_path = 'ftrace/adcvs_only/cpucp_log.txt'
    
    # Extract data
    df = extract_ddr_gold_data(log_file_path)
    
    if not df.empty:
        print(f"Extracted {len(df)} data points")
        
        # Save data to CSV file
        df.to_csv('ddr_gold_data.csv', index=False)
        print("Data saved to ddr_gold_data.csv")
        
        # Create interactive web plot
        create_interactive_web_plot(df)
    else:
        print("No data extracted from the log file")

if __name__ == "__main__":
    main()