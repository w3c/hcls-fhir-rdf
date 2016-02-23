# Copyright (c) 2016, Mayo Clinic
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
# Redistributions of source code must retain the above copyright notice, this
#     list of conditions and the following disclaimer.
#
#     Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions and the following disclaimer in the documentation
#     and/or other materials provided with the distribution.
#
#     Neither the name of the <ORGANIZATION> nor the names of its contributors
#     may be used to endorse or promote products derived from this software
#     without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, 
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
# OF THE POSSIBILITY OF SUCH DAMAGE.


t1 = '\t'
t2 = '\t' * 2
t3 = '\t' * 3
t4 = '\t' * 4

GENX = False


def genx(s: str) -> str:
    """ Emit GENX if called for
    :param s: string to emit
    :return: emitted string if called for
    """
    return ('%%GenX:{' + s + '%%}') if s and GENX else ''


def dotted_cdr(p: str) -> str:
    """ Return the rightmost node of path p
    :param p: path
    :return: rightmost dot separated nodp

    >>> dotted_cdr("A1.b2.c3")
    'c3'

    >>> dotted_cdr("abc")
    'abc'

    >>> dotted_cdr("a1.b2.")
    ''

    >>> dotted_cdr(".a")
    'a'

    >>> dotted_cdr(".")
    ''

    >>> dotted_cdr('')
    ''

    """
    return p if '.' not in p else p.rsplit('.', 1)[1]


def dotted_car(p: str) -> str:
    """ Return the leftmost node of path p
    :param p: path
    :return: everything to the left of the rightmost dot

    >>> dotted_car("A1.b2.c3")
    'A1.b2'

    >>> dotted_car("abc")


    >>> dotted_car("a1.b2.")
    'a1.b2'

    >>> dotted_car("a1.b2.")
    'a1.b2'

    >>> dotted_car(".a")
    ''

    >>> dotted_car(".")
    ''

    >>> dotted_car('')


    """
    return None if '.' not in p else p.rsplit('.', 1)[0]
