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
        print(command, *args)

        cmd = command = self.quote(command, *args)
        if self.sudo:
            if self.sudo_user is None:
                command = "sudo /bin/sh -c \"{}\"".format(
                    command)
            else:
                command = "sudo -u {} /bin/sh -c \"{}\"".format(
                    self.sudo_user, command)
        print(cmd)

        if self.user is not None:
            container_args = "-u {} {}".format(self.user, self.name)
        else:
            container_args = self.name

        joint_command = "docker exec {container_args} {runtime} -c \"{cmd}\""
        joint_command = joint_command.format(
            container_args=container_args,
            runtime=self.runtime,
            cmd=cmd
        )
        print(joint_command)

        p, stdout, stderr = self.execute_cmd(joint_command)

        out = self.result(p.returncode, command, stdout, stderr)
        out.command = self.encode(cmd)
        return out
