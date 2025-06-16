import sqlite3
import datetime
from contextlib import contextmanager
from typing import Optional, Tuple, List


class DatabaseManager:
    def __init__(self, db_path: str = "Profile.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self) -> None:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    net_total INTEGER DEFAULT 0,
                    max_gambled INTEGER DEFAULT 0,
                    gamble_wins INTEGER DEFAULT 0,
                    gamble_losses INTEGER DEFAULT 0,
                    gamble_wins_streak INTEGER DEFAULT 0,
                    gamble_losses_streak INTEGER DEFAULT 0
                )
            """
            )
            conn.commit()

    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
        finally:
            conn.close()

    def register_user(self, user_id: int) -> bool:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE user_id = ?", (str(user_id),))

            if cursor.fetchone() is None:
                cursor.execute(
                    """
                    INSERT INTO users (user_id, net_total, max_gambled, gamble_wins, gamble_losses)
                    VALUES (?, ?, ?, ?, ?)
                """,
                    (str(user_id), 0, 0, 0, 0),
                )
                conn.commit()
                return True
            return False

    def get_user_details(self, user_id: int) -> Optional[Tuple]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE user_id = ?", (str(user_id),))
            return cursor.fetchone()

    def update_user_net_total(self, user_id: int, amount: int) -> None:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET net_total = net_total + ? WHERE user_id = ?",
                (amount, str(user_id)),
            )
            conn.commit()

    def get_leaderboard_by_net_total(self, limit: int = 10) -> List[Tuple]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM users ORDER BY net_total DESC LIMIT ?", (limit,)
            )
            return cursor.fetchall()

    def get_leaderboard_by_gambles(self, limit: int = 10) -> List[Tuple]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT *, (gamble_wins + gamble_losses) as total_gambles 
                FROM users 
                ORDER BY total_gambles DESC 
                LIMIT ?
            """,
                (limit,),
            )
            return cursor.fetchall()

    def update_gamble_stats(self, user_id: int, won: bool, amount: int) -> None:
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                "SELECT gamble_wins_streak, gamble_losses_streak, max_gambled FROM users WHERE user_id = ?",
                (str(user_id),),
            )
            result = cursor.fetchone()

            if result:
                wins_streak, losses_streak, max_gambled = result

                if won:
                    cursor.execute(
                        "UPDATE users SET gamble_wins = gamble_wins + 1, gamble_wins_streak = ?, gamble_losses_streak = 0 WHERE user_id = ?",
                        (wins_streak + 1, str(user_id)),
                    )
                else:
                    cursor.execute(
                        "UPDATE users SET gamble_losses = gamble_losses + 1, gamble_losses_streak = ?, gamble_wins_streak = 0 WHERE user_id = ?",
                        (losses_streak + 1, str(user_id)),
                    )

                if amount > max_gambled:
                    cursor.execute(
                        "UPDATE users SET max_gambled = ? WHERE user_id = ?",
                        (amount, str(user_id)),
                    )

                conn.commit()

    def get_user_position_in_leaderboard(
        self, user_id: int, order_by: str = "net_total"
    ) -> int:
        with self.get_connection() as conn:
            cursor = conn.cursor()

            if order_by == "gambles":
                cursor.execute(
                    """
                    SELECT COUNT(*) + 1 as position
                    FROM users u1, users u2
                    WHERE u1.user_id = ? AND (u2.gamble_wins + u2.gamble_losses) > (u1.gamble_wins + u1.gamble_losses)
                """,
                    (str(user_id),),
                )
            else:
                cursor.execute(
                    """
                    SELECT COUNT(*) + 1 as position
                    FROM users u1, users u2
                    WHERE u1.user_id = ? AND u2.net_total > u1.net_total
                """,
                    (str(user_id),),
                )

            result = cursor.fetchone()
            return result[0] if result else 0


database = DatabaseManager()
