import glob
import os
import subprocess
import time
import types

from corazon_runner.constants import LOCAL_DATA_PATH
from corazon_runner.datatypes import TESSLightCurveFile


def locate_and_resolve_tess_datums(input_dir: str) -> types.GeneratorType:
    for filepath in glob.glob(f'{input_dir}/*.txt'):
        filename = os.path.basename(filepath)
        print(f'Loading File: {filename}')
        with open(filepath, 'rb') as stream:
            lines = stream.read().decode('utf-8').split('\n')

        filepath_name = '-'.join(os.path.basename(filepath).rsplit('.', 1)[0].rsplit('_', 3)[1:])
        for line in lines:
            if line in ['']:
                continue

            rel_path = os.path.join(LOCAL_DATA_PATH, line.strip('/'))
            if not os.path.exists(rel_path):
                continue

            rel_filename = os.path.basename(line)
            if rel_filename.startswith('hlsp_tess-spoc'):
                hunk, sector = rel_filename.rsplit('-', 1)
                sector, hunk = sector.split('_', 1)
                sector = int(sector.strip('s'))
                tic, hunk = rel_filename.rsplit('-', 1)
                hunk, tic = tic.rsplit('_', 1)
                tic = int(tic)
                local_dir = os.path.dirname(rel_path)
                output_dir = os.path.join('spoc', filepath_name)
                yield TESSLightCurveFile(sector, tic, rel_filename, rel_path, local_dir, 'tess-spoc', output_dir)

            elif rel_filename.startswith('hlsp_qlp_tess'):
                sector, hunk = rel_filename.rsplit('-', 1)
                hunk, sector = sector.rsplit('_', 1)
                sector = int(sector.strip('s'))
                hunk, tic = rel_filename.rsplit('-', 1)
                tic, hunk = tic.split('_', 1)
                tic = int(tic)
                local_dir = os.path.dirname(rel_path)
                output_dir = os.path.join('qlp', filepath_name)
                yield TESSLightCurveFile(sector, tic, rel_filename, rel_path, local_dir, 'qlp', output_dir)

            else:
                raise NotImplementedError(line)

def test_against_tess_data(input_dir: str, output_dir: str) -> None:
    import os
    import shutil
    import tempfile

    from corazon import run_pipeline

    from tess_stars2px import tess_stars2px_function_entry

    entries = []
    for entry in locate_and_resolve_tess_datums(input_dir):
        entries.append(entry)

    if os.path.exists(output_dir):
        raise IOError(f'Output DIR Exists: {output_dir}')

    os.makedirs(output_dir)

    # import pdb; pdb.set_trace()
    print(f'Light curves found: {len(entries)}')
    print(f'Output Directory: {output_dir}')
    for idx, entry in enumerate(entries):
        if idx % 100 == 0:
            print(f'Chunk: {idx}')

        tic_folder = os.path.join(output_dir, entry.output_dir, str(entry.tic))
        if not os.path.exists(tic_folder):
            os.makedirs(tic_folder)

        # tic_folder = os.path.join(output_dir, str(entry.tic))
        run_pipeline.run_write_one(entry.tic, entry.sector, tic_folder, entry.option, entry.local_dir)


def run_command(cmd: str) -> None:
    proc = subprocess.Popen(cmd, shell=True)
    while proc.poll() is None:
        time.sleep(.1)
        continue

    if proc.poll() in [23]:
        pass

    elif proc.poll() > 0:
        raise NotImplementedError(f'Program Error: {proc.poll()}')


def sync_data(host: str, input_dir: str) -> None:
    for filepath in glob.glob(f'{input_dir}/*.txt'):
        cmd = [f'rsync -avp --files-from {filepath} {host}: {LOCAL_DATA_PATH}']
        import pdb; pdb.set_trace()
        run_command(cmd)

def test_against_tess_data_multi(input_dir: str, output_dir: str) -> None:
    import os
    import shutil
    import tempfile

    from corazon import run_pipeline

    from tess_stars2px import tess_stars2px_function_entry

    entries = []
    for entry in locate_and_resolve_tess_datums(input_dir):
        entries.append(entry)

    if os.path.exists(output_dir):
        raise IOError('Output DIR Exists: {output_dir}')

    os.makedirs(output_dir)

    print(f'Light curves found: {len(entries)}')
    print(f'Output Directory: {output_dir}')
