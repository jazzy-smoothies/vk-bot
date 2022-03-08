import asyncio
from vkbottle import UserAuth
from vkbottle import API
from vkbottle import VKAPIError
from vkbottle import CaptchaError
from vkbottle.tools import PhotoToAlbumUploader
from os import walk
import os
import random
import requests
from vk_api_error_validator import VKAPIErrorResponseValidator

IMAGE_FOLDER_PATH = 'image'
CACHE_FOLDER_NAME = 'cache'


class VKBot:
    def __init__(self, api: API):
        self.api = api
        self.protos = []

    async def go(self):
        await self.create_album()
        await self.spam_groups()

    async def search_groups(self):
        groups = await self.api.groups.search(os.environ['SEARCH_GROUP'])
        return groups.items

    async def spam_groups(self):
        groups = await self.search_groups()
        added_groups = []
        for group in groups:
            try:
                # time.sleep(0.5)
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
                        attachments=random.choice(self.protos)
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

    async def create_album(self):
        if not os.path.exists(CACHE_FOLDER_NAME):
            os.makedirs(CACHE_FOLDER_NAME)
        size = 0

        for e in os.scandir(IMAGE_FOLDER_PATH):
            size += os.path.getsize(e)
        cache_path = CACHE_FOLDER_NAME + '/' + 'photos_' + str(size) + os.environ['VK_USER']
        cache_exist = os.path.exists(cache_path)
        if cache_exist:
            with open(cache_path) as f:
                self.protos = f.read().splitlines()
            return
        else:
            cache_file = open(cache_path, "w")

        # raise Exception
        album_name = os.environ['ALBUM_NAME']
        print(f'Start album "{album_name}" creation...')
        alb = await self.api.photos.create_album(album_name)
        for (_, _, filenames) in walk(IMAGE_FOLDER_PATH):
            for filename in filenames:
                upload = await PhotoToAlbumUploader(self.api) \
                    .upload(album_id=alb.id, paths_like=IMAGE_FOLDER_PATH + '/' + filename)
                upload = upload[0]
                self.protos.append(upload)
                if not cache_exist:
                    cache_file.write(upload + "\n")
                print(f'Image {filename} added successfully')
        if not cache_exist:
            cache_file.close()


async def main():
    token = await UserAuth().get_token(os.environ['VK_USER'], os.environ['VK_PASSWORD'])
    api = API(token)
    api.add_captcha_handler(captcha_handler)
    api.response_validators.insert(1, VKAPIErrorResponseValidator())
    x = VKBot(api)
    print("login success. Ok, let's go!")
    await x.go()


async def captcha_handler(error: CaptchaError):
    captcha_url = os.environ['CAPTCHA_ML_URL']
    res = requests.post(f'http://{captcha_url}:3333/captcha-solve', data={'link': error.img})
    return res.json()['result']


asyncio.run(main())
