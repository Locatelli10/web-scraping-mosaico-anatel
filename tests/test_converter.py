# tests/test_converter.py

import os
import sys
# Adiciona a raiz do projeto ao path para localizar o pacote src
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

import pandas as pd
import numpy as np
import pytest
from pandas.api.types import is_object_dtype
from processador_dados_anatel import ProcessadorDadosAnatel

@pytest.fixture
def exemplo_df():
    # DataFrame de exemplo com diversos formatos antes da conversão
    return pd.DataFrame({
        'AlturaAntena': ['10,5', '20;75', None, 'invalid'],
        'Frequencia': ['700,0', '800;5', '900', ''],
        'DataPrimeiroLicenciamento': ['2020-01-01', 'notadate', None, '2021-03-15'],
        'DataUltimoLicenciamento': ['2019-06-30', '2020-07-01', '2021-08-02', None],
        'Outro': [1, 2, 3, 4]
    })


def test_conversao_de_tipos(exemplo_df):
    proc = ProcessadorDadosAnatel()
    df2 = proc._converter_tipos_e_tratar_ausentes(exemplo_df)

    # Após a conversão e remoção, apenas a primeira linha permanece
    assert len(df2) == 1

    # Verifica presença das colunas críticas
    assert 'AlturaAntena' in df2
    assert 'Frequencia' in df2
    assert 'DataPrimeiroLicenciamento' in df2
    assert 'DataUltimoLicenciamento' in df2

    # Verifica que os valores ainda são strings (object dtype)
    assert is_object_dtype(df2['AlturaAntena'])
    assert is_object_dtype(df2['Frequencia'])

    # Verifica valores convertidos corretamente na primeira linha
    assert df2['AlturaAntena'].iloc[0] == '10.5'
    assert df2['Frequencia'].iloc[0] == '700.0'


def test_remocao_linhas_criticas(exemplo_df):
    proc = ProcessadorDadosAnatel()
    df2 = proc._converter_tipos_e_tratar_ausentes(exemplo_df)

    # Apenas a primeira linha permanece
    assert len(df2) == 1
    assert df2['AlturaAntena'].iloc[0] == '10.5'
