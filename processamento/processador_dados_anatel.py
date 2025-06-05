import pandas as pd
from datetime import datetime

class ProcessadorDadosAnatel:
    """
    Processa um DataFrame de dados da Anatel, aplicando transformações de limpeza,
    seleção, renomeação e padronização.
    """

    # Mapeamentos e constantes de configuração
    _COLUNAS_PARA_SELECIONAR = [
        'NomeEntidade', 'NumFistel', 'NumServico', 'NumEstacao', 'SiglaUf', 'CodMunicipio',
        'Tecnologia', 'FreqTxMHz', 'ClassInfraFisica', 'AlturaAntena', 'Latitude', 'Longitude',
        'DataLicenciamento', 'DataPrimeiroLicenciamento', 'DataValidade', 'Municipio.NomeMunicipio'
    ]

    _MAPEAMENTO_RENOMEACAO_COLUNAS = {
        'NomeEntidade': "Operadora",
        'SiglaUf': "UF",
        'FreqTxMHz': "Frequencia",
        'ClassInfraFisica': "TipoInfra",
        'DataLicenciamento': "DataUltimoLicenciamento",
        'Municipio.NomeMunicipio': "NomeMunicipio"
    }

    _MAPEAMENTO_OPERADORAS = {
        'CLARO S.A.': "CLARO",
        'TELEFONICA BRASIL S.A.': "VIVO",
        'Telefonica Brasil S.a.': "VIVO",
        'TIM S A': "TIM",
        'TIM S/A': "TIM",
        'Brisanet Servicos de Telecomunicacoes S.A.': "BRISANET"
    }

    _MAPEAMENTO_TECNOLOGIAS = {
        'GSM': "2G",
        'WCDMA': "3G",
        'WDCMA': "3G",
        'LTE': "4G",
        'NR': "5G",
        '': "Nao Informado"
    }

    _TIPAGEM_COLUNAS = {
        'Operadora': 'string',
        'NumFistel': 'Int64',
        'NumServico': 'Int64',
        'UF': 'string',
        'CodMunicipio': 'Int64',
        'Tecnologia': 'string',
        'TipoInfra': 'string',
        'Latitude': 'float',
        'Longitude': 'float',
        'DataUltimoLicenciamento': 'datetime64[ns]',
        'DataPrimeiroLicenciamento': 'datetime64[ns]',
        'DataValidade': 'datetime64[ns]',
        'NomeMunicipio': 'string'
    }

    def processar(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Orquestra o processo de transformação do DataFrame de dados da Anatel.

        Args:
            df (pd.DataFrame): O DataFrame bruto a ser processado.

        Returns:
            pd.DataFrame: O DataFrame processado.
        """
        df_processado = df.copy()

        df_processado = self._remover_espacos(df_processado)
        df_processado = self._selecionar_e_renomear_colunas(df_processado)
        df_processado = self._converter_tipos_e_tratar_ausentes(df_processado)
        df_processado = self._filtrar_dados(df_processado)
        df_processado = self._padronizar_valores(df_processado)
        df_processado = self._adicionar_coluna_data_download(df_processado)

        return df_processado

    def _remover_espacos(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove espaços em branco de todas as células e nomes de colunas."""
        df = df.astype(str).map(str.strip)
        df.columns = df.columns.str.strip()
        return df

    def _selecionar_e_renomear_colunas(self, df: pd.DataFrame) -> pd.DataFrame:
        """Seleciona as colunas desejadas e as renomeia."""
        colunas_existentes = [col for col in self._COLUNAS_PARA_SELECIONAR if col in df.columns]
        df = df[colunas_existentes]
        df = df.rename(columns=self._MAPEAMENTO_RENOMEACAO_COLUNAS)
        return df

    def _converter_tipos_e_tratar_ausentes(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Converte tipos de dados e trata valores ausentes/inválidos,
        removendo linhas problemáticas ou convertendo conforme o tipo.
        """
        # Substituindo vírgula/ponto e vírgula por ponto para colunas numéricas antes da conversão
        if 'AlturaAntena' in df.columns:
            df['AlturaAntena'] = df['AlturaAntena'].astype(str).str.replace('[,;]', '.', regex=True)
        if 'Frequencia' in df.columns:
            df['Frequencia'] = df['Frequencia'].astype(str).str.replace('[,;]', '.', regex=True)

        for col, dtype in self._TIPAGEM_COLUNAS.items():
            if col not in df.columns:
                continue

            if 'datetime' in str(dtype):
                df[col] = pd.to_datetime(df[col], errors='coerce')
            elif 'float' in str(dtype):
                df[col] = pd.to_numeric(df[col], errors='coerce')
            elif 'Int64' in str(dtype):
                 df[col] = pd.to_numeric(df[col], errors='coerce').astype(dtype)
            else:
                df[col] = df[col].astype(dtype)

        # Descartando linhas com valores inválidos críticos (datas e numéricos essenciais)
        df.dropna(subset=[
            'DataPrimeiroLicenciamento',
            'DataUltimoLicenciamento',
            'Frequencia',
            'AlturaAntena'
        ], inplace=True)

        return df

    def _filtrar_dados(self, df: pd.DataFrame) -> pd.DataFrame:
        """Filtra os dados para incluir apenas licenciamentos móveis (NumServico == 10)."""
        if 'NumServico' in df.columns:
            df['NumServico'] = pd.to_numeric(df['NumServico'], errors='coerce')
            df = df[df['NumServico'] == 10]
        return df

    def _padronizar_valores(self, df: pd.DataFrame) -> pd.DataFrame:
        """Padroniza valores em colunas específicas (TipoInfra, Operadora, Tecnologia)."""
        if 'TipoInfra' in df.columns:
            df['TipoInfra'] = df['TipoInfra'].replace('nan', 'Nao Especificado')
        if 'Operadora' in df.columns:
            df['Operadora'] = df['Operadora'].replace(self._MAPEAMENTO_OPERADORAS)
        if 'Tecnologia' in df.columns:
            df['Tecnologia'] = df['Tecnologia'].replace(self._MAPEAMENTO_TECNOLOGIAS)
        return df

    def _adicionar_coluna_data_download(self, df: pd.DataFrame) -> pd.DataFrame:
        """Adiciona uma coluna com a data do download dos registros."""
        df['DataDownload'] = datetime.now().strftime("%d/%m/%Y")
        return df