#VK Bot

##Prepare

1. Create an **image** folder and put your images in it
2. Create .env file using **.env_sample**, where:
   * `SEARCH_GROUP` - Keyword for searching for groups in which photos will be added in the comments to the last post.
   * `ALBUM_NAME` - The name of the album in which photos from the **image** folder will be preliminarily added for further work of the bot.
   * `VK_USER` - Vk login (email or phone number)
   * `VK_PASSWORD` - Vk password
3. `docker-compose build`
4. `docker-compose up -d captcha-ml`

##Usage
* Just run `docker-compose up bot` and watch progress. Bot will join the 20 most popular groups and leave comments.
* If you need to change account or keyword, just change **.env** file and run `docker-compose up bot` again
