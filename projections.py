import pandas as pd

def load_golf_data(filepath):
    """
    Loads golf player data from a CSV or Excel file.
    """
    try:
        df = pd.read_csv(filepath)
    except Exception:
        df = pd.read_excel(filepath)
    return df


def project_golf_points(row):
    """
    Projection formula combining FPPG, SG Putting, and SG Approach (SG:APP).
    Adjust weights below to tune projection logic.
    """
    fppg = row.get('FPPG', 0)
    sg_putting = row.get('SG_Putting', 0)
    sg_app = row.get('SG_APP', 0)

    # Example weights: 60% FPPG, 20% SG Putting, 20% SG Approach
    projection = fppg * 0.6 + sg_putting * 0.2 + sg_app * 0.2
    return projection


def add_projections(df):
    """
    Adds a 'Projected_Points' column to the DataFrame.
    """
    df['Projected_Points'] = df.apply(project_golf_points, axis=1)
    return df


if __name__ == "__main__":
    # Example usage
    path = 'your_golf_data.csv'  # Replace with your file path
    data = load_golf_data(path)
    data = add_projections(data)
    print(data[['Name', 'FPPG', 'SG_Putting', 'SG_APP', 'Projected_Points']].head())
