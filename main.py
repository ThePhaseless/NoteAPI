from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import Cookie, FastAPI, Response, WebSocket, responses

from models import (
    Game,
    HealthyResponse,
    NoGameFoundError,
    NoPlayerFoundError,
    Player,
    PlayerChoice,
)

app = FastAPI(servers=[{"url": "http://localhost:8000"},
              {"url": "https://api.nerine.dev"}])

players: dict[Player] = []
games: dict[Game] = []

max_players = 2


@app.get(
    "/",
    response_class=responses.RedirectResponse,
    response_description="Redirects to /docs",
)
async def docs_redirect() -> responses.RedirectResponse:
    return responses.RedirectResponse(url="/docs")


@app.get("/healtcheck")
def root() -> HealthyResponse:
    return HealthyResponse()


@app.post("/player")
async def create_player(name: str = "Anonymous") -> Player:
    new_player = Player(name=name)
    players[new_player] = new_player
    return new_player


@app.post("/game")
async def create_game(user: Annotated[str, Cookie()]) -> Game:
    new_game = Game(creator=user)
    games[new_game] = new_game
    return new_game


@app.get("/games")
async def get_games() -> list[Game]:
    return games


@app.get("/game/{game_id}", responses={404: {"description": "Game not found"}})
async def get_game(response: Response, game_id: UUID) -> Game:
    try:
        game = next(game for game in games if game.id == game_id)
    except StopIteration as e:
        response.status_code = 404
        raise NoGameFoundError from e

    return game


@app.get("/player/{player_name}", responses={404: {"description": "Player not found"}})
async def get_player(player_name: str, response: Response) -> Player:
    try:
        player = next(
            player for player in players if player.name == player_name
        )
    except StopIteration as e:
        response.status_code = 404
        raise NoPlayerFoundError from e

    return player


@app.get("/player/{player_name}/games")
async def get_player_games(player_name: str) -> list[Game]:
    return [game for game in games if game.creator == player_name]


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        self.active_connections.append(websocket)
        await websocket.accept()

    def disconnect(self, websocket: WebSocket, reason: str) -> None:
        self.active_connections.remove(websocket)
        websocket.close(reason=reason)

    async def send_personal_message(self, message: dict, websocket: WebSocket) -> None:
        await websocket.send_json(message)

    async def broadcast(self, message: dict) -> None:
        for connection in self.active_connections:
            await connection.send_json(message)


manager = ConnectionManager()


@app.websocket("/game/{game_id}/ws")
async def game_ws(
    websocket: WebSocket,
    game_id: UUID,
    player_name: str,
) -> None:
    await websocket.accept()
    try:
        player: Player = await get_player(player_name)
    except NoPlayerFoundError:
        await websocket.close(reason="Player not found")
        return

    try:
        game: Game = await get_game(game_id)
    except NoGameFoundError:
        await websocket.close(reason="Game not found")
        return

    if game.end_time is not None:
        await websocket.close(reason="Game already ended")
        return
    if len(game.players) >= max_players:
        await websocket.close(reason="Lobby full")
        return

    await manager.connect(websocket)
    data = await websocket.receive_json()
    while True:
        match data["action"]:
            case "join":
                await join_game(game_id, player, game)
                break
            case "leave":
                await leave_game(websocket, player, game)
                break
            case "play":
                await play_game(websocket, player, game, data["choice"])
                break


async def join_game(game_id: UUID, player: Player, game: Game) -> None:
    if player.current_game_id is None:
        player.current_game_id = game_id
        game.players.append(player)
        await manager.broadcast(
            message={
                "action": "joined",
                "player_name": player.name,
            },
        )
    else:
        await manager.send_personal_message(message={
            "action": "resumed",
        })


async def leave_game(websocket: WebSocket, player: Player, game: Game) -> None:
    player.current_game_id = None
    game.players.remove(player)
    await manager.broadcast(websocket, message={
        "action": "left",
        "player_name": player.name,
    })
    await manager.disconnect(websocket)


async def play_game(
        websocket: WebSocket, player: Player, game: Game, choice: PlayerChoice,
) -> None:
    if player.current_game_id != game.id:
        await manager.disconnect(websocket, reason="Wrong game")
        return

    game.players[player] = choice

    await manager.send_personal_message(message={
        "action": "played",
        "player_name": player.name,
        "choice": choice,
    }, websocket=websocket)

    should_game_end = False
    if len(game.players) == max_players:
        should_game_end = True

    if should_game_end:
        game.end_time = datetime.now()
        await manager.broadcast(websocket, message={
            "action": "ended",
            "choices": game.players,
        })
        await manager.disconnect(websocket, reason="Game ended")
