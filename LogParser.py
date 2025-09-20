from dataclasses import dataclass
import os
from typing import List


@dataclass
class Problem:
    code: str
    name: str
    submissions: List['Submission']

    def __repr__(self):
        return f"Problem(code='{self.code}', name='{self.name}', submissions={self.submissions})"


@dataclass
class Team:
    id: int
    name: str
    submissions: List['Submission']

    def __repr__(self):
        return f"Team(id={self.id}, name='{self.name}', submissions={self.submissions})"


@dataclass
class Submission:
    filename: str
    team: Team
    problem: Problem
    attempt: int
    time: int
    verdict: str

    def __repr__(self):
        return f"\nSubmission(filename={self.filename}, team_id={self.team.id}, problem='{self.problem.code}', attempt={self.attempt}, time={self.time}, verdict='{self.verdict}')"

@dataclass
class SubmissionOfProblem:
    filename: str
    team: Team
    attempt: int
    time: int
    verdict: str

    def __repr__(self):
        return f"\nSubmission(team_id={self.team.id}, attempt={self.attempt}, time={self.time}, verdict='{self.verdict}')"

@dataclass
class SubmissionOfTeam:
    filename: str
    problem: Problem
    attempt: int
    time: int
    verdict: str

    def __repr__(self):
        return f"\nSubmission(problem='{self.problem.code}', attempt={self.attempt}, time={self.time}, verdict='{self.verdict}')"


class LogParser:
    def __init__(self, logfile, archive):
        self.logfile = logfile
        self.archive = archive
        self.contest_name = ""
        self.contest_length = 0
        self.problems_count = 0
        self.teams_count = 0
        self.submissions_count = 0
        self.problems: List[Problem] = []
        self.teams: List[Team] = []
        self.submissions: List[Submission] = []

    def parse(self) -> None:
        
        files = [f for f in os.listdir(self.archive) if os.path.isfile(os.path.join(self.archive, f))]
        with open(self.logfile, 'r', encoding='utf-8') as f:
            idx = -1
            for line in f:
                line = line.strip()
                if not line:
                    continue

                parts = line.split(' ', 1)
                if len(parts) < 2:
                    continue

                cmd, data = parts

                if cmd == "@contest":
                    self.contest_name = data.strip('"')
                elif cmd == "@contlen":
                    self.contest_length = int(data)
                elif cmd == "@problems":
                    self.problems_count = int(data)
                elif cmd == "@teams":
                    self.teams_count = int(data)
                elif cmd == "@submissions":
                    self.submissions_count = int(data)
                elif cmd == '@p':
                    p_data = data.split(',')
                    self.problems.append(Problem(
                        code=p_data[0],
                        name=p_data[1],
                        submissions=[]
                    ))
                elif cmd == '@t':
                    t_data = data.split(',')
                    self.teams.append(Team(
                        id=int(t_data[0]),
                        name=t_data[3],
                        submissions=[]
                    ))
                elif cmd == '@s':
                    idx += 1
                    s_data = data.split(',')

                    # Находим команду по ID
                    team_id = int(s_data[0])
                    team = next((t for t in self.teams if t.id == team_id), None)

                    # Находим задачу по коду
                    problem_code = s_data[1]
                    problem = next((p for p in self.problems if p.code == problem_code), None)

                    submission = Submission(
                        filename=files[idx],
                        team=team,
                        problem=problem,
                        attempt=int(s_data[2]),
                        time=int(s_data[3]),
                        verdict=s_data[4]
                    )

                    # submission_of_team = SubmissionOfTeam(
                    #     filename='',
                    #     problem=problem,
                    #     attempt=int(s_data[2]),
                    #     time=int(s_data[3]),
                    #     verdict=s_data[4]
                    # )
                    #
                    # submission_of_problem = SubmissionOfProblem(
                    #     filename='',
                    #     team=team,
                    #     attempt=int(s_data[2]),
                    #     time=int(s_data[3]),
                    #     verdict=s_data[4]
                    # )

                    self.submissions.append(submission)
                    team.submissions.append(submission)
                    problem.submissions.append(submission)


if __name__ == "__main__":
    parser = LogParser('log.txt', '602776')
    parser.parse()

    print(f"Contest: {parser.contest_name}")
    # print(f"Problems: {[p for p in parser.problems]}")
    # print(f"Teams: {[t for t in parser.teams]}")
    print(f"Submissions: {[s for s in parser.submissions]}")
    # print(data['submissions'])