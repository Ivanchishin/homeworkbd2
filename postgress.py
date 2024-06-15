import psycopg2


class Database:
    def __init__(self, dbname, user, password):
        self.conn = psycopg2.connect(
            dbname=dbname, user=user, password=password
        )
        self.cur = self.conn.cursor()

    def create_tables(self):
        create_table_query1 = f"""
        CREATE TABLE IF NOT EXISTS clients(
        ID SERIAL PRIMARY KEY,
        NAME VARCHAR(255) not null,
        SURNAME VARCHAR(255) not null,
        EMAIL VARCHAR(255) not null
        );
        """
        self.cur.execute(create_table_query1)
        self.conn.commit()
        create_table_query2 = f"""
                CREATE TABLE IF NOT EXISTS telefons(
                ID SERIAL PRIMARY KEY,
                TELEFON VARCHAR(255) not null,
                CLIENTID INTEGER not null REFERENCES clients(ID));
                """
        self.cur.execute(create_table_query2)
        self.conn.commit()

    def define_client(self, name, surname, email):
        self.cur.execute("SELECT DISTINCT ID FROM clients"
                         " WHERE name = %s and surname = %sand email = %s;",
                         (name, surname, email))
        clientid = self.cur.fetchone()
        return clientid

    def add_client(self, name, surname, email, phone=None):
        addquery1 = """
                INSERT INTO clients(name, surname, email) VALUES(%s, %s, %s);
                """
        addquery2 = """
                INSERT INTO telefons(telefon, clientid) VALUES(%s, %s);
                """
        self.cur.execute(addquery1, (name, surname, email))
        self.conn.commit()
        if phone != None:
            self.cur.execute(addquery2,
                             (phone, self.define_client(name, surname, email)))
            self.conn.commit()

    def add_telefon(self, name, surname, email, phone):
        addquery2 = """
                        INSERT INTO telefons(telefon, clientid) VALUES(%s, %s);
                        """
        clientid = self.define_client(name, surname, email)
        if clientid != None:
            self.cur.execute(addquery2, (phone, clientid))
            self.conn.commit()
        else:
            return print('Клиент не найден')

    def delete_telefons(self, name, surname, email):
        clientid = self.define_client(name, surname, email)
        if clientid != None:
            deletequery = """
                        DELETE FROM telefons where telefons.CLIENTID = %s;
                        """
            self.cur.execute(deletequery, (clientid,))
            self.conn.commit()
        else:
            return print('Клиент не найден')

    def delete_telefon(self, name, surname, email, phone):
        clientid = self.define_client(name, surname, email)
        if clientid != None:
            deletequery = """
            DELETE FROM telefons 
            where telefons.CLIENTID = %s and telefons.telefon = %s;
            """
            self.cur.execute(deletequery, (clientid, phone))
            self.conn.commit()
        else:
            return print('Клиент или телефон не найден')

    def delete_client(self, name, surname, email):
        clientid = self.define_client(name, surname, email)
        if clientid != None:
            deletequery1 = """
            DELETE FROM clients where ID = %s;"""
            deletequery2 = """
            DELETE FROM telefons where telefons.CLIENTID = %s;"""
            self.cur.execute(deletequery2, (clientid,))
            self.conn.commit()
            self.cur.execute(deletequery1, (clientid,))
            self.conn.commit()
        else:
            return print('Клиент не найден')

    def change_client(self, name, surname, email, newname,
                      newsurname, newemail, phone=None, newphone=None):
        clientid = self.define_client(name, surname, email)
        updatequery1 = """
                    UPDATE clients 
                    set name = %s,
                    surname = %s,
                    email = %s
                    WHERE clients."id" = %s;
                    """
        updatequery2 = """
                    UPDATE telefons
                    set telefon = %s
                    WHERE CLIENTID = %s and telefon = %s;
                    """
        if clientid != None and phone != None:
            self.cur.execute(updatequery1, (newname, newsurname, newemail, clientid))
            self.conn.commit()
            self.cur.execute(updatequery2, (newphone, clientid, phone))
            self.conn.commit()

        elif clientid != None:
            self.cur.execute(updatequery1, (newname, newsurname, newemail, clientid))
            self.conn.commit()
        else:
            return print('Клиент не найден')

    def find_client(self, name, surname, email):
        self.cur.execute("""
        SELECT * FROM clients left join telefons on telefons.CLIENTID = Clients.ID
        WHERE clients.name = %s and clients.surname = %s and clients.email = %s;
        """, (name, surname, email))
        result = self.cur.fetchall()
        if result != [] and len(result) == 1:
            return print(f"ID клиента: {result[0][0]}\n"
                         f"Имя клиента: {result[0][1]}\n"
                         f"Фамилия клиента: {result[0][2]}\n"
                         f"Почта клиента: {result[0][3]}\n"
                         f"Телефон клиента: {result[0][5]}")
        elif result != [] and len(result) > 1:
            self.cur.execute("""
        SELECT telefons.telefon FROM clients 
        left join telefons on telefons.CLIENTID = Clients.ID
        WHERE clients.name = %s and clients.surname = %s and clients.email = %s;
        """, (name, surname, email))
            telefons = self.cur.fetchall()
            tels = ''
            counts = 0
            for tel in telefons:
                counts += 1
                if len(telefons) != counts:
                    tels += tel[0] + ' ,'
                else:
                    tels += tel[0]
            return print(f"ID клиента: {result[0][0]}\n"
                         f"Имя клиента: {result[0][1]}\n"
                         f"Фамилия клиента: {result[0][2]}\n"
                         f"Почта клиента: {result[0][3]}\n"
                         f"Телефон(ы) клиента: {tels}")

        else:
            return print('Клиент не найден')

    def drop_tables(self):
        self.cur.execute("DROP TABLE IF EXISTS telefons;")
        self.cur.execute("DROP TABLE IF EXISTS clients;")
        self.conn.commit()

    def get_raw_data(self):
        self.cur.execute("SELECT * FROM clients left join telefons on telefons.CLIENTID = Clients.ID;")
        result = self.cur.fetchall()
        return print(result)


if __name__ == "__main__":
    db = Database("netologydz", "postgres", "12345")
    db.drop_tables()
    db.create_tables()
    db.add_client('Cерофим', 'Иванов', 'email')
    db.add_client('Cер', 'Иванов', 'email', '965')
    db.add_client('Cерофим', 'Петров', 'email', '452')
    db.add_client('Сергей', 'Иванов', 'email', '442235')
    db.add_client('Иван', 'Иванов', 'email', '8(093)')
    db.add_telefon('Иван', 'Иванов', 'email', '9999')
    db.add_telefon('Cер', 'Иванов', 'email', '9999')
    db.add_telefon('Cерофим', 'Петров', 'email', '9999')
    db.add_telefon('Cерофим', 'Петров', 'email', '99211')
    db.delete_client('Сергей', 'Иванов', 'email')
    db.delete_telefon('Cерофим', 'Петров', 'email', '452')
    db.delete_telefons('Cерофим', 'Петров', 'email')
    db.find_client('Cер', 'Иванов', 'email')
    db.change_client('Иван', 'Иванов', 'email', 'Пётр', 'Петров', 'почта', '9999', '801')
