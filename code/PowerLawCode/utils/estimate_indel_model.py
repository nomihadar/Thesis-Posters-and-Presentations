import sys, os
import enum

__author__ = 'Nomi'

sys.path.append(os.path.dirname(sys.path[0]))

from defs import *
from msa_functions import *
from runJobPower import run_job

CMD_PY = "python {script} -f {msa} -o {output}"

MIN_IR = 0 #minimal value of indel rate
MAX_IR = 0.01 #maximal value of indel rate
MIN_A = 1 #minimal value of shape parameter 'a'
MAX_A = 2 #maximal value of shape parameter 'a'
PRECISION = 5 #num digits to round to

class Methods(enum.Enum):
    random = 1
    max_gap_in_ref = 2
    average_length_sequences = 3

def estimate_indel_rate(msa, method):
    if Methods.random:
        ir = np.random.uniform(MIN_IR, MAX_IR)
        ir = round(ir, PRECISION)
    return ir

def estimate_shape_parameter(msa, method):
    if Methods.random:
        while True:
            a = np.random.uniform(MIN_A, MAX_A)
            a = round(a, PRECISION)
            if a != 1: #cannot be exactly 1
                break
    return a

def estimate_root_length(msa, method):
    if Methods.average_length_sequences:
        rl = int(get_average_length_sequences(msa))
    return rl

def estimate_maxi_indel_len(msa, method):

    if Methods.max_gap_in_ref:
        lengths = get_min_max_gap_length(msa)
        max_gap_length = lengths[1]
        if max_gap_length < 2:
            max_gap_length = 2

    return int(max_gap_length)

def main(msa_file, output):

    msa = get_msa_from_file(msa_file)

    ir = estimate_indel_rate(msa, Methods.random)
    a = estimate_shape_parameter(msa, Methods.random)
    rl = estimate_root_length(msa, Methods.average_length_sequences)
    max_gap = estimate_maxi_indel_len(msa, Methods.max_gap_in_ref)
    params = [ir, a, rl, max_gap]

    d = {name: [value] for name, value in zip(COL_NAMES_INDEL_MODEL, params)}
    df = pd.DataFrame(d)
    df = df[COL_NAMES_INDEL_MODEL]
    df.to_csv(output, index=False)

def run_on_paths_list(paths_file):

    df = pd.read_csv(paths_file)
    dirs = df[PATH_COL].tolist()

    for dir in dirs:
        os.chdir(dir)
        if not os.path.exists(SIMULATIONS_DIR):
            os.mkdir(SIMULATIONS_DIR)
        os.chdir(SIMULATIONS_DIR)

        cmd = CMD_PY.format(script=os.path.realpath(__file__),
                            msa=os.path.join(dir, REF_MSA_PHY),
                            output=INDEL_MODEL_OUTPUT)

        run_job(cmd, "job_estimate_indel_model.sh")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('-f', required=True,
                        help='alignment file or file of paths')
    parser.add_argument('-paths', action='store_true',
                        help='if specified - input is df with list of paths')
    parser.add_argument('-o', required=False,
                        help='output name', default=INDEL_MODEL_OUTPUT)
    args = parser.parse_args()

    if args.paths:
        run_on_paths_list(args.f)
    else:
        main(args.f, args.o)
