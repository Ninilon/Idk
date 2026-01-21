import requests
import base64
from .. import loader, utils

@loader.tds
class GitHubUploader(loader.Module):
    """GitHub Uploader с настройкой через конфиг"""
    strings = {"name": "GitHubUpload"}

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "token",
                "",
                lambda: "GitHub Personal Access Token",
                validator=loader.validators.Hidden(),
            ),
            loader.ConfigValue(
                "username",
                "ninilon",
                lambda: "Ваш юзернейм на GitHub",
            ),
            loader.ConfigValue(
                "repo",
                "idk",
                lambda: "Название репозитория",
            ),
            loader.ConfigValue(
                "branch",
                "main",
                lambda: "Ветка репозитория",
            ),
        )

    async def ghupcmd(self, message):
        """<имя_файла> - Загрузить файл на GitHub"""
        args = utils.get_args_raw(message)
        reply = await message.get_reply_message()
        
        if not reply or not reply.media:
            return await message.edit("<b>Реплай на файл!</b>")

        # Проверка заполнения токена
        if not self.config["token"]:
            return await message.edit("<b>❌ Ошибка: Токен не установлен в конфиге!</b>")

        token = self.config["token"]
        user = self.config["username"]
        repo = self.config["repo"]
        branch = self.config["branch"]
        path = args.strip() if args else "file.py"
        
        url = f"https://api.github.com/repos/{user}/{repo}/contents/{path}"
        
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Hikka-Userbot",
            "Host": "api.github.com" 
        }

        await message.edit(f"<i>📡 Загрузка на GitHub...</i>")
        
        try:
            file = await message.client.download_file(reply)
            content = base64.b64encode(file).decode("utf-8")
            
            # Проверка SHA (для обновления)
            r = requests.get(url, headers=headers, timeout=10)
            sha = r.json().get("sha") if r.status_code == 200 else None

            data = {
                "message": f"Upload {path} via Hikka",
                "content": content,
                "branch": branch
            }
            if sha:
                data["sha"] = sha

            res = requests.put(url, headers=headers, json=data, timeout=15)

            if res.status_code in (200, 201):
                link = f"https://github.com/{user}/{repo}/blob/{branch}/{path}"
                await message.edit(f"<b>✅ Загружено на GitHub:</b>\n<a href='{link}'>Смотреть файл</a>")
            else:
                await message.edit(f"<b>❌ Ошибка API ({res.status_code}):</b>\n<code>{res.text}</code>")
                
        except Exception as e:
            await message.edit(f"<b>❌ Ошибка:</b>\n<code>{str(e)}</code>")
