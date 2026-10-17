from enum import IntEnum
from random import choices, choice, uniform, sample
from multiprocessing import Process, Queue
from queue import Empty
from time import monotonic, sleep
from prettytable import PrettyTable


PHI = (1 + 5 ** 0.5) / 2
QUANTITY_OF_QUESTIONS = 3


class Status(IntEnum):
    QUEUE = 0
    PASSED = 1
    FAILED = 2


class Mood(IntEnum):
    BAD = 0
    GOOD = 1
    NEUTRAL = 2


class Student:
    def __init__(self, idx, name, gender):
        self.idx = idx
        self.name = name
        self.gender = gender
        self.status = Status.QUEUE
        self.start_time = None
        self.finish_time = None


class Examiner:
    def __init__(self, idx, name, gender):
        self.idx = idx
        self.name = name
        self.gender = gender
        self.current_student = None
        self.total_students = 0
        self.failed_students = 0
        self.start_time = None
        self.finish_time = None


class Exam:
    def __init__(self):
        self.examiners = self._parse_persons("src/exercise1/examiners.txt", Examiner)
        self.students = self._parse_persons("src/exercise1/students.txt", Student)
        self.questions = self._parse_questions()
        self.exam_start = None
        self.exam_finish = None

    def _parse_persons(self, filename, person):
        persons = []
        with open(filename, "r", encoding="utf-8") as file:
            for idx, line in enumerate(file):
                name, gender = line.strip().split()
                persons.append(person(idx=idx, name=name, gender=gender))
        return persons

    def _parse_questions(self):
        questions = {}
        with open("src/exercise1/questions.txt", "r", encoding="utf-8") as file:
            for line in file:
                questions[line.strip()] = 0
        return questions


def one_rand_answer(words, weights, answers):
    random_index = choices(range(len(words)), weights=weights, k=1)[0]
    chosen_item = words.pop(random_index)
    weights.pop(random_index)
    answers.append(chosen_item)


def golden_answers(question, gender, quantity):
    words = question.split()
    if gender == 'Ж':
        words = words[::-1]
    weights = []
    answers = []
    remaining = 1
    for _ in range(len(words) - 1):
        chance = remaining / PHI
        weights.append(chance)
        remaining -= chance
    weights.append(remaining)
    one_rand_answer(words, weights, answers)
    while len(answers) != quantity and choice((True, False, False)):
        one_rand_answer(words, weights, answers)
    return answers


def student_answer(question, gender):
    return golden_answers(question, gender, 1)[0]


def examiner_answer(question, gender):
    return golden_answers(question, gender, len(question.split()))


def make_a_decision(student, s_answers, e_answers, questions):
    mood = Mood(choices(range(3), weights=[1/8, 1/4, 5/8], k=1)[0])
    count_correct_answer = 0
    correct_questions = []
    for i in range(QUANTITY_OF_QUESTIONS):
        if s_answers[i] in e_answers[i]:
            correct_questions.append(questions[i])
            count_correct_answer += 1
    if mood == Mood.BAD:
        student.status = Status.FAILED
    elif mood == Mood.GOOD:
        student.status = Status.PASSED
    else:
        if count_correct_answer > QUANTITY_OF_QUESTIONS - count_correct_answer:
            student.status = Status.PASSED
        else:
            student.status = Status.FAILED
    return correct_questions


def exam_session(student, examiner, questions):
    s_answers = []
    e_answers = []
    for i in range(QUANTITY_OF_QUESTIONS):
        s_answers.append(student_answer(questions[i], student.gender))
        e_answers.append(examiner_answer(questions[i], examiner.gender))
    sleep(uniform(len(examiner.name) - 1, len(examiner.name) + 1))
    student.finish_time = monotonic()
    return make_a_decision(student, s_answers, e_answers, questions)


def work_session(examiner, question_bank, student_queue, result_queue):
    is_lunch = False
    while True:
        examiner.current_student = student_queue.get()
        if examiner.current_student is None:
            examiner.finish_time = monotonic()
            result_queue.put({'EXAMINER_FINISHED': (examiner.finish_time, ),
                              'idx': (examiner.idx, None)})
            break
        examiner.total_students += 1
        questions = sample(list(question_bank.keys()), k=QUANTITY_OF_QUESTIONS)
        examiner.current_student.start_time = monotonic()
        result_queue.put({'EXAM_STARTED': (examiner.current_student.start_time, ),
                          'idx': (examiner.idx, examiner.current_student.idx)})
        questions = exam_session(examiner.current_student, examiner, questions)
        if examiner.current_student.status == Status.FAILED:
            examiner.failed_students += 1
        result_queue.put({'EXAM_FINISHED': (examiner.current_student.status, examiner.current_student.finish_time,
                                            examiner.total_students, examiner.failed_students, questions),
                          'idx': (examiner.idx, examiner.current_student.idx)})
        if monotonic() - examiner.start_time >= 30 and not is_lunch:
            is_lunch = True
            sleep(uniform(12, 18))


