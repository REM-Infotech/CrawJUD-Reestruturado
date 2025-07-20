"""
Realiza operações de pré-processamento de imagem e OCR para resolver captchas.

Este módulo contém funções para processar imagens de captchas utilizando OpenCV e extrair texto via Tesseract OCR.

Args:
    Nenhum argumento de módulo.

Returns:
    Nenhum valor de retorno.

Raises:
    Nenhuma exceção específica.

"""

from os import environ
from pathlib import Path

import cv2
import pytesseract

# Configura o caminho do executável do Tesseract a partir das variáveis de ambiente
pytesseract.pytesseract.tesseract_cmd = environ["PATH_TESSERACT"]
custom_config = environ["CONFIG_TESSERACT"]


def image_to_text(img: Path) -> str:
    """
    Processa uma imagem de captcha e extrai o texto utilizando OCR.

    Args:
        img (Path): Caminho para a imagem a ser processada.

    Returns:
        str: Texto extraído da imagem após o processamento.

    Raises:
        KeyError: Se as variáveis de ambiente necessárias não estiverem definidas.
        cv2.error: Se ocorrer erro ao processar a imagem.

    """
    # Converte para escala de cinza
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Aplica binarização com Otsu
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Inverte a imagem se necessário (letras brancas em fundo preto)
    # thresh = cv2.bitwise_not(thresh)

    # Suaviza ruído com mediana (sem borrar letras)
    thresh = cv2.medianBlur(thresh, 3)

    # (Opcional) Dilatar para reforçar letras quebradas
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    thresh = cv2.dilate(thresh, kernel, iterations=1)

    # Salva imagem processada (debug visual opcional)
    cv2.imwrite("processed1.png", thresh)

    # Aplica OCR
    text = str(pytesseract.image_to_string(thresh, config=custom_config))
    return text.replace("\n")


# def test2():
#     """
#     (Exemplo comentado) Processa uma imagem de captcha e extrai texto usando configuração alternativa.
#
#     Args:
#         img (Path): Caminho para a imagem a ser processada.
#
#     Returns:
#         str: Texto extraído da imagem.
#     """
#     # Converter para escala de cinza
#     gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#
#     # Aplicar binarização
#     _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
#
#     # Remover ruídos (opcional)
#     thresh = cv2.medianBlur(thresh, 3)
#
#     # Salvar temporariamente a imagem processada
#     cv2.imwrite("processed2.png", thresh)
#
#     # Configurações do Tesseract
#     custom_config = r'--oem 3 --psm 7 -c tessedit_char_whitelist=0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
#
#     # Extrair texto
#     text = pytesseract.image_to_string(thresh, config=custom_config)
#     print(text)


# test1()
# test2()
