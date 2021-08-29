import logging

from . import __version__ as VERSION
from .__words__ import Words
from .__swing__ import Swing
from argparse import ArgumentParser

LOG_LEVEL = ['DEBUG', 'INFO', 'WARN', 'ERROR', 'CRITICAL']
USER_CHOICE = LOG_LEVEL+list(map(lambda w: w.lower(), LOG_LEVEL))


class Process:

    def __init__(self, args):
        self.ids = [6, 15]
        self.words = self.get_words(args.sources, args.column)

    def get_words(self, sources, column):
        words = Words(column)
        for src in sources:
            words.parse(src)
        return words

    def get_hinsi(self):
        d = {}
        for id in self.ids:
            if id in self.words.hinsi:
                d[id] = sorted(self.words.hinsi[id].items(), key=lambda x:len(x[1]))
        return d

    def get_distance(self):
        for x in Swing().distance(self.words, self.ids):
            for d in x:
                yield d

    def get_swing(self, num):
        if num > 0:
            high = []
            for x in Swing().swing(self.words, self.ids):
                high.extend(x[0:num])
                high = sorted(high, reverse=True, key=lambda x: x.score)[0:num]
            for d in high:
                yield d
        else:
            for x in Swing().swing(self.words, self.ids):
                for d in x:
                    yield d


class CLI:

    def __init__(self):
        self.setup()

    def setup(self):
        self.parser = ArgumentParser()
        self.parser.add_argument(
            '-v',
            '--version',
            action='version',
            version=u'%(prog)s version ' + VERSION
        )
        self.parser.add_argument(
            '--dumpversion',
            action='version',
            version=VERSION
        )
        self.parser.add_argument(
            '--log',
            choices=USER_CHOICE,
            default="WARN",
            help="set log level."
        )

        subparser = self.parser.add_subparsers()

        count_cmd = subparser.add_parser(
            'count',
            description='count words',
            help='count words. see `count -h`')
        count_cmd.set_defaults(handler=self.command_count)

        distance_cmd = subparser.add_parser(
            'distance',
            description='distance counted words',
            help='distance counted words. see `distance -h`')
        distance_cmd.set_defaults(handler=self.command_distance)

        show_cmd = subparser.add_parser(
            'show',
            description='show words',
            help='show words. see `show -h`')
        show_cmd.set_defaults(handler=self.command_show)
        show_cmd.add_argument(
            '-a',
            '--attr',
            action='append',
            default=[],
            help="set show mrph attributes"
        )

        swing_cmd = subparser.add_parser(
            'swing',
            description='show notation fluctuations',
            help='show notation fluctuations. see `swing -h`')
        swing_cmd.set_defaults(handler=self.command_swing)
        swing_cmd.add_argument(
            '-n',
            '--num',
            type=int,
            default=30,
            help="Display n items from the highest score. All if n is less than or equal to 0"
        )

        input_file_cmds = [count_cmd, distance_cmd, show_cmd, swing_cmd]
        for cmd in input_file_cmds:
            cmd.add_argument(
                '-c',
                '--column',
                action='append',
                default=[],
                help="specific csv file column name."
            )
            cmd.add_argument(
                'sources',
                metavar='SOURCE',
                nargs='+',
                help='input files'
            )

        subcommands = self.parser.format_usage().split('{')[1].split('}')[0]
        help_cmd = subparser.add_parser('help', help='show subcommand help. see `help -h`')
        help_cmd.set_defaults(handler=self.command_help)
        help_cmd.add_argument(
            'subcommand',
            nargs=1,
            help='subcommand name {' + subcommands + '}'
        )
        help_cmd_default_usage = help_cmd.format_usage().replace('usage: ', '')
        help_cmd.usage = help_cmd_default_usage.replace('subcommand', 'subcommand{' + subcommands + '}')

    def parse_command_line(self, argv):
        args = self.parser.parse_args(argv)
        numeric_level = getattr(logging, args.log.upper(), None)
        if not isinstance(numeric_level, int):
            raise ValueError('Invalid log level: %s' % args.log)
        logging.basicConfig(level=numeric_level)
        return args

    def get_process(self, args):
        return Process(args)

    def command_count(self, args):
        proc = self.get_process(args)
        for v in proc.get_hinsi().values():
            for word,arr in v:
                print("{} : {}".format(len(arr), word))

    def command_distance(self, args):
        proc = self.get_process(args)
        for d in proc.get_distance():
            print(d.format())

    def command_swing(self, args):
        proc = self.get_process(args)
        for d in proc.get_swing(args.num):
            print(d.format())

    def get_variables(self, mrph, vars):
        s = []
        for v in vars:
            id = v + "_id"
            if hasattr(mrph, v):
                if hasattr(mrph, id):
                    s.append("{}({})".format(getattr(mrph, v), getattr(mrph, id)))
                else:
                    s.append("{}".format(getattr(mrph, v)))
        return s

    def command_show(self, args):
        proc = self.get_process(args)
        vars = args.attr
        if len(vars) == 0:
            vars.append('hinsi')
        for mrphs in proc.words.mrphs:
            infos = []
            s = ""
            prev = ""
            for mrph in mrphs:
                infos.insert(0, "{}└ {}".format(prev, ','.join(self.get_variables(mrph, vars))))
                prev = "\033[34m{}\033[33m\033[4m{}\033[0m".format(s, mrph.midasi)
                s += mrph.midasi
            print(prev)
            for info in infos:
                print(info)

    def command_help(self, args):
        print(self.parser.parse_args([args.subcommand[0], '--help']))

    def print_help(self):
        self.parser.print_help()

    def execute(self):
        self.execute_with_args()

    def execute_with_args(self, argv=None):
        args = self.parse_command_line(argv)
        if hasattr(args, 'handler'):
            args.handler(args)
        else:
            self.print_help()

def main():
    cli = CLI()
    cli.execute()

if __name__ == '__main__':
    main()
