from uuid import UUID

from fastapi import FastAPI, responses

from models import Game, HealthyResponse, Player

app = FastAPI()

players: list[Player] = []
games: list[Game] = []


@app.get("/", response_class=responses.RedirectResponse, response_description="Redirects to /docs")
async def docs_redirect():
    return responses.RedirectResponse(url="/docs")


@app.get("/healtcheck")
def root() -> HealthyResponse:
    return HealthyResponse()


@app.post("/player")
async def create_player(name: str = "Anonymous") -> Player:
    new_player = Player(name=name)
    players.append(new_player)
    return new_player


@app.post("/game")
async def create_game(user_id: int) -> Game:
    new_game = Game(creator_id=user_id)
    games.append(new_game)
    return new_game


@app.get("/game/{game_id}")
async def get_game(game_id: UUID) -> Game:
    return next((game for game in games if game.id == game_id), None)


@app.get("/player/{player_id}")
async def get_player(player_id: UUID) -> Player:
    return next((player for player in players if player.id == player_id), None)


@app.get("/player/{player_id}/games")
async def get_player_games(player_id: UUID) -> list[Game]:
    return [game for game in games if game.creator_id == player_id]
