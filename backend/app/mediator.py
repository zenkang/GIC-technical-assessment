from sqlalchemy.ext.asyncio import AsyncSession


class Mediator:
    """
    Mediator pattern dispatcher.

    Decouples route handlers from command/query implementations.
    Route handlers call mediator.send(SomeCommand(...)) without
    knowing anything about how the command is executed.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def send(self, command_or_query):
        """Dispatch a command or query to its execute() method."""
        return await command_or_query.execute(self.db)


def get_mediator(db: AsyncSession):
    """FastAPI dependency factory — injected into route handlers via Depends."""
    return Mediator(db)
