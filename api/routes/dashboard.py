"""
Module for dashboard routes.

This module provides endpoints for rendering the dashboard and for serving
chart data for executions per month and most executed bots.
"""

from __future__ import annotations

from traceback import format_exception
from typing import TYPE_CHECKING

from quart import Blueprint, Response, abort, current_app, jsonify, make_response
from quart_jwt_extended import jwt_required

from api import db
from api.addons.colors import escurecer_cor, gerar_cor_base, rgb_to_hex
from api.models import Executions

if TYPE_CHECKING:
    from api.models.bots import BotsCrawJUD


dash = Blueprint("dash", __name__)


@dash.route("/linechart_system")
@jwt_required
async def linechart_system() -> Response:
    """
    Render the line chart page.

    Returns:
        Response: The response object containing the chart data.

    """
    try:
        executions = db.session.query(Executions).all()

        labels = {
            "1": "Janeiro",
            "2": "Fevereiro",
            "3": "Março",
            "4": "Abril",
            "5": "Maio",
            "6": "Junho",
            "7": "Julho",
            "8": "Agosto",
            "9": "Setembro",
            "10": "Outubro",
            "11": "Novembro",
            "12": "Dezembro",
        }

        contagem_execucoes = []

        system_colors = {
            "PROJUDI": {
                "background_color": "#67277e",
                "border_color": "#371442",
            },
            "PJE": {
                "background_color": "#ca1a9d",
                "border_color": "#ab1685",
            },
            "ESAJ": {
                "background_color": "#59236c",
                "border_color": "#4b1d5b",
            },
            "ELAW": {
                "background_color": "#b67909",
                "border_color": "#925607",
            },
        }

        for system in ["PROJUDI", "PJE", "ESAJ", "ELAW", "CAIXA", "TJDF", "CAIXA"]:
            executions_mes = {
                "Janeiro": 0,
                "Fevereiro": 0,
                "Março": 0,
                "Abril": 0,
                "Maio": 0,
                "Junho": 0,
                "Julho": 0,
                "Agosto": 0,
                "Setembro": 0,
                "Outubro": 0,
                "Novembro": 0,
                "Dezembro": 0,
            }
            for item in executions:
                exec_bot: BotsCrawJUD = item.bot

                if exec_bot.system.upper() == system:
                    mes = labels[str(item.data_execucao.month)]
                    executions_mes[mes] += 1

            contagem_execucoes.append({system: executions_mes})

        data: dict[str, dict[str, str] | list[dict[str, str]]] = {
            "labels": list(labels.values()),
            "datasets": [],
        }

        for contagem in contagem_execucoes:
            it = contagem.items()

            for key, value in it:
                numbers = list(value.values())

                background_color = system_colors.get(key.upper(), {}).get("background_color", "#000000")
                border_color = system_colors.get(key.upper(), {}).get("border_color", "#000000")
                # Se não houver cor definida, gerar nova cor
                if not system_colors.get(key.upper()):
                    # Gerar cor base
                    r, g, b = gerar_cor_base()
                    background_color = rgb_to_hex(r, g, b)

                    # Gerar cor da borda mais escura
                    r_borda, g_borda, b_borda = escurecer_cor(r, g, b)
                    border_color = rgb_to_hex(r_borda, g_borda, b_borda)

                setup_dataset = {
                    "label": key,
                    "data": numbers,
                    "borderColor": border_color,
                    "backgroundColor": background_color,
                    "yAxisID": "y",
                }

                data["datasets"].append(setup_dataset)

        return await make_response(jsonify(dataset=data))
    except (KeyError, AttributeError, ValueError) as e:
        current_app.logger.error("\n".join(format_exception(e)))
        abort(500, "Erro ao gerar o gráfico de linha.")


@dash.route("/linechart_bot")
@jwt_required
async def linechart_bot() -> Response:
    """
    Render the line chart page.

    Returns:
        Response: The response object containing the chart data.

    """
    try:
        executions = db.session.query(Executions).all()

        labels = {
            "1": "Janeiro",
            "2": "Fevereiro",
            "3": "Março",
            "4": "Abril",
            "5": "Maio",
            "6": "Junho",
            "7": "Julho",
            "8": "Agosto",
            "9": "Setembro",
            "10": "Outubro",
            "11": "Novembro",
            "12": "Dezembro",
        }

        contagem_execucoes = []

        system_colors = {
            "PROJUDI": {
                "background_color": "#67277e",
                "border_color": "#371442",
            },
            "PJE": {
                "background_color": "#ca1a9d",
                "border_color": "#ab1685",
            },
            "ESAJ": {
                "background_color": "#59236c",
                "border_color": "#4b1d5b",
            },
            "ELAW": {
                "background_color": "#b67909",
                "border_color": "#925607",
            },
        }

        list_system: list[str] = []

        for item in executions:
            bot_exec: BotsCrawJUD = item.bot
            if bot_exec.display_name.upper() not in list_system:
                list_system.append(item.bot.display_name.upper())

        for bot in list_system:
            executions_mes = {
                "Janeiro": 0,
                "Fevereiro": 0,
                "Março": 0,
                "Abril": 0,
                "Maio": 0,
                "Junho": 0,
                "Julho": 0,
                "Agosto": 0,
                "Setembro": 0,
                "Outubro": 0,
                "Novembro": 0,
                "Dezembro": 0,
            }
            for item in executions:
                exec_bot: BotsCrawJUD = item.bot

                if exec_bot.display_name.upper() == bot:
                    mes = labels[str(item.data_execucao.month)]
                    executions_mes[mes] += 1

            contagem_execucoes.append({bot: executions_mes})

        data: dict[str, dict[str, str] | list[dict[str, str]]] = {
            "labels": list(labels.values()),
            "datasets": [],
        }

        for contagem in contagem_execucoes:
            it = contagem.items()

            for key, value in it:
                numbers = list(value.values())

                background_color = system_colors.get(key.upper(), {}).get("background_color", "#000000")
                border_color = system_colors.get(key.upper(), {}).get("border_color", "#000000")
                # Se não houver cor definida, gerar nova cor
                if not system_colors.get(key):
                    # Gerar cor base
                    r, g, b = gerar_cor_base()
                    background_color = rgb_to_hex(r, g, b)

                    # Gerar cor da borda mais escura
                    r_borda, g_borda, b_borda = escurecer_cor(r, g, b)
                    border_color = rgb_to_hex(r_borda, g_borda, b_borda)

                setup_dataset = {
                    "label": key,
                    "data": numbers,
                    "borderColor": border_color,
                    "backgroundColor": background_color,
                    "yAxisID": "y",
                }

                data["datasets"].append(setup_dataset)

        return await make_response(jsonify(dataset=data))
    except (KeyError, AttributeError, ValueError) as e:
        current_app.logger.error("\n".join(format_exception(e)))
        abort(500, "Erro ao gerar o gráfico de linha.")
