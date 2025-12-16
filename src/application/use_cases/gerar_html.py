"""Caso de uso: Gerar HTML."""

from ...domain.interfaces.html_generator import IHTMLGenerator
from ...domain.interfaces.file_repository import IFileRepository


class GerarHTMLUseCase:
    """Caso de uso para gerar HTML a partir de resultado de texto."""
    
    def __init__(
        self,
        html_generator: IHTMLGenerator,
        file_repository: IFileRepository
    ):
        """
        Inicializa o caso de uso.
        
        Args:
            html_generator: Gerador de HTML
            file_repository: Repositório de arquivos
        """
        self.html_generator = html_generator
        self.file_repository = file_repository
    
    def executar(self, arquivo_entrada: str, arquivo_saida: str) -> bool:
        """
        Executa a geração de HTML.
        
        Args:
            arquivo_entrada: Caminho do arquivo de entrada (resultado.txt)
            arquivo_saida: Caminho do arquivo de saída (HTML)
            
        Returns:
            True se gerado com sucesso, False caso contrário
        """
        if not self.file_repository.existe(arquivo_entrada):
            print(f"❌ Arquivo não encontrado: {arquivo_entrada}")
            return False
        
        # Parsear o arquivo
        dados = self.html_generator.parsear_resultado_txt(arquivo_entrada)
        
        # Gerar HTML
        html = self.html_generator.gerar_html(dados)
        
        # Salvar HTML
        sucesso = self.file_repository.salvar(html, arquivo_saida)
        
        if sucesso:
            print(f"✅ HTML gerado com sucesso!")
            print(f"   - {len(dados['authors'])} autores processados")
            print(f"   - {sum(a['count'] for a in dados['authors'].values())} PRs no total")
            print(f"   - Arquivo salvo: {arquivo_saida}")
        
        return sucesso

