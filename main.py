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
periodic_time = datetime.time(hour=12, minute=0, tzinfo=kst)

@bot.command()
async def 안녕(ctx):
    embed = discord.Embed(
        title="👋 안녕하세요!",
        description=f"반가워요, {ctx.author.mention}님!\n오늘도 즐거운 하루 보내세요.",
        color=discord.Color.gold()
    )
    embed.set_thumbnail(url=ctx.author.display_avatar.url)
    embed.set_footer(text=f"{bot.user.name} 드림", icon_url=bot.user.display_avatar.url)
    await ctx.send(embed=embed)

@bot.command()
async def 북(ctx):
    embed = discord.Embed(
        title="북",
        description="딱"
    )
    color=discord.Color.random()
    await ctx.send(embed=embed)

@bot.command()
async def 딱(ctx):
    embed = discord.Embed(
        title="제가 딱 한마디만 하겠습니다",
        description="이야 기분좋다"
    )
    color=discord.Color.random()
    await ctx.send(embed=embed)

@bot.command()
async def 노무(ctx):
    embed = discord.Embed(
        title="프로필사진",
        description=f"예아, {ctx.author.mention}님이 닉네임을 변경했노"
    )
    color=discord.Color.random()
    await ctx.send(embed=embed)
    await ctx.author.edit(nick="노무현")


@bot.command()
async def 랜덤역할(ctx):
    if ctx.author.id != ctx.guild.owner_id:
        embed = discord.Embed(
            title="🚫 접근 거부",
            description="이 명령어는 **서버 방장**만 사용할 수 있습니다.",
            color=0xff0000 # 빨간색
        )
        await ctx.send(embed=embed)
        return
    
    target_members = [m for m in ctx.guild.members if not m.bot and m.id != ctx.guild.owner_id]

    assignable_roles = [role for role in ctx.guild.roles if role.name in RANDOM_ROLES]

    if len(target_members) > len(assignable_roles):
        embed = discord.Embed(
            title="❌ 개수 부족 오류",
            description=f"사람은 {len(target_members)}명인데 역할은 {len(assignable_roles)}개뿐입니다.",
            color=0xff0000
        )
        await ctx.send(embed=embed)
        return
    
    loading_embed = discord.Embed(
        title="🔄 작업 시작",
        description=f"총 **{len(target_members)}명**의 역할을 섞고 닉네임을 변경합니다...",
        color=0x0000ff # 파란색
    )
    
    await ctx.send(embed=loading_embed)
    random.shuffle(assignable_roles)    
    count = 0

    for member, new_role in zip(target_members, assignable_roles):
        try:
            roles_to_remove = [r for r in member.roles if r.name in RANDOM_ROLES]
            if roles_to_remove:
                await member.remove_roles(*roles_to_remove, reason="랜덤 역할 초기화")

            await member.add_roles(new_role, reason="랜덤 역할 부여")

            count += 1
            await asyncio.sleep(1) # API 제한 방지 (1초 대기)
        except discord.Forbidden:
            print(f"권한 부족: {member.display_name}님을 건드릴 수 없습니다.")
        except Exception as e:
            print(f"오류 발생 ({member.display_name}): {e}")
    
    success_embed = discord.Embed(
        title="✅ 작업 완료!",
        description=f"총 **{count}명**의 역할과 닉네임 변경을 마쳤습니다.",
        color=0x00ff00 # 초록색
    )
    success_embed.set_footer(text="봇이 자동으로 수행함")
    await ctx.send(embed=success_embed)

@tasks.loop(time=periodic_time)
async def assign_random_role():
    if datetime.datetime.now(kst).weekday() != 0:
        print("오늘은 월요일이 아닙니다.")
        return

    print("월요일 12시! 역할 섞기를 시작합니다.")

    guild = bot.get_guild(TARGET_GUILD_ID)
    if guild is None:
        print("오류: 서버 ID를 찾을수 없습니다. TARGET_GUILD_ID를 확인해주세요!!!")
        return
    
    target_members = [m for m in guild.members if not m.bot and m.id != guild.owner_id]
    assignable_roles = [role for role in guild.roles if role.name in RANDOM_ROLES]

    if len(target_members) > len(assignable_roles):
        print("역할의 개수가 부족합니다.")
        return
    
    random.shuffle(assignable_roles)
    print(f"총 {len(target_members)}명에게 역할을 배분합니다...")

    for member, new_role in zip(target_members):
        try:
            roles_to_remove = [r for r in member.roles if r.name in RANDOM_ROLES]
            if roles_to_remove:
                await member.remove_roles(*roles_to_remove, reason="주간 랜덤 역할 초기화")

            await member.add_roles(new_role, reason="주간 랜덤 역할 부여")
            print(f"{member.display_name} -> {new_role.name} 부여 완료")

            await asyncio.sleep(1) # API 제한 방지 (1초 대기)
        except discord.Forbidden:
            print(f"권한 부족: {member.display_name}님을 건드릴 수 없습니다.")
        except Exception as e:
            print(f"오류 발생 ({member.display_name}): {e}")

    print("이번주 모든 멤버의 역할 변경이 완료되었습니다.")

bot.run(token)