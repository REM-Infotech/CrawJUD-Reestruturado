"""Modulo de controle da Classe de controle para robôs CNJ.

Esse modulo tem como objetivo criar uma classe de controle para
bots cujo a finalidade é automatizar tarefas de processos de
sistemas que o CNJ opera (Projudi, ESAJ, PJe, etc.).

"""

from abc import abstractmethod

from crawjud.controllers.bots.master.cnj_bots import CNJBots as ClassBot


class AnyBots[T](ClassBot):
    """Classe de controle para bots no geral."""

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
