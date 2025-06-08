import zipfile
import pandas as pd
import os

def _get_first_csv_from_zip(zip_ref):
    """
    Helper function to find and return the name of the first CSV file
    within a ZipFile object. Returns None if no CSV is found.
    """
    csv_files = [f for f in zip_ref.namelist() if f.endswith('.csv')]
    return csv_files[0] if csv_files else None

def extract_and_load_csv_from_zip(
    zip_path: str,
    encoding: str = 'latin1',
    on_bad_lines: str = 'skip'
) -> pd.DataFrame | None:
    """
    Extracts the first CSV file from a ZIP archive and loads it into a pandas DataFrame.

    Args:
        zip_path (str): The full path to the ZIP file.
        encoding (str): The encoding to use when reading the CSV file (default is 'latin1').
        on_bad_lines (str): Action to take when encountering a bad line in the CSV
                            (default is 'skip').

    Returns:
        pd.DataFrame | None: A pandas DataFrame if a CSV is successfully extracted and loaded,
                            otherwise None.
    """
    if not os.path.exists(zip_path):
        print(f"Erro: O arquivo ZIP '{zip_path}' não foi encontrado.")
        return None

    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            csv_file_name = _get_first_csv_from_zip(zip_ref)

            if not csv_file_name:
                print(f"Não foi encontrado arquivo CSV no ZIP: '{zip_path}'.")
                return None

            print(f"Extraindo e carregando '{csv_file_name}' de '{zip_path}'...")
            with zip_ref.open(csv_file_name) as csvfile:
                df = pd.read_csv(csvfile, encoding=encoding, on_bad_lines=on_bad_lines)
                print("CSV carregado com sucesso.")
                return df

    except zipfile.BadZipFile:
        print(f"Erro: O arquivo '{zip_path}' não é um arquivo ZIP válido ou está corrompido.")
        return None
    except pd.errors.ParserError as e:
        print(f"Erro ao analisar o CSV de '{zip_path}': {e}")
        return None
    except Exception as e:
        print(f"Ocorreu um erro inesperado ao processar '{zip_path}': {e}")
        return None
