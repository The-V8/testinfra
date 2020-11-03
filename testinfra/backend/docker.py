# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from testinfra.backend import base


class DockerBackend(base.BaseBackend):
    NAME = "docker"

    def __init__(self, name, *args, **kwargs):
        self.name, self.user = self.parse_containerspec(name)
        super().__init__(self.name, *args, **kwargs)

    def run(self, command, *args, **kwargs):
        '''
        Builds the command for docker to execute and
        passes it on to the run_local function in the
        backend/base.py

        The optional parameter "terminal" can be passed
        to specify the terminal which runs the command.

        Usage:
        host.run("my command")
        host.run("my command", terminal='powershell)
        host.run("my command", terminal='/bin/bash)
        '''
        cmd = self.get_command(command, *args)

        # get the terminal specification - default: "/bin/sh"
        terminal_key = "terminal"
        terminal = (
            "/bin/sh" if terminal_key not in kwargs
            else kwargs[terminal_key])
        # get the docker command
        docker_command, args = self.__docker_command(terminal, cmd)

        # run the built docker command
        out = self.run_local(docker_command, *args)
        out.command = self.encode(cmd)
        return out

    def __docker_command(self, terminal, command):
        '''
        Builds the command to be run by the specified terminal.
        This method does not execute the command

        terminal (str): The terminal to run the command in
        command (str): The command to execute

        Usage:
            __docker_command('/bin/sh', cmd) will return the docker
            command with placeholders and the corresponding args.
        '''
        command_items = []
        args = []
        if self.user is None:
            command_items = [
                "docker exec",
                "%s",
                terminal, "-c",
                "%s"]
            args = [self.name, command]
        else:
            command_items = [
                "docker exec",
                "-u", "%s", "%s",
                terminal, "-c",
                "%s"]
            args = [self.user, self.name, command]

        # join the command into one string
        docker_command = " ".join(command_items)
        return (docker_command, args)
