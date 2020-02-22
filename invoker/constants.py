COMPILE_ARGV = {
    'cpp': ['g++-9', 'participant.cpp', '-o', 'participant.out', '-std=c++17', '-Wall', '-Wextra', '-O2'],
    'py': ['cp', 'participant.py', 'participant.out']
}
RUN_ARGV = {
    'cpp': ['./participant.out'],
    'py': ['python3', 'participant.out']
}
