COMPILE_ARGV = {
    'cpp': ['g++-7', 'participant.cpp', '-o', 'participant.out', '-std=c++17', '-Wall', '-Wextra', '-O2'],
    'py': ['cp', 'participant.py', 'participant.out']
}

RUN_ARGV = {
    'cpp': ['./participant.out'],
    'py': ['python3', 'participant.out']
}

LANGUAGE_MATCHING = {
    'cpp': 'GNU C++ 7.4.0',
    'py': 'Python 3.6',
    'txt': 'Plain Text'
}

STATUS_MATCHING = {
    'In queue': 'В очереди',
    'Compiling': 'Компилирование...',
    'Running': 'Выполняется...',
    'Partial': 'Неполное решение',
    'Accepted': 'OK',
    'CE': 'Ошибка компиляции',
    'PE': 'Неправильный формат вывода',
    'RE': 'Ошибка исполнения',
    'ML': 'Превышено ограничение по памяти',
    'TL': 'Превышено ограничение по времени',
    'IL': 'Превышено ограничение реального времени',
    'WA': 'Неправильный ответ',
    'OK': 'OK',
    'FAIL': 'Ошибка проверки'
}
