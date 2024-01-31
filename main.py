## @author shadowvvf
# Conda installation:
# conda create -n tgbot python=3.11.5
# conda activate tgbot
# pip install -r requirements.txt

from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
import requests

# Заменить на токен
TELEGRAM_BOT_TOKEN = 'token'
# можешь не пробовать юзать токен который был в прошлом коммите, всё равно он не рабочий :)

def start(update: Update, context: CallbackContext):
    update.message.reply_text('Привет! Отправь мне GitHub имя пользователя, чтобы получить информацию о нем.')

def get_repo_info(update: Update, context: CallbackContext):
    args = context.args
    if len(args) < 2:
        update.message.reply_text('Пожалуйста, укажите имя пользователя и название репозитория после команды.')
        return

    username, repo_name = args[0], args[1]
    repo_url = f'https://api.github.com/repos/{username}/{repo_name}'
    response = requests.get(repo_url)
    if response.status_code == 200:
        repo_data = response.json()
        repo_info = f"""
🏷Название: {repo_data.get('name', 'Недоступно')}
👤Владелец: {repo_data.get('owner', {}).get('login', 'Недоступно')}
📂Количество форков: {repo_data.get('forks_count', 'Недоступно')}
⭐️Звёзды: {repo_data.get('stargazers_count', 'Недоступно')}
👀Просмотры: {repo_data.get('watchers_count', 'Недоступно')}
🔗URL: {repo_data.get('html_url', 'Недоступно')}
        """
        update.message.reply_text(repo_info)

        # Чисто технически функция есть, и она показывает содержимое репозитория, но она была отключена поскольку на github стоит rate limit
        # для запросов, а именно их всего 60. И восстанавливаются они примерно 30 минут. Так что функция была отключена
        # для экономии этого самого rate limit

        """contents_url = repo_data.get('contents_url', '').replace('{+path}', '')
        contents_response = requests.get(contents_url)
        if contents_response.status_code == 200:
            contents_data = contents_response.json()
            file_hierarchy = format_file_hierarchy(contents_data)
            update.message.reply_text(file_hierarchy)
        else:
            update.message.reply_text('Ошибка при попытке получить содержимое репозитория.')"""

    else:
        update.message.reply_text('Произошла ошибка при получении информации о репозитории GitHub.')

"""
def format_file_hierarchy(contents_data, path_prefix=''):
    hierarchy = ''
    for item in contents_data:
        if item['type'] == 'file':
            hierarchy += f"📄{path_prefix}{item['name']}\n"
        elif item['type'] == 'dir':
            hierarchy += f"📂{path_prefix}{item['name']}\n"
            # Recursively get the contents of the directory
            dir_contents_url = item['url']
            dir_contents_response = requests.get(dir_contents_url)
            if dir_contents_response.status_code == 200:
                dir_contents_data = dir_contents_response.json()
                hierarchy += format_file_hierarchy(dir_contents_data, f"{path_prefix}{item['name']}/")
    return hierarchy
"""

def get_user_info(update: Update, context: CallbackContext):
    username = ' '.join(context.args)
    if not username:
        update.message.reply_text('Пожалуйста, укажите имя пользователя GitHub после команды.')
        return

    user_url = f'https://api.github.com/users/{username}'
    response = requests.get(user_url)
    if response.status_code == 200:
        user_data = response.json()
        stars_url = user_data.get('starred_url', '').split('{')[0]  # Убрать {/owner}{/repo}
        stars_response = requests.get(stars_url)
        stars_count = len(stars_response.json()) if stars_response.ok else 'Недоступно'
        
        user_info = f"""
🏷Имя: {user_data.get('name', 'Недоступно')}
👤Профиль: {user_data.get('html_url', 'Недоступно')}
📂Количество репозиториев: {user_data.get('public_repos', 'Недоступно')}
👥Подписчики: {user_data.get('followers', 'Недоступно')}
🌟Звёзд: {stars_count}
        """
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Смотреть репозитории", url=f'https://github.com/{username}?tab=repositories')]
        ])
        
        update.message.reply_text(user_info, reply_markup=keyboard)
    else:
        update.message.reply_text('Произошла ошибка при получении информации о пользователе GitHub.')

def main():
    updater = Updater(TELEGRAM_BOT_TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("getuserinfo", get_user_info, pass_args=True))
    dp.add_handler(CommandHandler("getrepoinfo", get_repo_info, pass_args=True))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()