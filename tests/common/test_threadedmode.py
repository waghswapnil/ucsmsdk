# Copyright 2017 Cisco Systems, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from nose import SkipTest
from nose.tools import with_setup, assert_equal
import threading
from ..connection.info import custom_setup, custom_teardown, get_skip_msg

handle = None


def setup_module():
    global handle
    handle = custom_setup()
    if not handle:
        msg = get_skip_msg()
        raise SkipTest(msg)


def teardown_module():
    custom_teardown(handle)


def t1_func():
    from ucsmsdk.mometa.ls.LsServer import LsServer
    obj = LsServer("org-root", "temp_sp1")
    handle.add_mo(obj)


def t2_func():
    from ucsmsdk.mometa.ls.LsServer import LsServer
    obj1 = LsServer("org-root", "temp_sp2")
    obj2 = LsServer("org-root", "temp_sp3")
    handle.add_mo(obj1)
    handle.add_mo(obj2)


@with_setup(setup_module, teardown_module)
def test_test_threading_mode():
    handle.set_mode_threading()

    t1 = threading.Thread(name="t1", target=t1_func)
    t2 = threading.Thread(name="t2", target=t2_func)

    t1.start()
    t2.start()

    t1.join()
    t2.join()

    # commit buffers should be in different contexts
    buf1 = handle._get_commit_buf(tag="t1")
    buf2 = handle._get_commit_buf(tag="t2")

    assert_equal(len(buf1), 1)
    assert_equal(len(buf2), 2)

    handle.commit_buffer_discard(tag="t1")
    handle.commit_buffer_discard(tag="t2")

    handle.unset_mode_threading()
