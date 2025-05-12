"""Módulo de gerenciamento dos tipos elements."""

from typing import Union

from crawjud.addons.elements.caixa import CAIXA_AM
from crawjud.addons.elements.calculadoras import TJDFT
from crawjud.addons.elements.elaw import ELAW_AME
from crawjud.addons.elements.esaj import ESAJ_AM
from crawjud.addons.elements.pje import PJE_AM
from crawjud.addons.elements.projudi import PROJUDI_AM

type_elements = Union[ESAJ_AM, PROJUDI_AM, ELAW_AME, CAIXA_AM, PJE_AM, TJDFT]
