import discord
import traceback
import httpx
from config import get_config
from discord import app_commands


# 아이템 json 정보를 embed로 바꾸는 함수
def item_to_embed(item):
    item_name = item['Name']
    item_quality = item['GradeQuality']
    item_price = item['AuctionInfo']['BuyPrice']
    item_thumbnail = item['Icon']
    item_trade_count = item['AuctionInfo']['TradeAllowCount']
    embed = discord.Embed(title="경매장 아이템 알람")
    embed.set_thumbnail(url=item_thumbnail)
    item_options = item['Options']

    embed.add_field(name="이름", value=item_name, inline=True)
    embed.add_field(name="품질", value=item_quality, inline=True)
    embed.add_field(name="가격", value=item_price, inline=True)
    embed.add_field(name="거래 가능 횟수", value=item_trade_count, inline=True)

    # item_options는 배열에 json 객체가 있음. 순서대로 스탯1, 스탯2(목걸이), 패널티, 각인1, 각인2
    for i in range(len(item_options)):
        embed.add_field(name=item_options[i]['OptionName'], value=item_options[i]['Value'], inline=True)
    return embed

async def get_user_key(user_id):
    user_key = ''

    return user_key


# 봇 클라이언트
class MyClient(discord.Client):

    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        super().__init__(intents=intents)

        self.tree = app_commands.CommandTree(self)

    async def alarm(self, user_id: int, items: list):
        user = self.get_user(user_id)
        if user:
            for item in items:
                print(item)
                embed = item_to_embed(item)
                await user.send(embed=embed)
        return 1

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')

    async def on_member_join(self, member):
        dm_channel = await member.create_dm()
        await dm_channel.send(f'안녕하세요, {member.name}님! /join 커맨드를 사용해서 유저 등록을 진행해주세요!'
                              f'입력받은 API 키는 암호화하여 안전하게 보관합니다.')

    async def setup_hook(self) -> None:
        await self.tree.sync(guild=None)  # 디스코드 서버에 등록하기


class JoinModal(discord.ui.Modal, title='유저 등록'):
    lostark_api_key = discord.ui.TextInput(
        label='API KEY',
        placeholder='API 키를 입력해주세요.'
    )

    async def on_submit(self, interaction) -> None:
        cocomo_key = await self.join(interaction.user.id, self.lostark_api_key.value)
        await interaction.response.send_message(f'정상적으로 API 키를 암호화하여 등록했습니다!'
                                                f'웹 서비스 https://ouohoon.github.io 를 이용하실 때는 지금 발급한 키로 로그인 하세요.'
                                                f'코코모 키: {cocomo_key}')

    async def on_error(self, interaction, error) -> None:
        await interaction.response.send_message(f'오류가 발생했습니다! 이미 등록한 디스코드 아이디거나 올바르지 않은 API 키입니다.')

        traceback.print_exception(type(error), error, error.__traceback__, file=open('bot_errors.log', 'a+'))

    async def join(self, user_id: int, api_key: str):
        async with httpx.AsyncClient(verify=False) as client: # 개발용으로 verify=False
            response = await client.get(get_config()['csrf_url'])
            csrf = response.headers['set-cookie']
            start = csrf.find("=") + 1
            end = csrf.find(";")
            headers = {
                'X-XSRF-TOKEN': csrf[start:end],
                'Content-Type': 'application/json'
            }
            data = {
                "discordId": user_id,
                "apiKey": api_key
            }

            response = await client.post(get_config()['join_url'],
                                         json=data, headers=headers, cookies=client.cookies)
            if response.status_code == 200:
                print(response.json())
                cocomo_key = response.json()['data']['cocomoKey']
                return cocomo_key
