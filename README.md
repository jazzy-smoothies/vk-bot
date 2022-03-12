# VK Bot

## Prepare

1. Create an **image** folder and put your images or\and video files (`mp4` or `avi`) in it
2. Create .env file using **.env_sample**, where:
   * `SEARCH_GROUP` - Keyword for searching for groups in which photos will be added in the comments to the last post.
   * `MESSAGE` - (optional) Text on comment
   * `ALBUM_NAME` - The name of the album in which photos from the **image** folder will be preliminarily added for further work of the bot.
   * `VK_USER` - Vk login (email or phone number)
   * `VK_PASSWORD` - Vk password
3. `docker-compose build`
4. `docker-compose up -d captcha-ml`

## Usage
* Just run `docker-compose up bot` and watch progress. Bot will join the 20 most popular groups and leave comments.
* If you need to change account or keyword, just change **.env** file and run `docker-compose up bot` again

## Working with a bunch of accounts and/or keywords
* If you have a list of accounts, you need to create a file `accounts.txt` in the following format:
```
login1:password1
login2:password2
login3:password3
...
```
* If you want to use a list of keywords for searching, create a file `keywords.txt` like this:
```
keyword1
keyword2
keyword3
...
```
NOTE: You can have only `accounts.txt` or only `keywords.txt`, or both, or neither (if there is no file, the keyword or login \ password will be used from the `.env`)

## Usefully Links
* [Free VPN](https://clearvpn.com/apps/#download)
* [By VK accounts](https://darkstore.su/) - You can purchase accounts using Dodgecoin (minimum fee)
