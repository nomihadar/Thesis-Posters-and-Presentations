import os, sys

__author__ = 'Nomi'

sys.path.append(os.path.dirname(sys.path[0]))

from defs import *
#from utils import change_path_permissions_to_777

# qsub command and arguments
QSUB_ARGS = \
'''
#!/bin/bash

#PBS -S /bin/bash
#PBS -r y
#PBS -q itaym
#PBS -v PBS_O_SHELL=bash,PBS_ENVIRONMENT=PBS_BATCH
#PBS -N {job_name}
#PBS -e .
#PBS -o .
#PBS -l nodes=compute-0-259+compute-0-260+compute-0-261+compute-0-262
cd $PBS_O_WORKDIR

module load python/python-anaconda3.5
{commands}
'''

#module load python/anaconda_python-3.5

SH_FILE = "job.sh"
DIRECTORY = "run_{}"

CMD = ''

def run_job(cmd, sh_file=SH_FILE, job_name="job", priority=-1):
    # create the arguments file for qsub
    with open(sh_file, 'w') as f:
        qsub_args = QSUB_ARGS.format(commands=cmd,
                                     priority=priority,
                                     job_name=job_name)
        f.write(qsub_args)

    #change_path_permissions_to_777(os.getcwd())

    cmd = "qsub {sh_file}".format(sh_file=sh_file)
    call(cmd.split(" "))


def main(command, sh_file, multiply_jobs, priority, job_name):
    if not multiply_jobs:
        run_job(command, sh_file, job_name, priority)
    else:
        for i in range(1, multiply_jobs + 1):
            dir = DIRECTORY.format(i)
            os.makedirs(dir)
            os.chdir(dir)
            run_job(command, sh_file, job_name, priority)
            os.chdir("../")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--command', '-cmd', required=False,
                        default=CMD, help='command to run')
    parser.add_argument('-n', default=0, type=int,
                        help='number of times to run command')
    parser.add_argument('--sh_file', '-sh', default=SH_FILE,
                        required=False, help='name of .sh file')
    parser.add_argument('--priority', '-p', default=0, type=int,
                        required=False, help='priority of job')
    parser.add_argument('-job_name', default="job",
                        required=False, help='name of job')

    args = parser.parse_args()

    main(args.command, args.sh_file, args.n, args.priority, args.job_name)

