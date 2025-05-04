import asyncio
import websockets
import json
from telegram import Bot
from config import TELEGRAM_TOKEN, CHAT_ID

bot = Bot(token= TELEGRAM_TOKEN )

def format_price(ton_value):
    return f"{ton_value / 1e9:.2f}"

async def listen_fragment():
    uri = "wss://fragment.com/api/ws"
    async with websockets.connect(uri) as websocket:
        await websocket.send(json.dumps({
            "op": "sub",
            "channel": "lots"
        }))

        async for message in websocket:
            data = json.loads(message)

            if data.get("type") == "lots_update":
                for lot in data["data"]:
                    name = lot.get("name")
                    price = lot.get("price")
                    if name and price:
                        msg = (
                            f"<b>Новая ставка</b>\n"
                            f"Юзернейм: <a href='https://fragment.com/username/@{name}'>@{name}</a>\n"
                            f"Ставка: <b>{format_price(price)} TON</b>"
                        )
                        await bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode="HTML")

            elif data.get("type") == "lot_closed":
                lot = data.get("data", {})
                name = lot.get("name")
                winner = lot.get("winner")
                final_price = lot.get("price")
                if name and winner and final_price:
                    msg = (
                        f"<b>Аукцион завершён!</b>\n"
                        f"Юзернейм: <a href='https://fragment.com/username/@{name}'>@{name}</a>\n"
                        f"Победитель: <code>{winner}</code>\n"
                        f"Финальная цена: <b>{format_price(final_price)} TON</b>"
                    )
                    await bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode="HTML")

if __name__ == "__main__":
    asyncio.run(listen_fragment())
