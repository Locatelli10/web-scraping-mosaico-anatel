import unittest
import pandas as pd

from processador_dados_anatel import ProcessadorDadosAnatel


class TestProcessadorDadosAnatelFuncoesEssenciais(unittest.TestCase):
    def setUp(self):
        """
        Método executado antes de cada teste.
        Inicializa uma nova instância do processador e um DataFrame de teste.
        """
        self.processador = ProcessadorDadosAnatel()
        # Criando um DataFrame de exemplo com algumas das colunas importantes para simular os dados de entrada.
        self.dados_iniciais = {
            'NomeEntidade': [' CLARO S.A. ', 'TELEFONICA BRASIL S.A.', 'TIM S A', 'Outra Operadora'],
            'NumFistel': [50409307637, 50409314250, 50409428698, 50409889580],
            'NumServico': [10, 20, 10, 10],
            'SiglaUf': ['SP', 'RJ ', 'MG', 'BA'],
            'CodMunicipio': [12345, 67890, 11223, 44556],
            'Tecnologia': [' GSM ', 'WCDMA', 'LTE', 'Inexistente'],
            'FreqTxMHz': ['900,5', '1800.0', '2100;0', 'abc'],
            'ClassInfraFisica': [' Greenfield ', None, 'Rooftop', 'Indoor'],
            'AlturaAntena': ['50.0', '30,0', '20', 'xyz'],
            'Latitude': [-23.0, -22.0, -21.0, -20.0],
            'Longitude': [-46.0, -43.0, -47.0, -48.0],
            'DataLicenciamento': ['2023-01-15', '2022-11-20', '2024-03-10', 'Data Invalida'],
            'DataPrimeiroLicenciamento': ['2020-05-01', '2019-02-28', '2021-09-15', '2018-01-01'],
            'DataValidade': ['2025-01-15', '2024-11-20', '2026-03-10', '2023-12-31'],
            'Municipio.NomeMunicipio': ['São Paulo', 'Rio de Janeiro ', 'Belo Horizonte', 'Salvador']
        }
        self.df_base = pd.DataFrame(self.dados_iniciais)

    def test_selecionar_e_renomear_colunas(self):
        """
        Testa se as colunas são selecionadas e renomeadas corretamente.
        """
        df_processado = self.processador._selecionar_e_renomear_colunas(self.df_base.copy())
        
        expected_columns = list(self.processador._MAPEAMENTO_RENOMEACAO_COLUNAS.values())
        for col in self.processador._COLUNAS_PARA_SELECIONAR:
            if col not in self.processador._MAPEAMENTO_RENOMEACAO_COLUNAS and col in self.df_base.columns:
                expected_columns.append(col)
        
        # Remove duplicatas e garante ordem para comparacao
        expected_columns = sorted(list(set(expected_columns)))
        actual_columns = sorted(list(df_processado.columns))
        
        self.assertListEqual(actual_columns, expected_columns, "As colunas renomeadas não correspondem às esperadas.")
        self.assertIn('Operadora', df_processado.columns, "A coluna 'Operadora' não foi encontrada.")
        self.assertIn('UF', df_processado.columns, "A coluna 'UF' não foi encontrada.")
        self.assertIn('Frequencia', df_processado.columns, "A coluna 'Frequencia' não foi encontrada.")
        self.assertNotIn('NomeEntidade', df_processado.columns, "A coluna original 'NomeEntidade' ainda existe.")

    def test_converter_tipos_e_tratar_ausentes(self):
        """
        Testa a conversão de tipos de dados e o tratamento de valores ausentes/inválidos,
        focando na precisão numérica e na remoção de linhas.
        """
        
        df_teste_conv = self.df_base.copy()
        df_teste_conv = self.processador._limpar_espacos_em_branco(df_teste_conv)
        df_teste_conv = self.processador._selecionar_e_renomear_colunas(df_teste_conv)

        df_processado = self.processador._converter_tipos_e_tratar_ausentes(df_teste_conv)

        # Verifica se as colunas de data sao datetime
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(df_processado['DataPrimeiroLicenciamento']), 
                        "A coluna 'DataPrimeiroLicenciamento' não é do tipo datetime.")
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(df_processado['DataUltimoLicenciamento']),
                        "A coluna 'DataUltimoLicenciamento' não é do tipo datetime.")

        # Verificacao de tipos numericos (float/int)
        self.assertIsInstance(df_processado['Frequencia'].iloc[0], (float, int),
                              "O valor da Frequencia não é numérico (float ou int).")
        self.assertIsInstance(df_processado['AlturaAntena'].iloc[0], (float, int),
                              "O valor da AlturaAntena não é numérico (float ou int).")

        # Verifica se linhas com valores invalidos criticos foram removidas
        self.assertEqual(len(df_processado), 3, "Número incorreto de linhas após remoção de inválidos.")

        # Verifica a conversao de virgula/ponto e virgula para ponto e depois o valor
        self.assertAlmostEqual(df_processado.loc[0, 'Frequencia'], 900.5, 
                               msg="Frequencia do item 0 incorreta após conversão.")
        self.assertAlmostEqual(df_processado.loc[1, 'Frequencia'], 1800.0,
                               msg="Frequencia do item 1 incorreta após conversão.")
        self.assertAlmostEqual(df_processado.loc[2, 'Frequencia'], 2100.0,
                               msg="Frequencia do item 2 incorreta após conversão (de '2100;0').")

        self.assertAlmostEqual(df_processado.loc[0, 'AlturaAntena'], 50.0,
                               msg="AlturaAntena do item 0 incorreta após conversão.")
        self.assertAlmostEqual(df_processado.loc[1, 'AlturaAntena'], 30.0,
                               msg="AlturaAntena do item 1 incorreta após conversão.")
        self.assertAlmostEqual(df_processado.loc[2, 'AlturaAntena'], 20.0,
                               msg="AlturaAntena do item 2 incorreta após conversão.")

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)