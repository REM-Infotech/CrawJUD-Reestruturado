"""Módulo de gerenciamento dos tipos elements."""

from typing import Union

from celery_app.addons.elements.caixa import CAIXA_AM
from celery_app.addons.elements.calculadoras import TJDFT
from celery_app.addons.elements.elaw import ELAW_AME
from celery_app.addons.elements.esaj import ESAJ_AM
from celery_app.addons.elements.pje import PJE_AM
from celery_app.addons.elements.projudi import PROJUDI_AM

type_elements = Union[ESAJ_AM, PROJUDI_AM, ELAW_AME, CAIXA_AM, PJE_AM, TJDFT]
