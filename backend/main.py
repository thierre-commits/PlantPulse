from dotenv import load_dotenv

from database.db_connection import close_connection, get_db_connection


def main() -> None:
    connection = None

    try:
        load_dotenv()
        connection = get_db_connection()
        print("Conexao com PostgreSQL realizada com sucesso.")
    except Exception as error:
        print(f"Erro ao conectar ao PostgreSQL: {error}")
    finally:
        close_connection(connection)


if __name__ == "__main__":
    main()
