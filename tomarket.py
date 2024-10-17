from colorama import Fore, Style
from datetime import datetime
from fake_useragent import FakeUserAgent
from time import sleep, time
from urllib.parse import parse_qs, unquote
import asyncio
import json
import os
import pytz
import random
import requests
import sys


class Colors:
    END = Style.RESET_ALL

async def loading_animation(message, duration):
    frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    end_time = time() + duration
    i = 0
    while time() < end_time:
        try:
            sys.stdout.write(f"\r{frames[i % len(frames)]} {message}")
            sys.stdout.flush()
        except UnicodeEncodeError:
            sys.stdout.write(f"\r* {message}")
            sys.stdout.flush()
        i += 1
        await asyncio.sleep(0.1)
    sys.stdout.write("\r" + " " * (len(message) + 2) + "\r")
    sys.stdout.flush()
    
def log_message(message, color=Colors.END, status="", end='\n'):
    status_symbol = "[+] ║" if status == "success" else "[-] ║" if status == "fail" else "[*] ║"
    sys.stdout.write(f"{color}{status_symbol} {message}{Colors.END}{end}")
    sys.stdout.flush()

async def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')

async def print_header():
    print(f"""{Fore.BLUE}
╔═══════════════════════════════════════════╗
║              Bot Automation               ║
║         Developed by @ItbaArts_Dev        ║
╚═══════════════════════════════════════════╝{Style.RESET_ALL}""")

def print_timestamp(message):
    now = datetime.now().isoformat(" ").split(".")[0]
    print(
        f"{Fore.BLUE + Style.BRIGHT}[ {now} ]{Style.RESET_ALL}"
        f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
        f"{message}"
    )


