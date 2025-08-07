from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T = TypeVar("AnyType")


class A(ABC):
    """
    Defina interface abstrata para classes derivadas.

    Args:
        Nenhum argumento específico.

    Returns:
        None: Não retorna valor.

    Raises:
        NotImplementedError: Caso método não seja implementado.
    """
    @abstractmethod
    def funcao_abs(self, *args: Generic[T], **kwargs: Generic[T]) -> None:
        """
        Declare método abstrato a ser implementado por subclasses.

        Args:
            *args (Generic[T]): Argumentos posicionais genéricos.
            **kwargs (Generic[T]): Argumentos nomeados genéricos.

        Returns:
            None: Não retorna valor.

        Raises:
            NotImplementedError: Método deve ser implementado por subclasses.
        """

class B(A):
    """
    Estenda interface abstrata A e adicione novo método abstrato.

    Args:
        Nenhum argumento específico.

    Returns:
        None: Não retorna valor.

    Raises:
        NotImplementedError: Caso método não seja implementado.
    """
    @abstractmethod
    def funcao_abs2(self, *args: Generic[T], **kwargs: Generic[T]) -> None:
        """
        Declare segundo método abstrato para subclasses.

        Args:
            *args (Generic[T]): Argumentos posicionais genéricos.
            **kwargs (Generic[T]): Argumentos nomeados genéricos.

        Returns:
            None: Não retorna valor.

        Raises:
            NotImplementedError: Método deve ser implementado por subclasses.
        """


class C(A):
    """
    Implemente método abstrato da classe A.

    Args:
        Nenhum argumento específico.

    Returns:
        None: Não retorna valor.
    """
    def funcao_abs(self, *args: Generic[T], **kwargs: Generic[T]) -> None:
        """
        Implemente método abstrato exibindo mensagem.

        Args:
            *args (Generic[T]): Argumentos posicionais genéricos.
            **kwargs (Generic[T]): Argumentos nomeados genéricos.

        Returns:
            None: Não retorna valor.
        """
        print("Pão de queijo")  # Exibe mensagem ao chamar método.


class D(B):
    """
    Implemente métodos abstratos das classes A e B.

    Args:
        Nenhum argumento específico.

    Returns:
        None: Não retorna valor.
    """
    def funcao_abs(self, *args: Generic[T], **kwargs: Generic[T]) -> None:
        """
        Implemente método abstrato exibindo mensagem.

        Args:
            *args (Generic[T]): Argumentos posicionais genéricos.
            **kwargs (Generic[T]): Argumentos nomeados genéricos.

        Returns:
            None: Não retorna valor.
        """
        print("Pão de queijo")  # Exibe mensagem ao chamar método.

    def funcao_abs2(self, *args: Generic[T], **kwargs: Generic[T]) -> None:
        """
        Implemente segundo método abstrato exibindo mensagem.

        Args:
            *args (Generic[T]): Argumentos posicionais genéricos.
            **kwargs (Generic[T]): Argumentos nomeados genéricos.

        Returns:
            None: Não retorna valor.
        """
        print("Café com Leite")  # Exibe mensagem ao chamar método.


"""
Implemente abstrações utilizando classes abstratas em Python.

Args:
    Nenhum argumento aplicável.

Returns:
    None: Este módulo não retorna valores diretamente.

Raises:
    Nenhuma exceção específica.

Resumo:
Utilize o módulo abc para definir interfaces abstratas por meio de classes
que herdam de ABC e métodos decorados com @abstractmethod. Classes abstratas
não podem ser instanciadas diretamente e servem como base para subclasses
que devem implementar todos os métodos abstratos definidos. O uso de
TypeVar e Generic permite flexibilidade de tipos nos métodos. Este padrão
é fundamental para garantir contratos de implementação e facilitar o
polimorfismo, promovendo código mais seguro e organizado.
"""
