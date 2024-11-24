from dataclasses import dataclass
import psycopg
import settings

@dataclass
class Feed:
    title: str
    url: str

async def make_connection():
    conn = psycopg.connect(
        host=settings.POSTGRES_HOST,
        user=settings.POSTGRES_USER,
        password=settings.POSTGRES_PASSWORD,
        dbname=settings.POSTGRES_DB
    )
    return conn

async def get_feeds() -> list[Feed]:
    conn = await make_connection()
    cur = conn.cursor()
    cur.execute("SELECT title, url FROM feeds")
    feeds = cur.fetchall()

    feeds = [Feed(title=feed[0], url=feed[1]) for feed in feeds]

    cur.close()
    conn.close()
    return feeds

async def save_feed(title: str, url: str):
    conn = await make_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO feeds (title, url) VALUES (%s, %s)", (title, url))
    conn.commit()
    cur.close()
    conn.close()
#
async def delete_feed(url: str):
    conn = await make_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM feeds WHERE url = %s", (url,))
    conn.commit()
    cur.close()
    conn.close()
