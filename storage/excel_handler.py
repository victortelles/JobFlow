import os
import datetime
import pandas as pd

# Define storage path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
FILE_PATH = os.path.join(DATA_DIR, 'jobflow.xlsx')
SHEET_NAME = 'postulaciones'

# Columns definition as per schema
COLUMNS = [
    'id', 'titulo', 'empresa', 'ubicacion', 'modalidad', 'turno',
    'nivel_experiencia', 'salario', 'tecnologias', 'descripcion_corta',
    'url_vacante', 'plataforma', 'fecha_publicacion', 'fecha_postulacion',
    'respondio', 'notas'
]

def initialize_excel() -> None:
    """
    Initializes the Excel storage file if it does not exist.
    Creates the 'data' directory and 'jobflow.xlsx' with correct schema headers.
    """
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR, exist_ok=True)
    
    if not os.path.exists(FILE_PATH):
        # Create an empty DataFrame with the defined columns
        df = pd.DataFrame(columns=COLUMNS)
        # Save to Excel
        with pd.ExcelWriter(FILE_PATH, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name=SHEET_NAME, index=False)

def load_data() -> pd.DataFrame:
    """
    Loads all applications from the Excel file.
    Returns a pandas DataFrame.
    """
    initialize_excel()
    try:
        df = pd.read_excel(FILE_PATH, sheet_name=SHEET_NAME)
        
        # Ensure all columns are present (in case columns were manually altered)
        for col in COLUMNS:
            if col not in df.columns:
                df[col] = None
        
        # Select and order columns as per definition
        df = df[COLUMNS]
        
        # Cast data types for consistency
        df['id'] = pd.to_numeric(df['id'], errors='coerce').astype('Int64')
        df['respondio'] = df['respondio'].fillna(False).astype(bool)
        df['titulo'] = df['titulo'].fillna("").astype(str)
        df['empresa'] = df['empresa'].fillna("").astype(str)
        df['ubicacion'] = df['ubicacion'].fillna("").astype(str)
        df['modalidad'] = df['modalidad'].fillna("").astype(str)
        df['turno'] = df['turno'].fillna("").astype(str)
        df['nivel_experiencia'] = df['nivel_experiencia'].fillna("").astype(str)
        df['salario'] = df['salario'].fillna("").astype(str)
        df['tecnologias'] = df['tecnologias'].fillna("").astype(str)
        df['descripcion_corta'] = df['descripcion_corta'].fillna("").astype(str)
        df['url_vacante'] = df['url_vacante'].fillna("").astype(str)
        df['plataforma'] = df['plataforma'].fillna("").astype(str)
        df['notas'] = df['notas'].fillna("").astype(str)
        
        # Convert date columns to date object or string for display
        df['fecha_publicacion'] = pd.to_datetime(df['fecha_publicacion'], errors='coerce').dt.date
        df['fecha_postulacion'] = pd.to_datetime(df['fecha_postulacion'], errors='coerce').dt.date
        
        return df
    except Exception as e:
        print(f"Error loading Excel data: {e}")
        # Return an empty DataFrame matching the schema in case of error
        return pd.DataFrame(columns=COLUMNS)

def save_data(df: pd.DataFrame) -> None:
    """
    Saves the pandas DataFrame back to the Excel file.
    """
    initialize_excel()
    try:
        # Reorder and filter to match schema columns
        df_to_save = df[COLUMNS].copy()
        
        # Format dates back to string or timestamp representation for Excel compatibility
        if 'fecha_publicacion' in df_to_save.columns:
            df_to_save['fecha_publicacion'] = pd.to_datetime(df_to_save['fecha_publicacion']).dt.strftime('%Y-%m-%d')
            # Handle NaN dates
            df_to_save['fecha_publicacion'] = df_to_save['fecha_publicacion'].replace('NaT', None)
            
        if 'fecha_postulacion' in df_to_save.columns:
            df_to_save['fecha_postulacion'] = pd.to_datetime(df_to_save['fecha_postulacion']).dt.strftime('%Y-%m-%d')
            df_to_save['fecha_postulacion'] = df_to_save['fecha_postulacion'].replace('NaT', None)
            
        # Ensure clean cast of numeric columns
        df_to_save['id'] = pd.to_numeric(df_to_save['id'], errors='coerce').astype('Int64')
        df_to_save['respondio'] = df_to_save['respondio'].fillna(False).astype(bool)

        with pd.ExcelWriter(FILE_PATH, engine='openpyxl') as writer:
            df_to_save.to_excel(writer, sheet_name=SHEET_NAME, index=False)
    except Exception as e:
        print(f"Error saving Excel data: {e}")
        raise e

def add_postulacion(postulacion_dict: dict) -> int:
    """
    Appends a new job application record to the Excel file.
    Automatically assigns an autoincrement ID and the current date as fecha_postulacion.
    
    Args:
        postulacion_dict (dict): A dictionary containing fields from the form.
        
    Returns:
        int: The newly created ID for the application.
    """
    df = load_data()
    
    # Calculate next autoincrement ID
    if len(df) > 0 and not df['id'].isna().all():
        next_id = int(df['id'].max() + 1)
    else:
        next_id = 1
        
    # Standardize dictionary keys and fill missing ones
    record = {}
    for col in COLUMNS:
        record[col] = postulacion_dict.get(col, None)
        
    # Overwrite auto-calculated fields
    record['id'] = next_id
    record['fecha_postulacion'] = datetime.date.today()
    record['respondio'] = False if record['respondio'] is None else bool(record['respondio'])
    
    # Standardize empty values
    for k, v in record.items():
        if v is None:
            record[k] = ""
            
    # Append the new record to the dataframe
    new_row = pd.DataFrame([record])
    
    # Concatenate safely
    if df.empty:
        df = new_row
    else:
        df = pd.concat([df, new_row], ignore_index=True)
        
    save_data(df)
    return next_id
