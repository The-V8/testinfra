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
        Builds the command for docker to execution
        '''
        cmd = self.get_command(command, *args)

        # Need to set console here since we re not dealing with the
        # super class run() signature
        console = "/bin/sh" if 'console' not in kwargs else kwargs['console']

        docker_command, args = self.__docker_command(console, cmd)
        out = self.run_local(docker_command, *args)

        out.command = self.encode(cmd)
        return out

    def __docker_command(self, console, command):
        '''
        Builds the command to be run by the specified console.
        This method does not execute the command.
        '''
        command_items = ["docker exec"]
        args = [self.name, command]
        user_flag = "-u %s"

        if self.user is not None:
            command_items.append(user_flag)
            args.insert(0, self.user)

        command_items.extend(["%s", console, "-c", "%s"])
        docker_command = " ".join(command_items)
        return (docker_command, args)
