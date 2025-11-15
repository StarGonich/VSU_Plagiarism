from dataclasses import dataclass
import os
from sqlite3 import Error
from typing import List
import sqlite3


@dataclass
class Contest:
    id: int
    name: str
    contlen: int
    problems: int
    teams: int
    submissions: int


@dataclass
class Problem:
    id: int
    code: str
    name: str


@dataclass
class Team:
    id: int
    code: int
    name: str


@dataclass
class Submission:
    submission_id: int
    language: str
    team_code: int
    problem_code: str
    attempt: int
    time: int
    verdict: str
    code: str

    def __repr__(self):
        return (f"\nSubmission(filename={self.submission_id}{self.language}, team={self.team_code},"
                f" problem='{self.problem_code}', attempt={self.attempt}, time={self.time}, verdict='{self.verdict}')")


class PlagiarismDB:
    def __init__(self, db_file="plagiarism.db"):
        self.db_file = db_file
        self.conn = None

        self.problems: List[Problem] = []
        self.teams: List[Team] = []
        self.submissions: List[Submission] = []

    def connect_db(self):
        try:
            self.conn = sqlite3.connect(self.db_file)
            # print(f"Подключение к SQLite успешно: {self.db_file}")
            return True
        except Error as e:
            print(f"Ошибка подключения: {e}")
            return False

    def close_db(self):
        if self.conn:
            self.conn.close()

    def create_tables(self):
        cursor = self.conn.cursor()
        try:
            sql_create_contests_table = """
            CREATE TABLE IF NOT EXISTS contests (
                contest_id integer PRIMARY KEY,
                contest_name varchar(127),
                contlen integer,
                problems integer,
                teams integer,
                submissions integer
            );
            """
            cursor.execute(sql_create_contests_table)
            self.conn.commit()
        except Error as e:
            print(f"Ошибка создания таблицы contests: {e}")
            exit(-255)

        try:
            sql_create_problems_table = """
            CREATE TABLE IF NOT EXISTS problems (
                problem_id integer PRIMARY KEY AUTOINCREMENT,
                contest_id integer REFERENCES contests(contest_id),
                problem_code char,
                problem_name varchar(127),
                UNIQUE(contest_id, problem_code)
            );
            """
            cursor.execute(sql_create_problems_table)
            self.conn.commit()
        except Error as e:
            print(f"Ошибка создания таблицы problems: {e}")
            exit(-255)

        try:
            sql_create_teams_table = """
            CREATE TABLE IF NOT EXISTS teams (
                team_id INTEGER PRIMARY KEY AUTOINCREMENT,
                contest_id INTEGER REFERENCES contests(contest_id),
                team_code INTEGER,
                team_name VARCHAR(127),
                UNIQUE(contest_id, team_code)
            );
            """
            cursor.execute(sql_create_teams_table)
            self.conn.commit()
        except Error as e:
            print(f"Ошибка создания таблицы teams: {e}")
            exit(-255)

        try:
            sql_create_submissions_table = """
            CREATE TABLE IF NOT EXISTS submissions (
                submission_id bigint PRIMARY KEY,
                language varchar(20),
                contest_id integer REFERENCES contests(contest_id),
                problem_id integer REFERENCES problems(problem_id),
                team_id integer REFERENCES teams(team_id),
                attempt integer,
                time integer,
                verdict varchar(3),
                code text,
                graph text
            );
            """
            cursor.execute(sql_create_submissions_table)
            self.conn.commit()
        except Error as e:
            print(f"Ошибка создания таблицы submissions: {e}")
            exit(-255)
        try:
            sql_create_results_table = """
            CREATE TABLE IF NOT EXISTS results (
                subgraphs_from INTEGER NOT NULL REFERENCES submissions(submission_id),
                isomorphism_to INTEGER NOT NULL REFERENCES submissions(submission_id),
                subgraph_size INTEGER NOT NULL,
                result REAL NOT NULL CHECK (result >= 0 AND result <= 1),
                UNIQUE(subgraphs_from, isomorphism_to, subgraph_size)
            );
            """
            cursor.execute(sql_create_results_table)
            self.conn.commit()
        except Error as e:
            print(f"Ошибка создания таблицы results: {e}")
            exit(-255)
        print("Таблицы созданы успешно")

    def save_contest_info(self, contest: Contest) -> None:
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT OR IGNORE INTO contests(contest_id, contest_name, contlen, problems, teams, submissions)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (contest.id, contest.name, contest.contlen, contest.problems, contest.teams, contest.submissions))
            self.conn.commit()
            print(f"Контест '{contest.name}' сохранён")
        except Error as e:
            print(f"Ошибка сохранения контеста: {e}")

    def save_problem(self, contest_id: int, problem: Problem):
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT OR IGNORE INTO problems (contest_id, problem_code, problem_name)
                VALUES (?, ?, ?) RETURNING problem_id
            """, (contest_id, problem.code, problem.name))
            result = cursor.fetchone()
            if result:
                problem_id = result[0]
            else:
                cursor.execute("""
                    SELECT problem_id FROM problems 
                    WHERE contest_id = ? AND problem_code = ?
                """, (contest_id, problem.code))
                problem_id = cursor.fetchone()[0]
            self.conn.commit()
            return problem_id
        except Error as e:
            print(f"Ошибка сохранения задачи {problem.code}: {e}")
            return None

    def save_team(self, contest_id: int, team: Team):
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT OR IGNORE INTO teams (contest_id, team_code, team_name)
                VALUES (?, ?, ?) RETURNING team_id
            """, (contest_id, team.code, team.name))
            result = cursor.fetchone()
            if result:
                team_id = result[0]
            else:
                cursor.execute("""
                    SELECT team_id FROM teams 
                    WHERE contest_id = ? AND team_code = ?
                """, (contest_id, team.code))
                team_id = cursor.fetchone()[0]
            self.conn.commit()
            return team_id
        except Error as e:
            print(f"Ошибка сохранения команды {team.code}: {e}")
            return None

    def save_submission(self, contest_id: int, problem_id: int, team_id: int, submission: Submission) -> None:
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT OR IGNORE INTO submissions (submission_id, language, contest_id, problem_id, team_id, attempt, 
                time, verdict, code)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (submission.submission_id,
                  submission.language,
                  contest_id,
                  problem_id,
                  team_id,
                  submission.attempt,
                  submission.time,
                  submission.verdict,
                  submission.code))
            self.conn.commit()
        except Error as e:
            print(f"Ошибка сохранения submission: {e}")

    def save_result(self, sub_from: int, iso_to: int, size: int, result: float) -> None:
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO results (subgraphs_from, isomorphism_to, subgraph_size, result)
                VALUES (?, ?, ?, ?)
            """, (sub_from, iso_to, size, result))
            self.conn.commit()
        except Error as e:
            print(f"Ошибка сохранения submission: {e}")

    def parse(self, logfile, archive) -> None:
        contest_id = int(archive)
        if not self.connect_db():
            return
        self.create_tables()
        files = sorted([f for f in os.listdir(archive) if os.path.isfile(os.path.join(archive, f))])
        idx = -1

        problem_db_ids = {}
        team_db_ids = {}

        with open(logfile, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                parts = line.split(' ', 1)
                if len(parts) < 2:
                    continue

                cmd, data = parts

                if cmd == "@contest":
                    contest_name = data.strip('"')
                elif cmd == "@contlen":
                    contlen = int(data)
                elif cmd == "@problems":
                    problems_count = int(data)
                elif cmd == "@teams":
                    teams_count = int(data)
                elif cmd == "@submissions":
                    submissions_count = int(data)

                    contest = Contest(
                        id=contest_id,
                        name=contest_name,
                        contlen=contlen,
                        problems=problems_count,
                        teams=teams_count,
                        submissions=submissions_count
                    )
                    self.save_contest_info(contest)
                elif cmd == '@p':
                    p_data = data.split(',')
                    problem = Problem(
                        id=0,
                        code=p_data[0],
                        name=p_data[1],
                    )
                    problem_id = self.save_problem(contest_id, problem)
                    if problem_id:
                        problem_db_ids[problem.code] = problem_id
                    problem.id = problem_id
                    self.problems.append(problem)

                elif cmd == '@t':
                    t_data = data.split(',')
                    team = Team(
                        id=0,
                        code=int(t_data[0]),
                        name=t_data[3],
                    )
                    team_id = self.save_team(contest_id, team)
                    if team_id:
                        team_db_ids[team.code] = team_id
                    team.id = team_id
                    self.teams.append(team)

                elif cmd == '@s':
                    idx += 1
                    filename, ext = os.path.splitext(files[idx])
                    filepath = os.path.join(archive, files[idx])
                    with open(filepath, 'r', encoding='utf-8') as f:
                        code = f.read()

                    s_data = data.split(',')

                    team_code = int(s_data[0])
                    team_id = team_db_ids[team_code]

                    # Находим задачу по коду
                    problem_code = s_data[1]
                    problem_id = problem_db_ids[problem_code]

                    submission = Submission(
                        submission_id=int(filename),
                        language=ext,
                        team_code=team_code,
                        problem_code=problem_code,
                        attempt=int(s_data[2]),
                        time=int(s_data[3]),
                        verdict=s_data[4],
                        code=code
                    )

                    self.submissions.append(submission)
                    self.save_submission(contest_id, problem_id, team_id, submission)
        print(f"Парсинг завершен. Сохранено в БД:")

    def get_all_contests(self) -> List[Contest]:
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM contests ORDER BY contest_id")

            contests = []
            for row in cursor.fetchall():
                contest = Contest(
                    id=row[0],
                    name=row[1],
                    contlen=row[2],  # эти поля не нужны для выбора
                    problems=row[3],
                    teams=row[4],
                    submissions=row[5]
                )
                contests.append(contest)
            return contests
        except Error as e:
            print(f"Ошибка получения контестов: {e}")
            return []

    def get_problems_by_contest(self, contest_id: int) -> List[Problem]:
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT problem_id, problem_code, problem_name 
                FROM problems 
                WHERE contest_id = ?
            """, (contest_id,))

            problems = []
            for row in cursor.fetchall():
                problem = Problem(
                    id=row[0],
                    code=row[1],
                    name=row[2]
                )
                problems.append(problem)
            return problems
        except Error as e:
            print(f"Ошибка получения contest {contest_id}: {e}")
            return []

    def get_submissions_by_problem(self, problem_id: int) -> List[Submission]:
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT s.submission_id, s.language, s.team_id, p.problem_code, s.attempt, s.time, s.verdict, s.code
                FROM submissions s
                JOIN problems p ON s.problem_id = p.problem_id
                WHERE s.problem_id = ?
            """, (problem_id,))

            submissions = []
            for row in cursor.fetchall():
                submission = Submission(
                    submission_id=row[0],
                    language=row[1],
                    team_code=row[2],
                    problem_code=row[3],
                    attempt=row[4],
                    time=row[5],
                    verdict=row[6],
                    code=row[7]
                )
                submissions.append(submission)
            return submissions
        except Error as e:
            print(f"Ошибка получения посылок задачи {problem_id}: {e}")
            return []

    def get_teams_by_contest(self, contest_id: int) -> List[Team]:
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT team_code, team_name 
                FROM teams 
                WHERE contest_id = ?
            """, (contest_id,))

            teams = []
            for row in cursor.fetchall():
                team = Team(
                    id=row[0],
                    code=row[1],
                    name=row[2]
                )
                teams.append(team)

            return teams
        except Error as e:
            print(f"Ошибка получения команд контеста {contest_id}: {e}")
            return []

    def get_submissions_by_team(self, team_id: int) -> List[Submission]:
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT s.submission_id, s.language, t.team_code, s.problem_id, s.attempt, s.time, s.verdict, s.code
                FROM submissions s
                JOIN teams t ON s.team_id = t.team_id
                WHERE s.team_id = ?
            """, (team_id,))

            submissions = []
            for row in cursor.fetchall():
                submission = Submission(
                    submission_id=row[0],
                    language=row[1],
                    team_code=row[2],
                    problem_code=row[3],
                    attempt=row[4],
                    time=row[5],
                    verdict=row[6],
                    code=row[7]
                )
                submissions.append(submission)
            return submissions
        except Error as e:
            print(f"Ошибка получения посылок задачи {team_id}: {e}")
            return []

    def get_subgraph_sizes(self) -> List[int]:
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT DISTINCT subgraph_size FROM results ORDER BY subgraph_size")

            return [row[0] for row in cursor.fetchall()]
        except Error as e:
            print(f"Ошибка получения размеров подграфов: {e}")
            return []

    def get_results_by_filters(self, contest_id: int, problem_code: str, subgraph_size: int) -> List[tuple]:
        try:
            cursor = self.conn.cursor()
            query = """
            SELECT 
                r.subgraphs_from,
                r.isomorphism_to, 
                r.subgraph_size,
                r.result,
                t1.team_code as from_team,
                t2.team_code as to_team,
                p.problem_code,
                s1.attempt as from_attempt,
                s2.attempt as to_attempt
            FROM results r
            JOIN submissions s1 ON r.subgraphs_from = s1.submission_id
            JOIN submissions s2 ON r.isomorphism_to = s2.submission_id
            JOIN teams t1 ON s1.team_id = t1.team_id
            JOIN teams t2 ON s2.team_id = t2.team_id
            JOIN problems p ON s1.problem_id = p.problem_id
            WHERE p.contest_id = ? AND p.problem_code = ? AND r.subgraph_size = ?
            ORDER BY r.result DESC
            """

            cursor.execute(query, (contest_id, problem_code, subgraph_size))
            return cursor.fetchall()
        except Error as e:
            print(f"Ошибка получения результатов: {e}")
            return []

    def get_problem_codes_by_contest(self, contest_id: int) -> List[str]:
        """УДАЛИТЬ НАХЕР"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT DISTINCT problem_code 
                FROM problems 
                WHERE contest_id = ? 
                ORDER BY problem_code
            """, (contest_id,))
            return [row[0] for row in cursor.fetchall()]
        except Error as e:
            print(f"Ошибка получения кодов задач: {e}")
            return []

    def get_final_results_by_filters(self, contest_id: int, problem_code: str, subgraph_size: int,
                                     limit: int = 50, offset: int = 0) -> List[tuple]:
        try:
            cursor = self.conn.cursor()
            query = """
            SELECT 
                r1.subgraphs_from as sub1,
                r1.isomorphism_to as sub2,
                r1.subgraph_size as size,
                r1.result as result1,
                r2.result as result2,
                s1.code as code1,
                s2.code as code2,
                CASE 
                    WHEN r1.result < r2.result THEN r1.result 
                    ELSE r2.result 
                END as final_result
            FROM results r1
            JOIN results r2 ON r1.subgraphs_from = r2.isomorphism_to 
                        AND r1.isomorphism_to = r2.subgraphs_from 
                        AND r1.subgraph_size = r2.subgraph_size
            JOIN submissions s1 ON r1.subgraphs_from = s1.submission_id
            JOIN submissions s2 ON r1.isomorphism_to = s2.submission_id
            JOIN problems p ON s1.problem_id = p.problem_id
            WHERE p.contest_id = ?
                AND p.problem_code = ?
                AND r1.subgraph_size = ?
                AND r1.subgraphs_from < r1.isomorphism_to  -- избегаем дубликатов
            ORDER BY final_result DESC
            LIMIT ? OFFSET ?
            """

            cursor.execute(query, (contest_id, problem_code, subgraph_size, limit, offset))
            return cursor.fetchall()
        except Error as e:
            print(f"Ошибка получения финальных результатов: {e}")
            return []


if __name__ == "__main__":
    db = PlagiarismDB('plagiarism.db')
    db.parse('log.txt', '602776')
    print(db.problems)
    # print(db.get_problems_by_contest(602776))
    # print(db.get_submissions_by_problem(11))
    print(db.get_submissions_by_team(11))
    print(db.get_final_results_by_filters(602776, 'B', 4))
    # print(db.get_final_results_by_filters(602776, 'C', 4))
    # print(db.teams)
    # print(db.submissions)

    db.close_db()