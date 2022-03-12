import asyncio

from vkbottle import UserAuth
from vkbottle import API
from vkbottle import VKAPIError
from vkbottle import CaptchaError
from vkbottle.tools import PhotoToAlbumUploader
from vkbottle.tools import VideoUploader
from os import walk
import os
import random
import requests
from vk_api_error_validator import VKAPIErrorResponseValidator

IMAGE_FOLDER_PATH = 'image'
CACHE_FOLDER_NAME = 'cache'
ACCOUNTS_FILE_PATH = 'accounts.txt'
KEYWORDS_FILE_PATH = 'keywords.txt'


class VKBot:
    def __init__(self):
        self.api = None
        self.protos = []
        self.accounts = []
        keywords = []
        if os.path.exists(ACCOUNTS_FILE_PATH):
            with open(ACCOUNTS_FILE_PATH) as f:
                for account_line in f.read().splitlines():
                    account_creds = account_line.split(':')
                    self.accounts.append({'login': account_creds[0], 'password': account_creds[1]})
        else:
            self.accounts.append({'login': os.environ['VK_USER'], 'password': os.environ['VK_PASSWORD']})
        random.shuffle(self.accounts)
        if os.path.exists(KEYWORDS_FILE_PATH):
            with open(KEYWORDS_FILE_PATH) as f:
                keywords = f.read().splitlines()
        else:
            keywords.append(os.environ['SEARCH_GROUP'])
        if len(keywords) < len(self.accounts):
            self.accounts = self.accounts[0:len(keywords)]
        self.keywords = keywords

    async def chunks(self):
        n = len(self.accounts)
        i = 0
        for keyword in self.keywords:
            if i > n - 1:
                i = 0
            account = self.accounts[i]
            await self.go(account['login'], account['password'], keyword)
            i = i + 1

    async def go(self, user, password, group):
        await self.login(user, password)
        await self.create_album(user)
        await self.spam_groups(group)

    async def search_groups(self, group):
        groups = await self.api.groups.search(group)
        return groups.items

    async def spam_groups(self, group):
        groups = await self.search_groups(group)
        added_groups = []
        for group in groups:
            try:
                print(f'Join to {group.name}')
                await self.api.groups.join(group_id=group.id)
            except VKAPIError as err:
                if err.code != 15:
                    raise err

            added_groups.append(group)
        for added_group in added_groups:
            try:
                wall = await self.api.wall.get(owner_id=-added_group.id, count=5)
            except Exception as e:
                continue

            last_post_retry_count = 5
            for item in wall.items:
                try:
                    await self.api.wall.create_comment(
                        owner_id=-added_group.id,
                        post_id=item.id,
                        attachments=random.choice(self.protos),
                        message=os.environ['MESSAGE'] if 'MESSAGE' in os.environ else None
                    )
                except Exception as e:
                    if last_post_retry_count == 0:
                        print('The group does not have permission to add comments. Skipping....')
                        break
                    last_post_retry_count = last_post_retry_count - 1
                    continue
                print('-----------------------------------------------------------------------------------')
                print(f'Post added Success on {added_group.name} group on {item.text} post')
                break

    async def create_album(self, user):
        if not os.path.exists(CACHE_FOLDER_NAME):
            os.makedirs(CACHE_FOLDER_NAME)
        size = 0

        for e in os.scandir(IMAGE_FOLDER_PATH):
            size += os.path.getsize(e)
        cache_path = CACHE_FOLDER_NAME + '/' + 'photos_' + str(size) + user
        cache_exist = os.path.exists(cache_path)
        if cache_exist:
            with open(cache_path) as f:
                self.protos = f.read().splitlines()
            return
        else:
            cache_file = open(cache_path, "w")

        album_name = os.environ['ALBUM_NAME']
        print(f'Start album "{album_name}" creation...')
        alb = await self.api.photos.create_album(album_name)
        for (_, _, filenames) in walk(IMAGE_FOLDER_PATH):
            for filename in filenames:
                full_path = IMAGE_FOLDER_PATH + '/' + filename
                ext = filename.split('.')[1]
                if ext in ['DS_Store']:
                    continue
                is_video = ext in ['avi', 'mp4']
                upload = await VideoUploader(self.api).upload(file_source=full_path) \
                    if is_video \
                    else await PhotoToAlbumUploader(self.api).upload(album_id=alb.id, paths_like=full_path)

                self.protos.append(upload)
                if not cache_exist:
                    cache_file.write(upload + "\n")
                print(f'Image {filename} added successfully')
        if not cache_exist:
            cache_file.close()

    async def login(self, username, password):
        token = await UserAuth().get_token(username, password)
        self.api = API(token)
        self.api.add_captcha_handler(captcha_handler)
        self.api.response_validators.insert(1, VKAPIErrorResponseValidator())
        print("login success. Ok, let's go!")


async def main():
    x = VKBot()
    await x.chunks()


async def captcha_handler(error: CaptchaError):
    captcha_url = os.environ['CAPTCHA_ML_URL']
    res = requests.post(f'http://{captcha_url}:3333/captcha-solve', data={'link': error.img})
    return res.json()['result']


asyncio.run(main())
