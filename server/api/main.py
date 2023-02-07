"""Graphql endpoint main module."""
from api.bootstrap import bootstrap_di
from api.context import Context
from api.schema import SchemaHelper
from fastapi import FastAPI
from kink import di
from sqlalchemy.orm import Session
from strawberry.fastapi import GraphQLRouter


async def get_context() -> Context:
    return Context()  # type: ignore

graphql_app = GraphQLRouter(
    SchemaHelper.get_schema(),
    context_getter=get_context)

app = FastAPI()
app.include_router(graphql_app, prefix="/graphql")


@app.get("/")
async def root():
    return {"message": "Hello GraphQL!"}

if __name__ == "__main__":
    bootstrap_di()
    import uvicorn
    try:
        uvicorn.run(app, host="0.0.0.0", port=8000)
    finally:
        di[Session].close()
