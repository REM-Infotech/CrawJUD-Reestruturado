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

import re
from typing import Any

import cv2
import numpy as np
import pytesseract
from dotenv import dotenv_values

environ = dotenv_values()

# Configura o caminho do executável do Tesseract a partir das variáveis de ambiente
pytesseract.pytesseract.tesseract_cmd = environ["PATH_TESSERACT"]
custom_config = environ["CONFIG_TESSERACT"]


def load_img_blur_apply(im_b: bytes) -> np.ndarray:
    """
    Realiza o pré-processamento de uma imagem de captcha aplicando conversão para escala de cinza, binarização e suavização.

    Args:
        im_b (bytes): Imagem em bytes a ser processada.

    Returns:
        np.ndarray: Imagem processada em escala de cinza e binarizada.

    Raises:
        Nenhuma exceção específica.

    """
    # Converte os bytes em um array numpy
    image_np = np.frombuffer(im_b, np.uint8)
    img_np = cv2.imdecode(image_np, cv2.IMREAD_COLOR)

    # Converter para escala de cinza
    color = cv2.COLOR_RGB2GRAY
    gray = cv2.cvtColor(img_np, color)

    # Aplicar binarização com Otsu
    _, thresh = cv2.threshold(gray, 5, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Suavizar ruído com mediana (sem borrar letras)
    return thresh


def reabre_imagem(f: Any) -> np.ndarray:
    """
    Reabra e processe uma imagem a partir de um arquivo, aplicando conversão para escala de cinza e binarização.

    Args:
        f (Any): Arquivo de imagem aberto em modo binário.

    Returns:
        np.ndarray: Imagem processada em escala de cinza e binarizada.

    Raises:
        Nenhuma exceção específica.

    """
    # Lê o conteúdo do arquivo e converte em array numpy
    image_np2 = np.frombuffer(f.read(), np.uint8)
    img_np2 = cv2.imdecode(image_np2, cv2.IMREAD_COLOR)
    color2 = cv2.COLOR_RGB2GRAY
    gray2 = cv2.cvtColor(img_np2, color2)
    _, threshold = cv2.threshold(gray2, 2, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return threshold


def captcha_to_image(im_b: bytes) -> str:
    """
    Processa uma imagem de captcha e extraia o texto utilizando OCR.

    Args:
        im_b (bytes): Imagem em bytes a ser processada.

    Returns:
        str: Texto extraído da imagem após o processamento.

    Raises:
        KeyError: Se as variáveis de ambiente necessárias não estiverem definidas.
        cv2.error: Se ocorrer erro ao processar a imagem.

    """
    # Define nome do arquivo para debug do processamento
    process_dbg = "process_dbg.png"

    # Pré-processa a imagem
    thresh = load_img_blur_apply(im_b=im_b)
    thresh = cv2.bitwise_not(thresh)

    # Define kernels para operações morfológicas
    kernel2_dilate = cv2.getStructuringElement(cv2.MORPH_DILATE, (1, 1))
    kernel_circle = cv2.getStructuringElement(cv2.MORPH_CROSS, (2, 1))
    kernel_ellipse = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (1, 2))
    kernel_open = cv2.getStructuringElement(cv2.MORPH_CLOSE, (2, 1))

    # Aplica operações morfológicas para melhorar a imagem
    i = 1
    for item in [kernel_circle, kernel_ellipse, kernel_open, kernel2_dilate]:
        thresh = cv2.medianBlur(thresh, i)
        thresh = cv2.erode(thresh, item, iterations=1)

    # cv2.imwrite(process_dbg, thresh)

    # Sequência de dilatações e erosões para refinar caracteres
    kernel1 = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    thresh = cv2.dilate(thresh, kernel1, iterations=1)
    # cv2.imwrite(process_dbg, thresh)

    kernel2 = cv2.getStructuringElement(cv2.MORPH_CROSS, (2, 1))
    thresh = cv2.erode(thresh, kernel2, iterations=1)
    # cv2.imwrite(process_dbg, thresh)

    kernel2 = cv2.getStructuringElement(cv2.MORPH_DILATE, (2, 1))
    thresh = cv2.erode(thresh, kernel2, iterations=1)
    # cv2.imwrite(process_dbg, thresh)

    kernel2 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (1, 1))
    thresh = cv2.erode(thresh, kernel2, iterations=1)
    cv2.imwrite(process_dbg, thresh)

    kernel2 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 1))
    thresh = cv2.erode(thresh, kernel2, iterations=1)
    # cv2.imwrite(process_dbg, thresh)

    # Aplica OCR usando pytesseract
    text_pytesseract = str(pytesseract.image_to_string(thresh))
    text = re.sub(
        r"[^a-z0-9]",
        "",
        text_pytesseract.lower().replace("\n", "").strip().replace(" ", ""),
    )

    return text
