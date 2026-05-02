import asyncio
from db.pool import get_pool


async def test_db():
    pool = await get_pool()
    async with pool.acquire() as conn:

        # 1️⃣ вставка
        row = await conn.fetchrow(
            """
            INSERT INTO work_sessions (ticket_id, user_id, started_at)
            VALUES (5, 'f5f5d7b6-c390-42e9-b1b7-eea970145ee0', NOW())
            RETURNING *
            """
        )

        print(">>> INSERT RESULT:", row)

        # 2️⃣ проверка
        all_rows = await conn.fetch("SELECT * FROM work_sessions")
        print(">>> ALL ROWS:", all_rows)


asyncio.run(test_db())