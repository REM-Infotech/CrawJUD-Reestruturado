Especifique o tipo do commit (ex.: `chore`, `refact`, etc.)

- Ao gerar mensagens de commit, o Copilot deve sugerir um título breve, descritivo e no imperativo, indicando resumidamente a principal alteração realizada. No corpo (body) da mensagem de commit, o Copilot deve detalhar separadamente as alterações feitas em cada arquivo modificado, listando o nome do arquivo seguido de uma breve descrição da mudança correspondente. Por exemplo:

```xml
✨ *<type>: <short summary>*

<detailed description - what, why, how>

Arquivos Alterados:
- *<path/file1.ext>*: <short summary of what changed>
- *<path/file2.ext>*: <short summary of what changed>
```

- O Copilot deve sugerir mensagens automaticamente sempre que alterações forem detectadas, apresentando a sugestão em cinza-claro na caixa de commit. O usuário pode aceitar a sugestão pressionando Tab ou visualizar mais opções pressionando Ctrl+Space. Caso a sugestão não apareça, o Copilot deve permitir que o usuário acione novas sugestões digitando / na caixa de commit.

- Certifique-se de que a configuração github.copilot.enableCommitMessageSuggestions está habilitada para que as sugestões de commit apareçam.

- Recomenda-se também sugerir o uso de emojis no início do título do commit, conforme o tipo de alteração, como por exemplo: ✨ para nova feature, 🐛 para correção de bug, 🔧 para ajustes de configuração, entre outros.

- Os commits precisam ser em português, mas o type e o scope ficam em inglês

- Quando a sugestão envolver alteração de local de pasta, nome de arquivo ou estrutura, gere uma mensagem clara explicando que se trata de uma alteração (e não de uma inserção). Seja direto e técnico na explicação.
