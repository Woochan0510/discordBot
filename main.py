import discord
from discord.ext import commands, tasks
import random
import datetime
import asyncio 

f = open('./token.txt', 'r')
token = f.read()

#봇의 접두사 설정
intents = discord.Intents.default()
intents.members = True # 멤버 접근 권한 활성화
intents.message_content = True # 채팅 읽는 권한 부여
bot = commands.Bot(command_prefix='!', intents=intents)

TARGET_GUILD_ID = 1448669313534918740

#서버 역할 목록
RANDOM_ROLES = ["닉변1", "닉변2", "닉변3", "닉변4", "닉변5", "닉변6", "닉변7"]

@bot.event
async def on_ready():
    print(f'봇이 입장하였습니다: {bot.user.name}')
    #봇이 켜지면 스케줄러 시작
    if not assign_random_role.is_running():
        assign_random_role.start()
        print("자동 역할 부여가 시작되었습니다.")

utc = datetime.timezone.utc
kst = datetime.timezone(datetime.timedelta(hours=9))
time_to_run = datetime.time(hour=12, minute=0, tzinfo=kst)

@bot.command()
async def 안녕(ctx):
    await ctx.send(f'{ctx.author.mention}님, 안녕하세요! 반가워요 👋')

@tasks.loop(time=time_to_run)
async def assign_random_role():
    if datetime.datetime.now(kst).weekday() != 0:
        return

    guild = bot.get_guild(TARGET_GUILD_ID)
    if guild is None:
        return
    
    assignable_roles = [role for role in guild.roles if role.name in RANDOM_ROLES]

    if not assignable_roles:
        print("부여할수 있는 역할이 서버에 존재하지 않습니다. `RANDOM_ROLES`를 확인해주세요.")
        return
    
    for member in guild.members:
        if member.bot:
            continue
        
        if member.id == guild.owner_id:
            continue

        try:
            roles_to_remove = [role for role in member.roles if role.name in RANDOM_ROLES]
            if roles_to_remove:
                await member.remove_roles(*roles_to_remove, reason="주간 랜덤 역할 초기화")

            new_role = random.choice(assignable_roles)
            await member.add_roles(new_role, reason="주간 랜덤 역할 부여")
            print(f"{member.display_name} -> {new_role.name} 부여 완료")

            await asyncio.sleep(1) # API 제한 방지 (1초 대기)
        except discord.Forbidden:
            print(f"권한 부족: {member.display_name}님을 건드릴 수 없습니다.")
        except Exception as e:
            print(f"오류 발생 ({member.display_name}): {e}")

    print("모든 멤버의 역할 변경이 완료되었습니다.")

bot.run(token)