class Tomarket:
    def __init__(self):
        self.headers = {
            "host": "api-web.tomarket.ai",
            "connection": "keep-alive",
            "accept": "application/json, text/plain, */*",
            "user-agent": "Mozilla/5.0 (Linux; Android 10; Redmi 4A / 5A Build/QQ3A.200805.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/86.0.4240.185 Mobile Safari/537.36",
            "content-type": "application/json",
            "origin": "https://mini-app.tomarket.ai",
            "x-requested-with": "tw.nekomimi.nekogram",
            "sec-fetch-site": "same-site",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "referer": "https://mini-app.tomarket.ai/",
            "accept-language": "en-US,en;q=0.9",
        }

    def parse_query(self, query: str):
        parsed_query = parse_qs(query)
        parsed_query = {k: v[0] for k, v in parsed_query.items()}
        user_data = json.loads(unquote(parsed_query['user']))
        parsed_query['user'] = user_data
        return parsed_query

    async def user_login(self, query):
        url = 'https://api-web.tomarket.ai/tomarket-game/v1/user/login'
        try:
            await clear_terminal()
            await print_header()
            await loading_animation("Logging in...", 2)
            payload = {
                'init_data': query,
                'invite_code': '',
                'is_bot': False
            }
            response = requests.post(url=url, headers=self.headers, json=payload)
            data = self.response_data(response)
            token = f"{data['data']['access_token']}"
            log_message("Login successful", color=Fore.GREEN, status="success")
            return token
        except (Exception) as e:
            log_message(f"Login failed: {e}", color=Fore.RED, status="fail")

    async def user_balance(self, token, random_number):
        url = 'https://api-web.tomarket.ai/tomarket-game/v1/user/balance'
        try:
            await clear_terminal()
            await print_header()
            await loading_animation("Fetching balance...", 2)
            self.headers.update({
                'Authorization': token
            })
            response = requests.post(url=url, headers=self.headers)
            data = self.response_data(response)
            if data is not None:
                log_message(
                    f"Available Balance: {data['data']['available_balance']} | Play Passes: {data['data']['play_passes']}",
                    color=Fore.YELLOW
                )
        
                while data['data']['play_passes'] > 0:
                    await asyncio.sleep(2)
                    point = 600
                    if random_number =='y':
                        point = random.randint(300,500)
                    await self.play_game(token=token, point=point)
                    data['data']['play_passes'] -= 1
            else:
                log_message('User balance data not found', color=Fore.RED, status="fail")
        except (Exception) as e:
            log_message(f"Error fetching balance: {e}", color=Fore.RED, status="fail")

    async def play_game(self, token, point):
        url = 'https://api-web.tomarket.ai/tomarket-game/v1/game/play'
        try:
            self.headers.update({
                'Authorization': token
            })
            
            payload = {
                'game_id': '59bcd12e-04e2-404c-a172-311a0084587d'
            }
            response = await asyncio.to_thread(requests.post, url=url, headers=self.headers, json=payload)
            data = self.response_data(response)
            if data is not None:
                if data['status'] == 0:
                    start_time = datetime.fromtimestamp(data['data']['start_at'])
                    end_time = datetime.fromtimestamp(data['data']['end_at'])
                    total_time = end_time - start_time
                    total_seconds = total_time.total_seconds()
                    log_message(f"Game Started Please Wait {int(total_seconds)} Seconds", color=Fore.GREEN + Style.BRIGHT)
                    slp = random.randint(30, 35)
                    sleep(slp)
                    await self.claim_game(token=token, points=point)
                elif data['status'] == 500:
                    log_message("No Chance To Play Game", color=Fore.YELLOW + Style.BRIGHT)
                else:
                    log_message(f"{data['message']}", color=Fore.RED + Style.BRIGHT)
            else:
                log_message('Data play game is None')
        except (Exception) as e:
            return log_message(f"{e}", color=Fore.RED + Style.BRIGHT)

    async def claim_game(self, token: str, points: int):
        url = 'https://api-web.tomarket.ai/tomarket-game/v1/game/claim'
        try:
            self.headers.update({
                'Authorization': token
            })
            payload = {
                'game_id': '59bcd12e-04e2-404c-a172-311a0084587d',
                'points': points
            }
            response = await asyncio.to_thread(requests.post, url=url, headers=self.headers, json=payload)
            data = self.response_data(response)
            if data is not None:
                if data['status'] == 0:
                    log_message(f"Game Claimed {data['data']['points']}", color=Fore.GREEN + Style.BRIGHT)
                elif data['status'] == 500:
                    log_message("Game Not Start", color=Fore.YELLOW + Style.BRIGHT)
                    await self.play_game(token=token, point=points)
                else:
                    log_message(f"{data['message']}", color=Fore.RED + Style.BRIGHT)
            else:
                log_message('Data play game is None')
        except (Exception) as e:
            return log_message(f"{e}", color=Fore.RED + Style.BRIGHT)

    async def claim_daily(self, token: str):
        url = 'https://api-web.tomarket.ai/tomarket-game/v1/daily/claim'
        
        self.headers.update({
                'Authorization': token
        })
        payload = {
                'game_id': 'fa873d13-d831-4d6f-8aee-9cff7a1d0db1'
        }
        while True:
            response = await asyncio.to_thread(requests.post, url=url, headers=self.headers, json=payload)
            data = self.response_data(response)
            if data is not None:
                if data['status'] == 0:
                    log_message(
                        f"Daily Claim | Day {data['data']['today_game']} | Points {data['data']['today_points']}",
                        color=Fore.GREEN + Style.BRIGHT
                    )
                elif data['status'] == 400:
                    log_message(
                        f"Already Check Daily Claim | Day {data['data']['today_game']} | Points {data['data']['today_points']}",
                        color=Fore.MAGENTA + Style.BRIGHT
                    )
                else:
                    log_message(f"{data['message']}", color=Fore.RED + Style.BRIGHT)
            else:
                log_message('data claim daily not found')
            await asyncio.sleep(2)            

    async def start_farm(self, token: str):
        url = 'https://api-web.tomarket.ai/tomarket-game/v1/farm/start'
        try:
            self.headers.update({
                'Authorization': token
            })
            payload = {
                'game_id': '53b22103-c7ff-413d-bc63-20f6fb806a07'
            }
            while True:
                response = await asyncio.to_thread(requests.post, url=url, headers=self.headers, json=payload)
                data = self.response_data(response)
                if data is not None:
                    end_time = datetime.fromtimestamp(data['data']['end_at'])
                    now = datetime.now()
                    remaining_time = end_time - now
                    if data['status'] == 0:
                        log_message("Start Farm", color=Fore.GREEN + Style.BRIGHT)
                        if remaining_time.total_seconds() > 0:
                            hours, remainder = divmod(remaining_time.total_seconds(), 3600)
                            minutes, seconds = divmod(remainder, 60)
                            log_message(f"Please Wait {int(hours)} Hours {int(minutes)} Minutes {int(seconds)} Seconds To Claim Farm", color=Fore.YELLOW + Style.BRIGHT)
                            break
                        else:
                            await self.claim_farm(token=token)
                            break
                    elif data['status'] == 500:
                        log_message("Farm Already Started", color=Fore.MAGENTA + Style.BRIGHT)
                        if remaining_time.total_seconds() > 0:
                            hours, remainder = divmod(remaining_time.total_seconds(), 3600)
                            minutes, seconds = divmod(remainder, 60)
                            log_message(f"Please Wait {int(hours)} Hours {int(minutes)} Minutes {int(seconds)} Seconds To Claim Farm", color=Fore.YELLOW + Style.BRIGHT)
                            break
                        else:
                            await self.claim_farm(token=token)
                            break
                    else:
                        log_message(f"{data['message']}", color=Fore.RED + Style.BRIGHT)
                else:
                    log_message('data start farm not found')
                await asyncio.sleep(2)
        except (Exception) as e:
            return log_message(f"{e}", color=Fore.RED + Style.BRIGHT)

    async def claim_farm(self, token: str):
        url = 'https://api-web.tomarket.ai/tomarket-game/v1/farm/claim'
        try:
            self.headers.update({
                'Authorization': token
            })
            payload = {
                'game_id': '53b22103-c7ff-413d-bc63-20f6fb806a07'
            }
            while True:
                response = await asyncio.to_thread(requests.post, url=url, headers=self.headers, json=payload)
                data = self.response_data(response)
                if data is not None:
                    if data['status'] == 0:
                        log_message(f"Claimed {data['data']['points']} From Farm", color=Fore.GREEN + Style.BRIGHT)
                        await self.start_farm(token=token)
                        break
                    else:
                        log_message(f"{data['message']}", color=Fore.RED + Style.BRIGHT)
                else:
                    log_message('data claim not found')
                await asyncio.sleep(2)
        except (Exception) as e:
            return log_message(f"{e}", color=Fore.RED + Style.BRIGHT)

    async def list_tasks(self, token: str, query: str):
        url = 'https://api-web.tomarket.ai/tomarket-game/v1/tasks/list'
        try:
            payload = {
                'language_code': 'en'
            }
            data = json.dumps(payload)
            self.headers.update({
            'Authorization': token,
            # 'Content-Length': str(len(data)),
            # 'Content-Type': 'application/json'
                })
            response = requests.post(url=url, headers=self.headers, json=payload)
            response.raise_for_status()
            response_json = response.json()
            data = response_json.get('data')
            standard = data.get('standard', [])
            expire = data.get('expire', [])
            default = data.get('default', [])
            free_tomato = data.get('free_tomato',[])
            thirds = data.get('3rd',{})
            default = thirds.get('default',[])
            # invite_star_group = data.get('invite_star_group',[])
            invite_star_group = []
            for task in default:
                if task['status'] == 0 and task['type'] == "mysterious":
                    current_time = datetime.now()
                    date_part = current_time.strftime("%Y-%m-%d")
                    split_time  = task.get('startTime')
                    end_time = split_time.split(" ")[0]
                    if date_part == end_time:
                        log_message(f"Claiming {task['title']}", color=Fore.YELLOW + Style.BRIGHT)
                        await self.claim_tasks(token=token, task_id=task['taskId'])
                        await asyncio.sleep(2)
            
            for task in free_tomato:
                await self.clear_task(query, token, task)

            for task in invite_star_group:
                await self.clear_task(query, token, task)

            for task in standard:
                await self.clear_task(query, token, task)
            
            for task in expire:
                await self.clear_task(query, token, task)
            
            for task in default:
                await self.clear_task(query, token, task)

        except (Exception) as e:
            return log_message(f"{e}", color=Fore.RED + Style.BRIGHT)

    async def clear_task(self, query, token, task):
        if task['status'] == 1:
            log_message(f"You Haven't Finish Or Start This {task['title']} Task", color=Fore.YELLOW + Style.BRIGHT)
            trys = 9
            while True:
                if trys <= 0:
                    break
                await asyncio.sleep(5)
                data = await self.check_tasks(token=token, task_id=task['taskId'], init_data=query)
                if data['data']['status'] == 2:
                    await self.claim_tasks(token=token, task_id=task['taskId'])
                    break
                trys -= 1

        elif task['status'] == 2:
            log_message(f"Claiming {task['title']}", color=Fore.YELLOW + Style.BRIGHT)
            await self.claim_tasks(token=token, task_id=task['taskId'])
            await asyncio.sleep(2)

        elif task['status'] == 0:
            log_message(f"Starting {task['title']}", color=Fore.YELLOW + Style.BRIGHT)
            await self.start_tasks(query=query, token=token, task_id=task['taskId'])
            await asyncio.sleep(5)
            log_message(f"You Haven't Finish Or Start This {task['title']} Task", color=Fore.YELLOW + Style.BRIGHT)
            trys = 9
            while True:
                if trys <= 0:
                    break
                await asyncio.sleep(3)
                data = await self.check_tasks(token=token, task_id=task['taskId'],init_data=query)
                if data['data']['status'] == 2:
                    await self.claim_tasks(token=token, task_id=task['taskId'])
                    break
                trys -= 1

    async def start_tasks(self,query: str, token: str, task_id: int):
        url = 'https://api-web.tomarket.ai/tomarket-game/v1/tasks/start'
        try:
            
            payload = {
                'task_id': task_id,
            }
            data = json.dumps(payload)
            self.headers.update({
            'Authorization': token,
                })
            response = requests.post(url=url, headers=self.headers, json=payload)
            response.raise_for_status()
            return response.json()
        except (Exception) as e:
            return log_message(f"{e}", color=Fore.RED + Style.BRIGHT)

    async def check_tasks(self, token: str, task_id: int, init_data):
        url = 'https://api-web.tomarket.ai/tomarket-game/v1/tasks/check'
        
        payload = {
                'task_id': task_id,
                'init_data': init_data
        }
        data = json.dumps(payload)
        self.headers.update({
            'Authorization': token,
                })
        response = requests.post(url=url, headers=self.headers, json=payload)
        data = self.response_data(response)
        return data
            

    async def claim_tasks(self, token: str, task_id: int):
        url = 'https://api-web.tomarket.ai/tomarket-game/v1/tasks/claim'
        
        self.headers.update({
            'Authorization': token
        })
        payload = {
           'task_id': task_id
        }
        response = requests.post(url=url, headers=self.headers, json=payload)
        response.raise_for_status()
        data = response.json()
        if data['status'] == 0:
            log_message("Claimed", color=Fore.GREEN + Style.BRIGHT)
        elif data['status'] == 500:
            log_message("You Haven't Finish Or Start This Task", color=Fore.YELLOW + Style.BRIGHT)
        elif data['status'] == 401:
            log_message("Invalid Task", color=Fore.RED + Style.BRIGHT)
        else:
            log_message(f"{data['message']}", color=Fore.RED + Style.BRIGHT)
    
    async def validate(self, token):
        url = 'https://api-web.tomarket.ai/tomarket-game/v1/rank/evaluate'
        self.headers.update({
            'Authorization': token
        })
        response = requests.post(url=url, headers=self.headers)
        data = self.response_data(response)
        return data
        

    async def create(self, token):
        url = 'https://api-web.tomarket.ai/tomarket-game/v1/rank/create'
        self.headers.update({
            'Authorization': token
        })
        response = requests.post(url=url, headers=self.headers)
        data = self.response_data(response)
        return data

    async def upgrade_rank(self, token, payload):
        url = 'https://api-web.tomarket.ai/tomarket-game/v1/rank/upgrade'
        self.headers.update({
            'Authorization': token
        })
        response = requests.post(url=url, headers=self.headers, json=payload)
        data = self.response_data(response)
        return data

    async def share_tg(self, token):
        url = 'https://api-web.tomarket.ai/tomarket-game/v1/rank/sharetg'
        self.headers.update({
            'Authorization': token
        })
        response = requests.post(url=url, headers=self.headers)
        data = self.response_data(response)
        return data

    async def raffle(self, token, payload):
        url = 'https://api-web.tomarket.ai/tomarket-game/v1/spin/raffle'
        self.headers.update({
            'Authorization': token
        })
        response = requests.post(url=url, headers=self.headers,json=payload)
        data = self.response_data(response)
        return data

    async def rank_data(self, token, selector):
        url = 'https://api-web.tomarket.ai/tomarket-game/v1/rank/data'
        self.headers.update({
            'Authorization': token
        })
        response = await asyncio.to_thread(requests.post, url=url, headers=self.headers)
        data = self.response_data(response)
        if data is not None:
            if data.get('status',400) == 0:
                dat = data.get('data',{})
                isCreated = dat.get('isCreated')
                if isCreated:
                    currentRank = dat.get('currentRank')
                    nextRank = dat.get('nextRank')
                    unusedStars = dat.get('unusedStars')
                    log_message(f"Rank : {currentRank.get('name')} | Level : {currentRank.get('level')} | Stars: {unusedStars}")
                    minStar = nextRank.get('minStar',0)
                    range = nextRank.get('range', 0)
                    if selector == '1':
                        if unusedStars >= range:
                            log_message("Upgraded Rank...")
                            await asyncio.sleep(2)
                            payload = {'stars': unusedStars}
                            upgrade_data = await self.upgrade_rank(token=token, payload=payload)
                            if upgrade_data is not None:
                                data = upgrade_data.get('data',{})
                                currentRank = data.get('currentRank')
                                await asyncio.sleep(1)
                                data_share_tg = await self.share_tg(token=token)
                                if data_share_tg is not None:
                                    log_message(f"Upgrade to rank {currentRank.get('name')} Done")
                        else:
                            log_message(f"Need {range-unusedStars} stars to upgrade rank {nextRank.get('name', 'none')}")
                            
                    elif selector == '2':
                        if unusedStars > 0:
                            log_message("Playing raffle...")
                            payload = {'category': "tomarket"}
                            data_raffle = await self.raffle(token=token, payload=payload)
                            if data_raffle is not None:
                                status = data_raffle.get('status', 0)
                                if status == 0:
                                    data = data_raffle.get('data',{})
                                    result = data.get('results',[])
                                    for res in result:
                                        log_message(f"Raffle Done, Reward {res.get('amount',0)} {res.get('type')}")
                                else:
                                    log_message("error")
                        else:
                            log_message("No stars to play raffle")
                else:
                    await asyncio.sleep(2)
                    data_validate = await self.validate(token)
                    if data_validate is not None:
                        if data_validate.get('status',400) == 0:
                            log_message("Validate Rank...")
                            await asyncio.sleep(2)
                            data_create = await self.create(token)
                            if data_create is not None:
                                if data_create.get('status',400) == 0:
                                    dats = data_create.get('data')
                                    curRank = dats.get('currentRank')
                                    log_message(f"Rank : {curRank.get('name')} | Level : {curRank.get('level')}")

            else:
                log_message(data.get('message','Data Rank Not Found'))

    async def free_spin(self, token, query):
        url = 'https://api-web.tomarket.ai/tomarket-game/v1/user/tickets'
        payload = {"language_code":"en","init_data":query}
        self.headers.update({
            'Authorization': token
        })
        response = await asyncio.to_thread(requests.post, url=url, headers=self.headers, json=payload)
        data = self.response_data(response)
        if data is not None:
            payloads = {"category":"ticket_spin_1"}
            status = data.get('status')
            if status == 0:
                dats = data.get('data')
                ticket_spin_1 = dats.get('ticket_spin_1',0)
                while True:
                    if ticket_spin_1 > 0:
                        log_message("Open Free Raffle")
                        await asyncio.sleep(2)
                        data_raffle = await self.raffle(token=token, payload=payloads)
                        if data_raffle is not None:
                            status = data_raffle.get('status', 0)
                            if status == 0:
                                ticket_spin_1 -= 1
                                data = data_raffle.get('data',{})
                                result = data.get('results',[])
                                for res in result:
                                    log_message(f"Raffle Done, Reward {res.get('amount',0)} {res.get('type')}")
                            else:
                                log_message("error")
                    else:
                        break

        return data

    async def get_combo_puzzle(self):
        url = 'https://raw.githubusercontent.com/boytegar/TomarketBOT/refs/heads/master/combo.json'
        response = requests.get(url)
        data = self.response_data(response)
        return data

    async def puzzle_task(self, token, query):
        url = 'https://api-web.tomarket.ai/tomarket-game/v1/tasks/puzzle'
        self.headers.update({
            'Authorization': token
        })
        payload = {"language_code":"en","init_data": query}
        response = await asyncio.to_thread(requests.post, url=url, headers=self.headers, json=payload)
        data = self.response_data(response)
        if data is not None:
            status = data.get('status')
            if status == 0:
                list_data = data.get('data')
                for dats in list_data:
                    taskId = dats.get('taskId')
                    statuss = dats.get('status')
                    star = dats.get('star')
                    games = dats.get('games')
                    score = dats.get('score')
                    if statuss == 0:
                        list_combo = await self.get_combo_puzzle()
                        combo = self.find_by_id(list_combo, str(taskId))
                        if combo is not None:
                            payload = {'task_id': taskId, 'code': combo}
                            data_puzzle_claim = await self.puzzle_claim(token, payload)
                            if data_puzzle_claim.status_code == 200:
                                jsons = data_puzzle_claim.json()
                                data = jsons.get('data',{})

                                if len(data) == 0:
                                    log_message(f"Puzzle Done, Reward : {star} Star, {games} Tiket Games, {score} Tomato")
                                else:
                                    message = data.get('message','')
                                    log_message(message)

    async def puzzle_claim(self, token, payload):
        url = 'https://api-web.tomarket.ai/tomarket-game/v1/tasks/puzzleClaim'
        self.headers.update({
            'Authorization': token
        })
        response = await asyncio.to_thread(requests.post, url=url, headers=self.headers, json=payload)
        return response

    def response_data(self, response):
        if response.status_code >= 500:
            log_message(f"Error {response.status_code}")
            return None
        elif response.status_code >= 400:
            log_message(f"Error {response.status_code} : msg {response.text}")
            return None
        elif response.status_code >= 200:
            return response.json()
        else:
            return None
        
    def find_by_id(self, json_data, id):
        for key, value in json_data.items():
            if key == id:
                return value
        return None

