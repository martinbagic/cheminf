import yaml
import argparse
import pickle

from funcs import plot, poset, tranclo, genfuncs, hack
from helper import PATH
import logging


class Hasse:
    def __init__(self):
        '''
        1) Load arguments. 
        2a) Load pickled data.
        2b) Load yaml data and calculate fresh poset and transitive closure.
        3) Plot data.
        '''
        self.set_args()
        self.set_logging()
        self.extract_yaml()

        if self.args.read_pickle:
            self.read_pickle('poset')
            self.read_pickle('tranclo')
        else:
            self.set_poset()
            self.set_transitive_closure()

        if self.args.plot_poset:
            self.plot('poset')

        if self.args.plot_tranclo:
            self.plot('tranclo')

    ### PREPARATION ###

    def set_logging(self):
        if self.args.log:
            logging.basicConfig(
                level=logging.DEBUG,
                format='%(asctime)s --- %(levelname)s ::: %(message)s',
                datefmt="%H:%M:%S",
            )

    def set_args(self):
        ''' Read arguments from cmd. '''
        parser = argparse.ArgumentParser('Molecular Fragment Lattice')

        parser.add_argument('instance', help="name of instance", type=str)

        parser.add_argument(
            '-r', '--read-pickle', help="plot only", action='store_true')
        parser.add_argument(
            '-w', '--write-pickle', help="pickle calculations", action='store_true')

        parser.add_argument(
            '-g', '--plot-poset', help="plot poset", action='store_true')
        parser.add_argument(
            '-t', '--plot-tranclo', help="plot transitive closure", action='store_true')

        parser.add_argument(
            '-l', '--log', help="enable logging", action='store_true'
        )

        self.args = parser.parse_args()

    def extract_yaml(self):
        ''' Fetch data from yaml about a specific instance. '''
        with open(PATH('input.yaml'), 'r') as file:
            yml = yaml.safe_load(file)

        instance = yml[self.args.instance]
        self.mode = instance['mode']
        self.roots = instance['roots']

        if 'canonicalize' in instance:
            self.canonicalizer = hack.Canonicalizer()
            self.roots = [self.canonicalizer(root) for root in self.roots]
        else:
            self.canonicalizer = None

    ### CALCULATION ###
    def set_poset(self):
        ''' Calculate poset from yaml data. '''
        self.poset = poset.Poset(
            genfunc=genfuncs.genfuncs[self.mode],
            roots=self.roots,
            canonicalizer=self.canonicalizer,
        )()
        self.write_pickle('poset')

    def set_transitive_closure(self):
        ''' Calculate transitive closure from poset. '''
        self.tranclo = tranclo.get_transitive_closure(
            poset=self.poset
        )
        self.write_pickle('tranclo')

    ### PICKLES ###

    def read_pickle(self, attr):
        ''' Read old calculated data. '''
        filename = f'{self.args.instance}-{attr}.pickle'
        path = PATH(['pickles', filename])

        with open(path, 'rb') as file:
            obj = pickle.load(file)
            setattr(self, attr, obj)

    def write_pickle(self, attr):
        ''' Write fresh calculated data. '''
        if self.args.write_pickle:
            filename = f'{self.args.instance}-{attr}.pickle'
            path = PATH(['pickles', filename])

            with open(path, 'wb') as file:
                obj = getattr(self, attr)
                pickle.dump(obj, file)

    ### PLOTTING ###

    def plot(self, attr):
        ''' Plot digraph using graphviz. '''
        digraph = plot.get_digraph(
            g=getattr(self, attr),
            roots=self.roots,
            mode=self.mode,
        )

        digraph.render(
            filename=f'{self.args.instance}-{attr}',
            directory=PATH('plots'),
        )


if __name__ == '__main__':
    Hasse()
