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

import pipes

from testinfra.backend import base


class DockerBackend(base.BaseBackend):
    NAME = "docker"

    def __init__(self, name, *args, **kwargs):
        self.name, self.user = self.parse_containerspec(name)
        super().__init__(self.name, *args, **kwargs)

    def run(self, command, *args, **kwargs):
        '''Builds the command for docker to execution'''
        cmd = self.get_command(command, *args)
        cmd = pipes.quote(cmd)

        # Need to set console here since we re not dealing with the
        # super class run() signature
        console = "/bin/sh" if 'console' not in kwargs else kwargs['console']
        console = pipes.quote(console)

        docker_command = self.__docker_command(console, cmd)
        out = self.run_local(docker_command)

        out.command = self.encode(cmd)
        return out

    def __docker_command(self, console, command):
        '''Builds the command to be run by the specified console.'''
        docker_command = "docker exec "

        if self.user is not None:
            docker_command += f"-u {pipes.quote(self.user)} "

        docker_command += f"{self.name} {console} -c {command}"

        return docker_command
