import logging
import shlex
import subprocess

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def execute_command(command):
    logging.info(f'Executing command: {command}')
    try:
        # Using shlex to split the command properly
        args = shlex.split(command)
        result = subprocess.run(args, check=True, capture_output=True, text=True)
        logging.info('Command executed successfully')
        return result.stdout
    except subprocess.CalledProcessError as e:
        logging.error(f'Command failed with error: {e.stderr}')
        return None

# Example usage
if __name__ == '__main__':
    command_to_run = 'your_command_here'
    output = execute_command(command_to_run)
    if output:
        logging.info(f'Output: {output}')