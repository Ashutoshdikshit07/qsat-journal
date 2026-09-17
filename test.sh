#!/bin/bash
#SBATCH --job-name=Alt1000_DATE_9_Algo_MaxMin_Time_0_86399_maxIter1_C15
#SBATCH --output=Alt1000_DATE_9_Algo_MaxMin_Time_0_86399_maxIter1_C15.log
#SBATCH -N 1                # Use 1 compute node
#SBATCH -c 15             # Request 15 CPU cores

#SBATCH --partition=normal  # Use Standard partition


# Run the Python script
python3 write_rate_fid_date.py 