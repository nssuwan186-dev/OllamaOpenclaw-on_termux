import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sys
import os

def generate_report_visual(csv_path, output_image):
    try:
        df = pd.read_csv(csv_path)
        plt.figure(figsize=(10, 6))
        sns.set_style("whitegrid")
        
        # Example: Bar chart of revenue by room
        if 'room_no' in df.columns and 'amount' in df.columns:
            # Aggregate by room
            summary = df.groupby('room_no')['amount'].sum().sort_values(ascending=False).head(10)
            summary.plot(kind='bar', color='skyblue')
            plt.title('Top 10 Revenue by Room')
            plt.ylabel('Amount (Baht)')
            plt.xlabel('Room Number')
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.savefig(output_image)
            return {"status": "success", "image_path": output_image}
        else:
            return {"status": "error", "message": "Columns 'room_no' and 'amount' not found"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python visual_tool.py <csv_path> <output_image>")
    else:
        result = generate_report_visual(sys.argv[1], sys.argv[2])
        print(result)
