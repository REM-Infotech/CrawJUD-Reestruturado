"""Módulo de gerenciamento dos tipos elements."""

from typing import Union

from crawjud_app.addons.elements.caixa import CaixaAm
from crawjud_app.addons.elements.calculadoras import TJDFT
from crawjud_app.addons.elements.elaw import ElawAme
from crawjud_app.addons.elements.esaj import EsajAm
from crawjud_app.addons.elements.pje import PJeAm
from crawjud_app.addons.elements.projudi import ProjudiAm

type_elements = Union[EsajAm, ProjudiAm, ElawAme, CaixaAm, PJeAm, TJDFT]
