import io
import base64
import numpy as np
import pytest
from utils import recaptcha

class DummyFile(io.BytesIO):
    """Classe auxiliar para simular arquivo binário de imagem."""
    pass

def gerar_imagem_teste() -> bytes:
    """Gere uma imagem simples em bytes para testes."""
    # Cria uma imagem preta 10x10
    img = np.zeros((10, 10, 3), dtype=np.uint8)
    _, buf = recaptcha.cv2.imencode('.png', img)
    return buf.tobytes()

def test_load_img_blur_apply_retorna_ndarray() -> None:
    """Teste se load_img_blur_apply retorna um np.ndarray."""
    img_bytes = gerar_imagem_teste()
    resultado = recaptcha.load_img_blur_apply(img_bytes)
    assert isinstance(resultado, np.ndarray)
    assert resultado.shape[0] == 10 and resultado.shape[1] == 10

def test_reabre_imagem_retorna_ndarray() -> None:
    """Teste se reabre_imagem retorna um np.ndarray."""
    img_bytes = gerar_imagem_teste()
    dummy_file = DummyFile(img_bytes)
    resultado = recaptcha.reabre_imagem(dummy_file)
    assert isinstance(resultado, np.ndarray)
    assert resultado.shape[0] == 10 and resultado.shape[1] == 10

def test_captcha_to_image_retorna_str() -> None:
    """Teste se captcha_to_image retorna uma string de 6 caracteres."""
    img_bytes = gerar_imagem_teste()
    img_b64 = base64.b64encode(img_bytes).decode()
    resultado = recaptcha.captcha_to_image(img_b64)
    assert isinstance(resultado, str)
    assert len(resultado) == 6

def test_captcha_to_image_com_base64_prefixo() -> None:
    """Teste captcha_to_image com prefixo data:image/png;base64.
    Gera imagem válida em base64 para evitar erro de padding.
    """
    # Gera imagem de teste válida
    img_bytes = gerar_imagem_teste()
    img_b64 = base64.b64encode(img_bytes).decode()
    # Adiciona prefixo conforme esperado pela função
    img_b64_prefixed = f"data:image/png;base64,{img_b64}"
    # Executa função e valida retorno
    resultado = recaptcha.captcha_to_image(img_b64_prefixed)
    assert isinstance(resultado, str)
    assert len(resultado) == 6

def test_load_img_blur_apply_erro_tipo() -> None:
    """Teste se load_img_blur_apply levanta erro com tipo inválido."""
    with pytest.raises(TypeError):
        recaptcha.load_img_blur_apply("string_invalida")

def test_reabre_imagem_erro_tipo() -> None:
    """Teste se reabre_imagem levanta erro com tipo inválido."""
    with pytest.raises(AttributeError):
        recaptcha.reabre_imagem("string_invalida")
