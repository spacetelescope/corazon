#!/usr/bin/env python

import argparse

from corazon_runner.constants import DATA_HOST
from corazon_runner.datatypes import Mode
from corazon_runner.utils import test_against_tess_data, sync_data, test_against_tess_data_multi


def capture_options() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--data-output', required=True,
                        help="Where to store the output data")
    parser.add_argument('-i', '--data-input', required=True,
                        help="Where to find input data")
    parser.add_argument('-m', '--mode', type=Mode, required=True)

    return parser.parse_args()


def main() -> None:
    options = capture_options()
    if options.mode is Mode.RunCalculation:
        test_against_tess_data(options.data_input, options.data_output)

    elif options.mode is Mode.SyncData:
        sync_data(DATA_HOST, options.data_input)

    elif options.mode is Mode.RunConcurrently:
        test_against_tess_data_multi(options.data_input, options.data_output)

    else:
        raise NotImplementedError(options.mode)


if __name__ == '__main__':
    main()
