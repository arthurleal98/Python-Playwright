import os
import pyodbc
from typing import Any, Dict, List, Optional, Sequence
from contextlib import contextmanager
from dotenv import load_dotenv

# Carrega variáveis do .env
load_dotenv()

class DatabaseClient:
    """Helper para executar queries no SQL Server usando pyodbc."""

    def __init__(self , db_driver, db_server, db_database, db_username, db_password) -> None:
        self.driver = os.getenv(db_driver)
        self.server = os.getenv(db_server)
        self.database = os.getenv(db_database)
        self.username = os.getenv(db_username)
        self.password = os.getenv(db_password)
        self.trust_server_cert = os.getenv("DB_TRUST_SERVER_CERT", "yes").lower() in ("1", "true", "yes")
        self.trusted_connection = os.getenv("DB_TRUSTED_CONNECTION", "false").lower() in ("1", "true", "yes")
        self.timeout = int(os.getenv("DB_CONNECT_TIMEOUT", "30"))

        # Validações
        if not all([self.server, self.database]):
            raise ValueError("Variáveis de ambiente DB_SERVER e DB_DATABASE são obrigatórias.")

    def _connection_string(self) -> str:
        """Monta a connection string dinâmica a partir das variáveis do .env."""
        driver = self.driver
        if not driver.startswith("{"):
            driver = f"{{{driver}}}"

        parts = [
            f"DRIVER={driver}",
            f"SERVER={self.server}",
            f"DATABASE={self.database}",
            "Encrypt=yes",
            f"TrustServerCertificate={'yes' if self.trust_server_cert else 'no'}"
        ]

        if self.trusted_connection:
            parts.append("Trusted_Connection=yes")
        else:
            parts.append(f"UID={self.username}")
            parts.append(f"PWD={self.password}")

        return ";".join(parts)

    @contextmanager
    def connection(self):
        """Contexto de conexão segura."""
        conn = pyodbc.connect(self._connection_string(), timeout=self.timeout)
        try:
            yield conn
        finally:
            conn.close()

    # ========================
    # Métodos de execução
    # ========================

    def fetch_all(self, query: str, params: Optional[Sequence[Any]] = None) -> List[Dict[str, Any]]:
        """Executa SELECT e retorna todas as linhas como lista de dicionários."""
        with self.connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params or [])
            if not cursor.description:
                return []
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def fetch_one(self, query: str, params: Optional[Sequence[Any]] = None) -> Optional[Dict[str, Any]]:
        """Executa SELECT e retorna apenas a primeira linha."""
        with self.connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params or [])
            row = cursor.fetchone()
            if not row:
                return None
            columns = [col[0] for col in cursor.description]
            return dict(zip(columns, row))

    def execute(self, query: str, params: Optional[Sequence[Any]] = None) -> int:
        """Executa INSERT/UPDATE/DELETE, retorna número de linhas afetadas."""
        with self.connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params or [])
            conn.commit()
            return cursor.rowcount

    def execute_many(self, query: str, param_list: Sequence[Sequence[Any]]) -> int:
        """Executa vários INSERT/UPDATE/DELETE em lote."""
        with self.connection() as conn:
            cursor = conn.cursor()
            cursor.fast_executemany = True
            cursor.executemany(query, param_list)
            conn.commit()
            return cursor.rowcount


    def buscar_primeiro_container_valido(batch_size: int = 20):
        

        # --- First database connection (generic names) ---
        db_ecargo = DatabaseClient(
            db_driver='DB1_DRIVER',
            db_server="DB1_SERVER",
            db_database="DB1_DATABASE",
            db_username="DB1_USERNAME",
            db_password="DB1_PASSWORD"
        )

        # --- Second database connection (generic names) ---
        db_multi = DatabaseClient(
            db_driver='DB2_DRIVER',
            db_server="DB2_SERVER",
            db_database="DB2_DATABASE",
            db_username="DB2_USERNAME",
            db_password="DB2_PASSWORD"
        )

        # --- Total de linhas na tabela container ---
        result = db_ecargo.fetch_all("""
            SELECT SUM(row_count) AS total_linhas
            FROM sys.dm_db_partition_stats
            WHERE object_id = OBJECT_ID('container')
            AND (index_id = 0 OR index_id = 1);
        """)
        max_count = result[0]['total_linhas']
        print(f"📊 Total de linhas na tabela container: {max_count}")

        # --- Loop paginado ---
        count = 0
        while count < max_count:
            query = f"""
                SELECT num_container
                FROM container
                WHERE tab_tipo_container_id = 55
                AND num_container IS NOT NULL
                AND LTRIM(RTRIM(num_container)) <> ''
                AND CHARINDEX(CHAR(9), num_container) = 0
                AND num_container NOT LIKE '% %'
                AND num_container LIKE '[A-Z][A-Z][A-Z][A-Z][0-9][0-9][0-9][0-9][0-9][0-9][0-9]'
                ORDER BY num_container
                OFFSET {count} ROWS
                FETCH NEXT {batch_size} ROWS ONLY;
            """
            rows = db_ecargo.fetch_all(query)

            if not rows:
                break

            for row in rows:
                if not db_multi.fetch_all(f"select ctr_descricao from t_container where ctr_descricao = '{row['num_container']}'"):

                    return row['num_container']

            count += batch_size

        return None


if __name__ == "__main__":
    container = DatabaseClient.buscar_primeiro_container_valido(batch_size=50)
    if container:
        print(f"🚢 Primeiro container válido encontrado: {container}")
    else:
        print("⚠️ Nenhum container válido encontrado na tabela.")
