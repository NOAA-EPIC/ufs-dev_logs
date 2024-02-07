import sys
sys.path.append( '../modules' )
from load_data import LoadData
from generate_plots import GeneratePlots
from config import username, token

# Instantiate Module for Loading & Preprocessing Data
data_wrapper = LoadData(username, token)
data_wrapper.read_latest_logs(log_dir='/tests/logs')
data_wrapper.preprocess()
data_wrapper.map_metrics()
wall_time_df, test_sz_df = data_wrapper.generate_df()
wall_time_pivot_df = data_wrapper.generate_pivot_df(wall_time_df,
                                                    independent_feature_name='Wall Time (sec)')
test_sz_pivot_df = data_wrapper.generate_pivot_df(test_sz_df,
                                                  independent_feature_name='Max. Resident Set Size (KB)')

# Instantiate Module for Plotting Data
plt_wrapper = GeneratePlots(wall_time_df, test_sz_df)
plt_wrapper.generate_stacked_barplots()
plt_wrapper.generate_barplots_platform()
plt_wrapper.generate_histogramplots(test_sz_pivot_df)

