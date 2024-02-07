from subprocess import Popen, PIPE


def start_docker_container():
    docker_compose_command = "docker-compose up --d"
    process = Popen(docker_compose_command, shell=True,
                    stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()

    if process.returncode == 0:
        print("Docker container started successfully.")
    else:
        print(f"Error starting Docker container:\n{stderr.decode('utf-8')}")
