"""``mstring`` is a private class that formats the input deck.

MCNP can only handle old school styled strings, so ``mstring`` formats the
string passed to it to only acceptable columns.
"""

import textwrap
import logging


class mstring(object):
    """``mstring`` are strings that can be printed in MCNP files.

    MCNP is so finicky, and same with Python (with respect to indentation),
    that it's easier to just remove all newlines and split everything into 80
    character blocks.

    :param str string: a string, formatted however, that will be converted
        to MCNP format
    """

    def __init__(self, string):
        """``mstring.__init__`` starts the object with the string given.

        :param str string: a string, formatted however, that will be converted
            to MCNP format
        """
        self.string = string

    def flow(self):
        """``flow`` actually converts the string to MCNP format.

        :return str string: a string with newlines in 80 character blocks
        """
        newstr = ''
        for line in self.string.splitlines():
            # if the line is longer than 80 characters
            if len(line) > 80:
                # if it is a comment
                if line[0] is 'c':
                    str = textwrap.TextWrapper(initial_indent='c ',
                                               subsequent_indent='c ' + ' '*4,
                                               width=80)
                    newstr += "%s\n" % (str.fill(line))
                else:
                    str = textwrap.TextWrapper(initial_indent='',
                                               subsequent_indent=' '*6,
                                               width=78)
                    for _line in str.wrap(line):
                        newstr += "%s &\n" % (_line)
            else:
                newstr += "%s\n" % line
            if newstr[-2] is "&":
                logging.debug("ampersand")
                newstr = "%s\n" % newstr[:-2]
        return newstr
