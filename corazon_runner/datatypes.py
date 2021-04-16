import enum
import typing


class Mode(enum.Enum):
    SyncData = 'sync-data'
    RunCalculation = 'run-calc'
    RunConcurrently = 'run-multi-calc'


class TESSLightCurveFile(typing.NamedTuple):
    sector: str
    tic: int
    rel_filename: str
    rel_path: str
    local_dir: str
    option: str
    output_dir: str
