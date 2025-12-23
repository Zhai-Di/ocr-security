# README
This directory contains the artifact for the paper _Validity Is Not Enough: Uncovering the Security Pitfall in Chainlink's Off-Chain Reporting Protocol_. Specifically, this artifact includes the datasets we used and our experiments. The requirements for running our experiments are listed in the /requirements.txt file. The workflow of the experiments is described in our submitted Artifact Appendix.
- __./data_ae/__. This directory contains the datasets used in our experiments. Among them, eth_usd_observations.csv and ens_case_data.7z.001 are the datasets we collected, while eth_usd_full_lists.csv and eth_usd_honest_lists.csv were generated during the experiments.
  - __eth_usd_observations.csv__. Observation values from historical instances of Chainlink's ETH/USD price feed, covering the block range from 12,016,450 to 22,648,562.
  - __eth_usd_full_lists.csv__. Chainlink's historical ETH/USD price feed instances which contains 31 observation values.
  - __eth_usd_honest_lists.csv__. The dataset resulting from the filtering described in Section IV-B2. Every observation value in this dataset can be regarded as honest.
  - __ens_case_data.7z.001__. The compressed dataset used for the experiment of ENS case study in Section VI-C. To reconstruct the original dataset, extract it using 7-Zip.
- __./analysis_scripts_ae/__. This directory contains the analysis scripts used for our experiments.
  - __sec4_filter_eth_usd_full_lists.py__ is used to filter the historical ETH/USD price feed instances that have complete observation lists. The filtering results are consistent with eth_usd_full_lists.csv.
  - __sec4_measure_eth_usd_honest_range.py__ can be used to reproduce the experimental results shown in Figure 2 of Section IV-B.
- The directories __./sec6_a_ae/, ./sec6_b_ae/, and ./sec6_c_ae/__ contain the code used in our experiments described in Section VI.
  - __./sec6_a_ae/__ corresponds to the experimental code for RQ1 presented in Section VI.
  - __./sec6_b_ae/__ corresponds to the experimental code for RQ2 presented in Section VI.
  - __./sec6_c_ae/__ implements the ENS case study experiment in Section VI-RQ3. To reproduce the experimental results, the dataset in __./data_ae/ens_case_data.7z.001__ needs to be extracted.
