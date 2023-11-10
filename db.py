import asyncpg
from asyncpg.exceptions import UniqueViolationError

def db_connection_required(func):
    async def wrapper(self, *args, **kwargs):
        if self.conn is None or self.conn.is_closed():
            await self.connect()
        result = await func(self, *args, **kwargs)
        await self.disconnect()
        return result
    return wrapper


class Database:
    def __init__(self, db_url, db_port, db_name, db_user, db_password):
        self.db_url = f"postgresql://{db_user}:{db_password}@{db_url}:{db_port}/{db_name}"
        self.conn = None

    async def connect(self):
        self.conn = await asyncpg.connect(self.db_url)

    async def disconnect(self):
        await self.conn.close()

    @db_connection_required
    async def get_balance(self, user_id):
        query = "SELECT balance FROM users WHERE user_id = $1"
        result = await self.conn.fetchval(query, user_id)
        return result

    @db_connection_required
    async def update_balance(self, user_id, number):
        query = "UPDATE users SET balance = balance + $1 WHERE user_id = $2"
        await self.conn.execute(query, number, user_id)

    @db_connection_required
    async def get_access_keys(self, user_id):
        query = "SELECT keys, limits, used, country, name_id FROM access_keys WHERE user_id = $1"
        result = await self.conn.fetch(query, user_id)
        keys_data = [{"keys": row['keys'], "limits": row['limits'], "used": row['used'], "country": row['country'], "name": row["name_id"]} for row in result]
        return keys_data

    @db_connection_required
    async def update_limits(self, user_id, keys, number):
        query = "UPDATE access_keys SET limits = limits + $1 WHERE user_id = $2 AND keys = $3"
        await self.conn.execute(query, number, user_id, keys)

    @db_connection_required
    async def get_promo_code(self, code):
        query = "SELECT tokens, used FROM promo_codes WHERE code = $1"
        result = await self.conn.fetchrow(query, code)
        if result:
            return {"tokens": result['tokens'], "used": result['used']}
        else:
            return None

    @db_connection_required
    async def mark_promo_code_as_used(self, code):
        query = "UPDATE promo_codes SET used = True WHERE code = $1"
        await self.conn.execute(query, code)

    @db_connection_required
    async def add_user(self, user_id, username):
        query = "INSERT INTO users (user_id, username, balance, dateStart) VALUES ($1, $2, 0, current_date)"
        await self.conn.execute(query, user_id, username)


    @db_connection_required
    async def add_access_key(self, user_id, keys, limits, country, name_id):
        query = "INSERT INTO access_keys (user_id, keys, limits, used, country, name_id) VALUES ($1, $2, $3, 0, $4, $5)"
        await self.conn.execute(query, user_id, keys, limits, country, name_id)

    @db_connection_required
    async def delete_access_key(self, keys=None, idx=None):
        if keys:
            query = "DELETE FROM access_keys WHERE keys = $1"
            await self.conn.execute(query, keys)
        elif idx:
            query = "DELETE FROM access_keys WHERE name_id = $1"
            await self.conn.execute(query, idx)
        

    @db_connection_required
    async def delete_user_access_keys(self, user_id):
        query = "DELETE FROM access_keys WHERE user_id = $1"
        await self.conn.execute(query, user_id)

    @db_connection_required
    async def add_promo_code(self, code, tokens):
        query = "INSERT INTO promo_codes (code, tokens, used) VALUES ($1, $2, False)"
        await self.conn.execute(query, code, tokens)

    @db_connection_required
    async def update_used(self, list_keys):
        for keys, used in list_keys.items():
            try:
                query = "UPDATE access_keys SET used = $1 WHERE keys = $2"
                await self.conn.execute(query, used, keys)
            except UniqueViolationError:
                # Обработка ошибки, если такого ключа нет в базе данных
                pass
    
    @db_connection_required
    async def count_rows_by_user_id(self, user_id):
        query = "SELECT COUNT(*) FROM access_keys WHERE user_id = $1"
        result = await self.conn.fetchval(query, user_id)
        return result
