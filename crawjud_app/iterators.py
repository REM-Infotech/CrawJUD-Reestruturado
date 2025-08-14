"""Módulo de agrupamento de Iterators para o CrawJUD."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from controllers.bots.master.bot_head import ClassBot
    from interface.types.pje import DictSeparaRegiao


class RegioesIterator:
    """Retorne regiões e dados associados iterando sobre processos separados.

    Args:
        bot (PjeBot): Instância do bot para acessar métodos e dados.

    Returns:
        RegioesIterator: Iterador sobre tuplas (região, dados da região).

    Raises:
        StopIteration: Quando todas as regiões forem iteradas.

    """

    def __init__(self, bot: ClassBot) -> None:
        """Inicialize o iterador de regiões com dados do bot e processos separados.

        Args:
            bot (PjeBot): Instância do bot para acessar métodos e dados.


        """
        # Carrega arquivos e separa regiões
        bot.carregar_arquivos()
        dict_processo_separado: DictSeparaRegiao = bot.separar_regiao()
        self._bot = bot
        self._regioes = list(dict_processo_separado["regioes"].items())
        self._posicoes_processos_planilha = dict_processo_separado["position_process"]
        self._index = 0

        # Atualiza atributos do bot
        bot.posicoes_processos = self._posicoes_processos_planilha
        bot.total_rows = len(self._posicoes_processos_planilha.values())

    def __iter__(self) -> RegioesIterator:
        """Retorne o próprio iterador para permitir iteração sobre regiões.

        Returns:
            RegioesIterator: O próprio iterador de regiões.

        """
        return self

    def __next__(self) -> tuple[str, str]:
        """Implementa a iteração retornando próxima região e dados associados.

        Returns:
            tuple[str, str]: Tupla contendo a região e os dados da região.

        Raises:
            StopIteration: Quando todas as regiões forem iteradas.

        """
        if self._index >= len(self._regioes):
            raise StopIteration

        regiao, data_regiao = self._regioes[self._index]
        self._bot.regiao = regiao
        self._bot.data_regiao = data_regiao
        self._index += 1
        return regiao, data_regiao
