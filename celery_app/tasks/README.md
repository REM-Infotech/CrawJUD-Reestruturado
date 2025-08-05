# Documentação da Pasta tasks

## Introdução

Esta pasta contém as definições das tarefas assíncronas que serão executadas pelo Celery. Cada módulo pode conter uma ou mais funções de tarefa, organizadas conforme a lógica do projeto.

## Estrutura

- Módulos Python com funções decoradas como tarefas Celery.

## Exemplo de Uso

Implemente novas tarefas criando funções decoradas com `@celery_app.task` e importe-as conforme necessário.
