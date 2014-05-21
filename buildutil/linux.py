# Copyright 2014 Google Inc. All Rights Reserved.
#
# This software is provided 'as-is', without any express or implied
# warranty.  In no event will the authors be held liable for any damages
# arising from the use of this software.
# Permission is granted to anyone to use this software for any purpose,
# including commercial applications, and to alter it and redistribute it
# freely, subject to the following restrictions:
# 1. The origin of this software must not be misrepresented; you must not
# claim that you wrote the original software. If you use this software
# in a product, an acknowledgment in the product documentation would be
# appreciated but is not required.
# 2. Altered source versions must be plainly marked as such, and must not be
# misrepresented as being the original software.
# 3. This notice may not be removed or altered from any source distribution.
#

"""Linux-specific BuildEnvironment sub-module.

Optional environment variables:

CMAKE_PATH = Path to CMake binary. Required if cmake is not in $PATH,
or not passed on command line.
CMAKE_FLAGS = String to override the default CMake flags with.
"""


import distutils.spawn
import os
import shlex
import buildutil.common as common

_CMAKE_PATH_ENV_VAR = 'CMAKE_PATH'
_CMAKE_FLAGS_ENV_VAR = 'CMAKE_FLAGS'
_CMAKE_PATH = 'cmake_path'
_CMAKE_FLAGS = 'cmake_flags'


class BuildEnvironment(common.BuildEnvironment):

  """Class representing a Linux build environment.

  This class adds Linux-specific functionality to the common
  BuildEnvironment.

  Attributes:
    cmake_path: Path to the cmake binary, for cmake-based projects.
    cmake_flags: Flags to pass to cmake, for cmake-based projects.
  """

  def __init__(self, arguments):
    """Constructs the BuildEnvironment with basic information needed to build.

    The build properties as set by argument parsing are also available
    to be modified by code using this object after construction.

    It is required to call this function with a valid arguments object,
    obtained either by calling argparse.ArgumentParser.parse_args() after
    adding this modules arguments via buildutils.add_arguments(), or by passing
    in an object returned from buildutils.build_defaults().

    Args:
      arguments: The argument object returned from ArgumentParser.parse_args().
    """

    super(BuildEnvironment, self).__init__(arguments)

    if type(arguments) is dict:
      args = arguments
    else:
      args = vars(arguments)

    self.cmake_path = args[_CMAKE_PATH]
    self.cmake_flags = args[_CMAKE_FLAGS]

  @staticmethod
  def build_defaults():
    """Helper function to set build defaults.

    Returns:
      A dict containing appropriate defaults for a build.
    """
    args = common.BuildEnvironment.build_defaults()

    args[_CMAKE_PATH] = (os.getenv(_CMAKE_PATH_ENV_VAR) or
                         distutils.spawn.find_executable('cmake'))
    args[_CMAKE_FLAGS] = os.getenv(_CMAKE_FLAGS_ENV_VAR)

    return args

  @staticmethod
  def add_arguments(parser):
    """Add module-specific command line arguments to an argparse parser.

    This will take an argument parser and add arguments appropriate for this
    module. It will also set appropriate default values.

    Args:
      parser: The argparse.ArgumentParser instance to use.
    """
    defaults = BuildEnvironment.build_defaults()

    common.BuildEnvironment.add_arguments(parser)

    parser.add_argument('-c', '--' + _CMAKE_PATH,
                        help='Path to CMake binary', dest=_CMAKE_PATH,
                        default=defaults[_CMAKE_PATH])
    parser.add_argument(
        '-F', '--' + _CMAKE_FLAGS, help='Flags to use to override CMake flags',
        dest=_CMAKE_FLAGS, default=defaults[_CMAKE_FLAGS])

  def run_cmake(self, gen='Unix Makefiles'):
    """Run cmake based on the specified build environment.

    This will execute cmake using the configured environment, passing it the
    flags specified in the cmake_flags property.

    Args:
      gen: Optional argument to specify CMake project generator (defaults to
        Unix Makefiles)

    Raises:
      SubCommandError: CMake invocation failed or returned an error.
      ToolPathError: CMake not found in configured build environment or $PATH.
    """

    common.BuildEnvironment._check_binary('cmake', self.cmake_path)

    args = [self.cmake_path, '-G', gen]
    if self.cmake_flags:
      args += shlex.split(self.cmake_flags, posix=self._posix)
    args.append(self.project_directory)

    self.run_subprocess(args, cwd=self.project_directory)