def student_render(exam):
    student_table = PrettyTable()
    student_table.field_names = ['Студент', 'Статус']
    students = exam.students.copy()
    students.sort(key=lambda x: x.status)
    for i in range(len(exam.students)):
        student = students[i]
        status = 'Очередь'
        if student.status == Status.PASSED:
            status = 'Сдал'
        elif student.status == Status.FAILED:
            status = 'Провалил'
        student_table.add_row(
            [student.name, status]
        )
    student_table.align['Студент'] = 'l'
    return student_table


def examiner_render(exam):
    examiner_table = PrettyTable()
    examiner_table.field_names = ['Экзаменатор', 'Текущий студент',
                                  'Всего студентов', 'Завалил', 'Время работы']
    for i in range(len(exam.examiners)):
        examiner = exam.examiners[i]
        examiner_table.add_row(
            [examiner.name,
            examiner.current_student.name if examiner.current_student else '-',
            examiner.total_students,
            examiner.failed_students,
            round((examiner.finish_time if examiner.finish_time else monotonic()) - examiner.start_time, 2)]
        )
    examiner_table.align['Экзаменатор'] = 'l'
    examiner_table.align['Текущий студент'] = 'l'
    return examiner_table


def rendering_process(exam):
    student_table = student_render(exam)
    examiner_table = examiner_render(exam)
    print('\033[H\033[J', end='')
    print(student_table)
    print()
    print(examiner_table)
    print()
    print(f'Осталось в очереди: {len([i for i in exam.students if i.status == Status.QUEUE])} из {len(exam.students)}')
    print('Время с момента начала экзамена: ', 
          round((exam.exam_finish if exam.exam_finish else monotonic()) - exam.exam_start, 2))


def rendering_result(exam):
    student_table = student_render(exam)
    examiner_table = examiner_render(exam)
    examiner_table.del_column('Текущий студент')
    print('\033[H\033[J', end='')
    print(student_table)
    print()
    print(examiner_table)
    print()
    print('Время с момента начала экзамена:', 
          round((exam.exam_finish if exam.exam_finish else monotonic()) - exam.exam_start, 2))
    min_exam_time = min((round(x.finish_time - x.start_time, 2)
                         for x in exam.students if x.status == Status.PASSED),
                         default=None)
    print('Имена лучших студентов:',
          ', '.join([i.name for i in exam.students
                     if round(i.finish_time - i.start_time, 2) == min_exam_time and
                     i.status == Status.PASSED]))
    min_percent_failed = min((round(x.failed_students / x.total_students, 2)
                              for x in exam.examiners if x.total_students))
    print('Имена лучших экзаменаторов:',
              ', '.join([i.name for i in exam.examiners
                         if i.total_students and
                         round(i.failed_students / i.total_students, 2) == min_percent_failed]))
    min_failed_time = min((round(x.finish_time, 2)
                           for x in exam.students if x.status == Status.FAILED),
                           default=None)
    print('Имена студентов, которых после экзамена отчислят:',
          ', '.join([i.name for i in exam.students
                     if round(i.finish_time, 2) == min_failed_time and
                     i.status == Status.FAILED]))
    best_questions = max(value for value in exam.questions.values())
    print('Лучшие вопросы:',
          ', '.join([key for key in exam.questions.keys()
                     if exam.questions[key] == best_questions]))
    is_passed = sum(1 for i in exam.students if i.status == Status.PASSED) / len(exam.students) > 0.85
    print('Вывод:',
          'экзамен удался' if is_passed else 'экзамен не удался')
    

def get_messages(exam, result_queue):
    finished = 0
    while finished != len(exam.examiners):
        try:
            action = result_queue.get(timeout=0.1)
            examiner = exam.examiners[action['idx'][0]]
            if 'EXAM_STARTED' in action:
                examiner.current_student = exam.students[action['idx'][1]]
                examiner.current_student.start_time = action['EXAM_STARTED'][0]
            elif 'EXAM_FINISHED' in action:
                examiner.current_student.status = action['EXAM_FINISHED'][0]
                examiner.current_student.finish_time = action['EXAM_FINISHED'][1]
                examiner.current_student = None
                examiner.total_students = action['EXAM_FINISHED'][2]
                examiner.failed_students = action['EXAM_FINISHED'][3]
                for i in action['EXAM_FINISHED'][4]:
                    exam.questions[i] += 1
            elif 'EXAMINER_FINISHED' in action:
                finished += 1
                examiner.finish_time = action['EXAMINER_FINISHED'][0]
        except Empty:
            pass
        rendering_process(exam)


def main():
    exam = Exam()
    student_queue = Queue()
    result_queue = Queue()
    for i in exam.students:
        student_queue.put(i)
    exams = [Process(target=work_session, args=(exam.examiners[i],
                                                exam.questions,
                                                student_queue,
                                                result_queue)) for i in range(len(exam.examiners))]
    exam.exam_start = monotonic()
    for i in range(len(exam.examiners)):
        student_queue.put(None)
        exam.examiners[i].start_time = monotonic()
        exams[i].start()
    get_messages(exam, result_queue)
    exam.exam_finish = monotonic()
    rendering_result(exam)
    for i in range(len(exam.examiners)):
        exams[i].join()


if __name__ == "__main__":
    main()
    