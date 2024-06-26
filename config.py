# Cyberspace bot

##This source serves as a base for Cyberspace store bots.
##It aims to be as modular as possible, allowing adding new features with minor effort.

## Example config file
#6203838763:AAFKHxOaQilei4GnWtvyJ6NPXI03qwhuFI8
##```python
# Your Telegram bot token.
BOT_TOKEN = "6960140852:AAG68TEYqFA2tOB81qpfgYGJuxUEUfJMjVU"

# Telegram API ID and Hash. This is NOT your bot token and shouldn't be changed.
API_ID = 9641313
API_HASH = "baefb797b70643121704c7f344b92870"

# Chat used for logging errors.
LOG_CHAT = 6739589584

# Chat used for logging user actions (like buy, gift, etc).
ADMIN_CHAT = 6739589584
GRUPO_PUB = -1001896001178


# How many updates can be handled in parallel.
# Don't use high values for low-end servers.
WORKERS = 20

# Os administradores podem acessar o painel e adicionar novos materiais ao bot.
ADMINS = [6739589584]

# Sudoers têm acesso total ao servidor e podem executar comandos.
SUDOERS = [6739589584]

# Todos os sudoers também devem ser administradores.
ADMINS.extend(SUDOERS)

GIFTERS = [6739589584]

# Bote o Username do bot sem o @
# Exemplo: default
BOT_LINK = "ferprivs_bot"


# Bote o Username do suporte sem o @
# Exemplo: suporte
BOT_LINK_SUPORTE = "ferprivs"
##```