# Coin Farm
Project implemented by Python backend framework FastAPI.

## Getting Started
1. Install dependencies
```zsh
pip install -r requirements.txt
```
2. Start FastAPI process
```zsh
uvicorn app.main:app --reload
```
3. Open local API docs [http://localhost:8000/docs](http://localhost:8000/docs)
4. For further use, try to connect the ngrok software for accepting and sending request throw the https.

## Description
1. Condition format for __miners.miner__ table:

``````

## Description of the project mechanics 
1. There are 3 main parameters in this game:
	**Price**
	**Points per hour**
	**Followers**
**Price** provides information about the cost of purchase for specific item in the game, as well as price for its upgrade. **Points per hour** is the metric to measure the income that such item gives. By buying various cards and upgrading them player gain option to unlock new cards or upgrades for current cards, when enough game currency is collected player will be transferred to the next league. There will be 9 leagues in the start of the game: 

**NPC**
**Doomer**
**Meme inside**
**Skuf**
**Punk**
**Alfa**
**Sigma**
**Giga meme**
**G.O.A.T.**

```_Followers will be designed later, for now its not important_```

Formulas for increase in price and points per hour will be provided personally.
