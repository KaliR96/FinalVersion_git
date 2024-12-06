from database import execute_query, fetch_all
from datetime import datetime


async def track_event(user_id, username, state, is_new):
    # Сохраняем событие в базе данных
    query = """
    INSERT INTO user_analytics (user_id, username, state, is_new, event_time)
    VALUES (%s, %s, %s, %s, %s);
    """
    await execute_query(query, (user_id, username, state, is_new, datetime.now()))

async def get_summary_by_period(period: str):
    # Получаем сводку по состояниям за указанный период
    query = f"""
    SELECT state, COUNT(*) AS count
    FROM user_analytics
    WHERE event_time > NOW() - INTERVAL '{period}'
    GROUP BY state
    ORDER BY count DESC;
    """
    return await fetch_all(query)

async def get_user_retention():
    # Получаем сводку по возвращающимся пользователям
    query = """
    SELECT user_id, COUNT(*) AS visits, MAX(event_time) - MIN(event_time) AS duration
    FROM user_analytics
    GROUP BY user_id
    HAVING visits > 1;
    """
    return await fetch_all(query)

async def check_user_in_database(user_id):
    query = "SELECT EXISTS(SELECT 1 FROM user_analytics WHERE user_id = ?);"
    result = await execute_query(query, (user_id,))
    return result[0][0] == 1

