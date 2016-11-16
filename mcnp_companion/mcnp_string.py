import textwrap
class mstring:
    def __init__(self, string):
        self.string = string

    def flow(self):
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
                print "ampersand"
                newstr = "%s\n" % newstr[:-2]
        return newstr
