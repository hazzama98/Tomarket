import json
import random
from urllib.parse import parse_qs, unquote
from colorama import Fore, Style, init
import time
import asyncio
from tomarket import Tomarket, print_timestamp, clear_terminal, print_header, loading_animation, log_message, Colors
import sys

def load_credentials():
    try:
        with open('query.txt', 'r') as f:
            queries = [line.strip() for line in f.readlines()]
        return queries
    except FileNotFoundError:
        print("File query.txt tidak ditemukan.")
        return []
    except Exception as e:
        print("Terjadi kesalahan saat memuat token:", str(e))
        return []

def parse_query(query: str):
    parsed_query = parse_qs(query)
    parsed_query = {k: v[0] for k, v in parsed_query.items()}
    user_data = json.loads(unquote(parsed_query['user']))
    parsed_query['user'] = user_data
    return parsed_query

def get(id):
    tokens = json.loads(open("tokens.json").read())
    if str(id) not in tokens.keys():
        return None
    return tokens[str(id)]

def save(id, token):
    tokens = json.loads(open("tokens.json").read())
    tokens[str(id)] = token
    open("tokens.json", "w").write(json.dumps(tokens, indent=4))

async def generate_token():
    tom = Tomarket()
    queries = load_credentials()
    sum = len(queries)
    await clear_terminal()
    await print_header()
    for index, query in enumerate(queries):
        parse = parse_query(query)
        user = parse.get('user')
        log_message(f"Account {index+1}/{sum} {user.get('username','')}", color=Fore.CYAN)
        token = get(user['id'])
        if token == None:
            log_message("Generate token...", color=Fore.YELLOW)
            await loading_animation("Generating token", 2)
            token = await tom.user_login(query)
            save(user.get('id'), token)
            log_message("Generate Token Done!", color=Fore.GREEN, status="success")

async def main():
    init(autoreset=True)
    tom = Tomarket()
    await clear_terminal()
    await print_header()

    # Automatically generate tokens
    await generate_token()

    auto_task = input("Auto clear task (y/n): ").strip().lower()
    auto_game = input("Auto play game (y/n): ").strip().lower()
    auto_combo = input("Auto claim combo puzzle (y/n): ").strip().lower()
    random_number = input("Set random score in game 300-500 (y/n): ").strip().lower()
    free_raffle = input("Enable free raffle (y/n): ").strip().lower()
    used_stars = input("Use star for: 1. Upgrade rank | 2. Auto spin | n. Skip all (1/2/n): ").strip().lower()
    
    while True:
        queries = load_credentials()
        sum = len(queries)
        delay = int(3 * random.randint(3700, 3750))
        start_time = time.time()
        
        await clear_terminal()
        await print_header()
        
        for index, query in enumerate(queries):
            mid_time = time.time()
            total = delay - (mid_time-start_time)
            parse = parse_query(query)
            user = parse.get('user')
            token = get(user['id'])
            if token == None:
                await loading_animation("Logging in", 2)
                token = await tom.user_login(query)
                save(user.get('id'), token)
                await asyncio.sleep(2)
            log_message(f"Account {index+1}/{sum} {user.get('username','')}", color=Fore.CYAN)
            await tom.rank_data(token=token, selector=used_stars)
            await asyncio.sleep(2)
            await tom.claim_daily(token=token)
            await asyncio.sleep(2)
            await tom.start_farm(token=token)
            await asyncio.sleep(2)
            if free_raffle == "y":
                await tom.free_spin(token=token, query=query)
            await asyncio.sleep(2)
        
        if auto_task == 'y':
            for index, query in enumerate(queries):
                mid_time = time.time()
                total = delay - (mid_time-start_time)
                if total <= 0:
                    break
                parse = parse_query(query)
                user = parse.get('user')
                token = get(user['id'])
                if token == None:
                    token = await tom.user_login(query)
                log_message(f"Account {index+1}/{sum} {user.get('username','')}", color=Fore.CYAN)
                if auto_combo == 'y':
                    await tom.puzzle_task(token, query)
                await asyncio.sleep(2)   
                
        if auto_game == 'y':
            for index, query in enumerate(queries):
                mid_time = time.time()
                total = delay - (mid_time-start_time)
                if total <= 0:
                    break
                parse = parse_query(query)
                user = parse.get('user')
                token = get(user['id'])
                if token == None:
                    token = await tom.user_login(query)
                log_message(f"Account {index+1}/{sum} {user.get('username','')}", color=Fore.CYAN)
                await tom.user_balance(token=token, random_number=random_number)
                await asyncio.sleep(2)

        end_time = time.time()
        total = delay - (end_time-start_time)
        hours, remainder = divmod(total, 3600)
        minutes, seconds = divmod(remainder, 60)
        log_message(f"Restarting In {int(hours)} Hours {int(minutes)} Minutes {int(seconds)} Seconds", color=Fore.YELLOW)
        if total > 0:
            await asyncio.sleep(total)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except Exception as e:
        log_message(f"{e}", color=Fore.RED, status="fail")
    except KeyboardInterrupt:
        sys.exit(0)
