import asyncio
from quart import Quart



app = Quart(__name__)

name = "test"
counter = 0

class Metrics:
    counter = 0
    duration = 0
metrics = Metrics()

@app.get("/add")
async def handler_add(n = 1):
    counter += n
    return counter

@app.get("/remove")
async def handler_remove(n = 1):
    counter -= n
    return counter

@app.get("/name")
async def handler_name():
    return name

@app.get("/ping")
async def handler_ping():
    return "pong"

@app.get("/slow_ping")
async def handler_slow_ping():
    await asyncio.sleep(2)
    
    return "pong"

@app.get("/metrics")
async def handler_metrics():    
    return """
    metric1{key1=1, key2=3}\n
    metric2{key1=100, key2=300}
    """

if __name__ == "__main__":
    app.run("0.0.0.0", 8080, debug=True)