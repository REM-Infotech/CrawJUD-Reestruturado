"""Módulo de gerenciamento dos tipos elements."""

from typing import Union

from crawjud_app.addons.elements.caixa import CAIXA_AM
from crawjud_app.addons.elements.calculadoras import TJDFT
from crawjud_app.addons.elements.elaw import ELAW_AME
from crawjud_app.addons.elements.esaj import ESAJ_AM
from crawjud_app.addons.elements.pje import PJE_AM
from crawjud_app.addons.elements.projudi import PROJUDI_AM

type_elements = Union[ESAJ_AM, PROJUDI_AM, ELAW_AME, CAIXA_AM, PJE_AM, TJDFT]
