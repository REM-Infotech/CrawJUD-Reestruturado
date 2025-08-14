from abc import abstractmethod

from controllers.bots.master.bot_head import ClassBot


class CNJBots[T](ClassBot):
    """Classe de controle de bots de busca processual."""

    @abstractmethod
    def autenticar(self, *args: T, **kwargs: T) -> bool:
        """Autenticação do sistema do Robô.

        Returns:
            bool: Booleano para identificar se autenicação foi realizada.

        """

    @abstractmethod
    def buscar_processo(self, *args: T, **kwargs: T) -> bool:
        """Busca o processo no sistema do robô.

        Returns:
            DictResults: dicionário com os resultados da busca.

        """
