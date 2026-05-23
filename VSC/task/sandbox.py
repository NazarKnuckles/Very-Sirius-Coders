import docker
import tempfile
import os
import time
import subprocess

client = docker.from_env()


def run_in_sandbox(code: str, input_data: str = "") -> dict:
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        code_path = f.name

    try:
        start_time = time.time()

        result = subprocess.run(
            ['python', code_path],
            input=input_data,  # ← так правильно
            capture_output=True,
            text=True,
            timeout=5,
        )

        execution_time = int((time.time() - start_time) * 1000)

        return {
            'success': result.returncode == 0,
            'output': result.stdout,
            'error': result.stderr,
            'execution_time_ms': execution_time,
            'exit_code': result.returncode,
        }

    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'output': '',
            'error': 'Превышен лимит времени (5 сек)',
            'execution_time_ms': 5000,
            'exit_code': -1,
        }
    except Exception as e:
        return {
            'success': False,
            'output': '',
            'error': f'Ошибка выполнения: {str(e)}',
            'execution_time_ms': 0,
            'exit_code': -1,
        }
    finally:
        os.unlink(code_path)


def run_test_cases(code: str, test_cases) -> list:
    results = []
    for tc in test_cases:
        result = run_in_sandbox(code, tc.input_data)
        result['passed'] = (
                result['success'] and
                result['output'].strip() == tc.expected_output.strip()
        )
        results.append(result)
    return results
