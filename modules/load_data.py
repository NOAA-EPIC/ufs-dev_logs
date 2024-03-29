import sys
import os

# Inital setup modules
from init_setup import init_setup
import shutil
from git import Repo

# Data Maniputlation
import pandas as pd
from collections import defaultdict
import itertools
from functools import reduce
import time
from time import mktime
from datetime import datetime
import re
import numpy as np

class LoadData():
    """
    Pull, load, extract, & preprocess UFS-WM data.
    
    """
    def __init__(self, gh_username, gh_token, repo_abbrev='ufs-wm',  branch='develop'):
        """
        Args:                          
            gh_username (str): GitHub username

            gh_token (str): GiHub token
            
            repo_abbrev (str): Name of repository. Default: 'ufs-wm'
            
            branch (str): Default: Name of repository. 'develop
                              
        """
        # Clone & pull UFS-WM repo
        self.username, self.token = gh_username, gh_token
        self.repo_abbrev, self.branch = repo_abbrev, branch
        if not os.path.exists('ufs-repo'):
            print(f'Cloning {self.repo_abbrev} repo from remote ...')
            init_setup(self.username, self.token, self.repo_abbrev, self.branch)

        else:
            print(f'The {repo_abbrev} repo exist on local.')

        # Load local repo & verify active branch 
        self.local_repo_dir = os.getcwd() + '/ufs-repo'
        self.my_local_repo = Repo(self.local_repo_dir)
        print(f'\nCurrently on Active Branch: {self.my_local_repo.active_branch}')

        # Forcing a pull from remote repo to overwrite local repo
        self.my_local_repo.git.reset('--hard', f'origin/{self.my_local_repo.active_branch}')
        
        # Fetch information from remote repository & pull to local repo.
        print(f'\nPulling {self.repo_abbrev} repo from remote ...')
        self.my_local_repo.remote().pull(self.my_local_repo.active_branch)
        print('\nCompleted.')
        
        # Create directory to save results
        if not os.path.exists("dataframes"):
            os.mkdir("dataframes")

    def read_latest_logs(self, log_dir='/tests/logs', days_of_commits=10):
        """
        Extracts latest logs of UFS-WM RT & OpnReq Test framework.

        Args:
            log_dir (str): Relative directory of the where the logs files
                           are located in repository.

            days_of_commits (int): N number of days worth of commits.
            
        Return: None

        Note:
        - As of 01/2024, many platforms were removed from UFS-WM repo, log filenames, & UFS-WM RT
        framework structure were changed since 2022. In addition, there are logs saved with compiler 
        names residing within the UFS-WM RT framework that are no longer in use, but not 
        been removed -- as a result, those unused logs within the logs directory will be filtered 
        out within this method.
        
        - 2022: Some tests logs are defined by the platform and their
        associated compiler for which the tests was compiled on -- however
        not all of these log files will have a defined compiler listed within
        their filenames. Some Operation Requirements Tests logs are defined by the regression test name, 
        platform, & compiler listed within their filenames (e.g. OpnReqTests_cpld_bmark_p8_hera.intel.log)
        
        """
        # Observe commits made to against log's directory (e.g. /tests as of 2022) within last N days 
        commits_dict = defaultdict()
        commits_files_dict = {}
        for commit in self.my_local_repo.iter_commits('--all', max_count=100, since=f'{days_of_commits}.days.ago', paths='./tests'):
            print(commit)
            print("Committed by %s on %s with sha %s" % (commit.committer.name, time.strftime("%a, %d %b %Y %H:%M", time.localtime(commit.committed_date)), commit.hexsha))
            commits_dict[datetime.fromtimestamp(mktime(time.localtime(commit.committed_date)))] = {commit.hexsha: list(commit.stats.files.keys())}

        # Extract & generate list of relevant logs.
        unique_log_list = []
        for log_fn in os.listdir(self.local_repo_dir + log_dir):
            if 'intel' not in log_fn and 'RT-run' not in log_fn and '.log' in log_fn:
                unique_log_list.append(log_fn)
        print('\nList of relevant logs:\n', unique_log_list)

        # Generate dictionary of the latest commit's RT log corpuses
        self.log_files_corpus = {}
        log_file_content = []
        for log_filename in unique_log_list:
            try:
                # Checkout most recent committed log files to pull updates to local
                recent_log_committed = self.my_local_repo.git.show('{}:{}'.format([v for v in commits_dict[max(commits_dict)].keys()][0], f'.{log_dir}/{log_filename}'))
                self.log_files_corpus[(log_filename, max(commits_dict))] = recent_log_committed
            except:
                pass

        return
    
    def preprocess(self):
        """
        Extracts & parses metrics featured within logs.

        Args:
            None
            
        Return: Log information preprocessed per test per platform-to-compiler.

        """
        # Generate dictionary of parsed log details
        self.parsed_txt_dict = defaultdict(list)

        # Map the test size abbreviations to powers of 10 
        test_sz_abbrev = {'KB': (2**10),
                          'MB': (2**10)**2, 
                          'GB': (2**10)**3,
                          'TB': (2**10)**4}
        
        # Parse through log names & dates of latest retrieval
        for (log_fn, commit_date), txt in self.log_files_corpus.items():

            # Parse & extract platform and compiler from logs.
            pf = log_fn.split(".")[:-1][0]
            pf = pf.split("_",1)[1].title()
            
            # Parse log information per test per platform-to-compiler.
            framework_type = str()
            bl_test_dir = []
            compare_test_dir = []
            dtimes_performed = []
            dtimes_completed = []
            tot_times = []
            unique_test_steps = []
            unique_test_time = []
            unique_test_sz = []
            log_txt_list = []
            compile_builds_txt = []
            tests_txt = []
            reg_test_case = []
            reg_test = []
            failed_reg_test = []
            reg_test_stat = []
            for line in txt.split('\n'):
                log_txt_list.append(line)
                if "COMPILE" in line:
                    compile_builds_txt.append(line.split(' ')[3].replace("'", ""))   
                if log_fn.startswith('OpnReqTests'):  
                    if "Test " and " PASS" in line or "Test " and " FAIL Tries" in line:
                        reg_test_case.append(line.split(' ')[1])
                        casentest = line.split(' ')[1]
                        reg_test.append(casentest)
                        reg_test_stat.append(line.split(' ')[-1])
                elif log_fn.startswith('RegressionTests'):
                    if "PASS -- TEST" in line:
                        reg_test_case.append(line.split(' ')[1])
                        reg_test.append(line.split(' ')[3].replace("'", ""))
                        reg_test_stat.append(line.split(' ')[0])

                        # Extract test time 
                        unique_test_time.append(line[line.find("[")+1:line.find("]")])

                        # Extract test size
                        unique_test_sz.append(line.split('](')[-1].replace(")", ""))
                        
                    if "TEST" and " FAIL TO COMPARE" in line:
                        failed_reg_test.append(line[line.find("(")+1:line.find(")")])
                        
                    # Accomodating the empty test size with measurement unit placeholder
                    x1 = [x.split(' ')[0] if x.split(' ')[0]!='' else 0 for x in unique_test_sz]
                    x2 = [" ".join(re.findall("[a-zA-Z]+", x)) for x in unique_test_sz]
                    refactored_vector = ['{} {}'.format(x1,x2) for x1, x2 in zip(x1,x2)]   
                    
                    # Partition elements of test size & convert to numeric
                    x3 = [test_sz_abbrev[x.split(' ')[-1]] if x.split(' ')[-1] in test_sz_abbrev.keys() else 1 for x in refactored_vector]
                    x4 = np.asarray([re.sub("[^0-9]", "", x) for x in refactored_vector], dtype=int)
                    unique_test_sz_parsed = x3*x4

                    # Partition elements of test time & convert to numeric
                    wallnwait_times = [x.split(', ')[0] if x!=', ' else '00:00' for x in unique_test_time]
                    run_times = [x.split(', ')[1] if x!=', ' else '00:00' for x in unique_test_time]
                    wallnwait_dt_list = [datetime.strptime(elem, '%M:%S') for elem in wallnwait_times]
                    run_dt_list = [datetime.strptime(elem, '%M:%S') for elem in run_times]
                    zero_dt_list = [datetime.strptime('00:00', '%M:%S')]*len(run_dt_list)

                    # Overall test time (Wall time + Wait time + Run time)
                    unique_test_time_parsed = np.asarray(run_dt_list) - np.asarray(zero_dt_list) + np.asarray(wallnwait_dt_list)
                    
                    # Extract only time
                    unique_test_time_parsed = [dt_obj.time() for dt_obj in unique_test_time_parsed]
                    run_dt_list = [dt_obj.time() for dt_obj in run_dt_list]
                    wallnwait_dt_list = [dt_obj.time() for dt_obj in wallnwait_dt_list]
                    
            # Operation Req. & Regression Test logs feature different internal formats
            if log_fn.startswith('OpnReqTests'):
                
                # Framework type parsed & extracted
                framework_type = log_txt_list[1].replace('Start ', '')

                # Test Start/End Datetimes.
                dtimes_performed.append(log_txt_list[0])
                dtimes_completed.append(log_txt_list[-2])
                tot_times.append(re.sub("[^:0-9]", "", log_txt_list[-1].split(': ')[1]))

                # Compared & moved files per test per platform-to-compiler parsed & extracted
                bl_test_dir = list(re.findall(r'baseline dir = (.*?)working', txt.replace("\n", "")))
                
                # Test build steps parsed & extracted
                work_test_dir = list(re.findall(r'working dir  = (.*?)Checking', txt.replace("\n", " ")))

                # Test defined steps
                unique_test_steps = list(re.findall(r'results ....(.*?)0:', txt.replace("\n", "")))
                
                # Wall time (s) parsed & extracted
                unique_test_time = list(re.findall(r'The total amount of wall time(.*?)newline_stamp', txt.replace("\n", "newline_stamp")))
                unique_test_time_parsed = [float(t.split("= ")[-1]) for t in unique_test_time]
                
                # Convert Wall time to mins to maintain time measurement units consistency with regression test logs
                unique_test_time_parsed = [divmod(t, 60) for t in unique_test_time_parsed]
                unique_test_time_parsed = [datetime.strptime(str(int(elem[0]))+':'+str(round(elem[1], 6)), '%M:%S.%f').time() for elem in unique_test_time_parsed]
    
                # Maximum test size (Kb) parsed & extracted
                unique_test_sz = list(re.findall(r'maximum resident set size(.*?)newline_stamp', txt.replace("\n", "newline_stamp")))
                unique_test_sz_parsed = [float(t.split("= ")[-1]) for t in unique_test_sz]
                                
                unique_test_bl = dict(zip(reg_test, bl_test_dir))
                unique_test_work = dict(zip(reg_test, work_test_dir))
                unique_test_info = dict(zip(reg_test, unique_test_steps)) 
                
                mv_d = {}
                compare_d = {}
                for k, v in unique_test_info.items():
                    compare_files = []
                    compare_status = []
                    mv_files = []
                    mv_status = []
                    compare_files = list(re.findall(r'Comparing (.*?) .', v))
                    compare_status = list(re.findall(r'\.{6,15}(.*?) ', v))
                    mv_files = list(re.findall(r'Moving (.*?) .', v))
                    mv_status = list(re.findall(r'\.{6,15}(.*?) ', v))
                    compare_d[k] = dict(zip(compare_files, compare_status))
                    mv_d[k] = dict(zip(mv_files, mv_status))
                    
                # Convert start & end time per Opn Req. log to datetime
                dtimes_performed = [datetime.strptime(elem, '%a %b  %d %H:%M:%S %Z %Y') for elem in dtimes_performed]
                dtimes_completed = [datetime.strptime(elem, '%a %b  %d %H:%M:%S %Z %Y') for elem in dtimes_completed]
                
                # Convert total ("elapsed") time of the overall tests within Opn. Req. test log to datetime
                tot_times = [datetime.strptime(elem, '%H:%M:%S').time() for elem in tot_times]
                
                # Variables nulled as it is not applicable to the Opn. Req. Test logs
                wallnwait_dt_list = []
                run_dt_list = []

            elif log_fn.startswith('RegressionTests'):
                
                # Framework type parsed & extracted
                framework_type = log_txt_list[0].split(' ')
                framework_type = framework_type[-3] + ' ' + framework_type[-2]

                # Test Start/End Datetimes. 
                for txt in log_txt_list:
                    if 'Starting Date/Time' in txt:
                        dtimes_performed.append(txt.split(': ')[1])
                    if 'Ending Date/Time' in txt:
                        dtimes_completed.append(txt.split(': ')[1])
                    if 'Total Time' in txt:
                        tot_times.append(re.sub("[^:0-9]", "", txt.split(': ')[1]))

                    # Sourced comparison & baseline directorues
                    if 'BASELINE DIRECTORY' in txt:
                        bl_test_dir.append(txt.split(' ')[-1])
                        unique_test_bl = bl_test_dir
                    if 'COMPARISON DIRECTORY' in txt:
                        compare_test_dir.append(txt.split(' ')[-1])
                        compare_d = compare_test_dir

                # Convert start & end time per RT log to datetime
                dtimes_performed = [datetime.strptime(elem, '%Y%m%d %H:%M:%S') for elem in dtimes_performed]
                dtimes_completed = [datetime.strptime(elem, '%Y%m%d %H:%M:%S') for elem in dtimes_completed]

                # Convert total time of the overall tests within Opn. Req. test log to datetime
                tot_times = [datetime.strptime(elem, '%H:%M:%S').time() for elem in tot_times]
                
                # Variables nulled as it is not applicable to Req. Test logs
                work_test_dir = list()
                unique_test_work = dict()
                unique_test_info = dict()
                mv_d = dict()

            # Both Opn. Req. Test & Regression test logs will feature time & size per test
            unique_test_wallnwait_dt = dict(zip(reg_test, wallnwait_dt_list))
            unique_test_run_dt = dict(zip(reg_test, run_dt_list))
            unique_test_time = dict(zip(reg_test, unique_test_time_parsed))
            unique_test_sz = dict(zip(reg_test, unique_test_sz_parsed)) 

            # Dictionary of parsed log details
            self.parsed_txt_dict[(pf, commit_date)] = {"Platform": pf,
                                                      "Tests_Performed_Date": dtimes_performed,
                                                      "Test_Framework_Type": framework_type.title(),
                                                      "Builds": compile_builds_txt,
                                                      "Unique_Tests": reg_test,
                                                      "Unique_Test_Bl": unique_test_bl,
                                                      "Unique_Test_Work": unique_test_work,
                                                      "Unique_Test_Info": unique_test_info,
                                                      "Unique_Test_WallnWait_Time": unique_test_wallnwait_dt,
                                                      "Unique_Test_Run_Time": unique_test_run_dt,
                                                      "Unique_Test_Time": unique_test_time, # For RT logs, Wall + Wait + Run time. For Opn Req logs, referred to as "Total Wall Time"
                                                      "Unique_Test_Size": unique_test_sz, # Maximum resident set size (KB)
                                                      "Compared_Files": compare_d,
                                                      "Moved_Files": mv_d,
                                                      "Overall_Tests_Result": log_txt_list[-3].split(' ')[-1],
                                                      "Tests_Completed_Date": dtimes_completed,
                                                      "Elapsed_Time": tot_times}

            # Failed tests that are re-ran to fulfill a pass.
            # Note: The essential metrics, test's new wall time & test size, will only be re-captured 
            failed_regtest_list = []
            for idx, line in enumerate(txt.split('\n')):
                if "FAIL Tries" in line:
                    if log_fn.startswith('OpnReqTests'):
                        casentest = line.split(' ')[1] + ', ' + line.split(' ')[2]
                        failed_regtest_list.append(casentest)
                    elif log_fn.startswith('RegressionTests'):
                        failed_reg_test = line.split(' ')[2]
                        failed_regtest_list.append(failed_reg_test)
                for f in failed_regtest_list:
                    if f in line and line.endswith('PASS'):
                        # Wall time parsed & extracted
                        failed_test_new_time=txt.split('\n')[idx-3]
                        failed_test_new_time = float(failed_test_new_time.split("= ")[-1])
                        
                        # Max test size (Kb) parsed & extracted
                        failed_test_new_sz=txt.split('\n')[idx-2]
                        failed_test_new_sz = float(failed_test_new_sz.split("= ")[-1])

                        # Updates dictionary to the re-captured relevant metrics
                        self.parsed_txt_dict[(pf, commit_date)]["Unique_Test_Time"][f]= failed_test_new_time
                        self.parsed_txt_dict[(pf, commit_date)]["Unique_Test_Size"][f]= failed_test_new_sz
                        
        return self.parsed_txt_dict

    def map_metrics(self):
        """
        Maps out the metrics by platform & compiler

        Args:
            None
            
        Return: None

        """
        # Generate Wall Time & Size Dfs per platform-compiler.
        self.wall_time_dict = {}
        self.test_sz_dict = {}
        for (pf, commit_date), k2 in self.parsed_txt_dict.items():
            for testname_time, t in k2["Unique_Test_Time"].items():
                self.wall_time_dict[(k2["Test_Framework_Type"], pf, testname_time)] = t
            for testname_sz, sz in k2["Unique_Test_Size"].items():
                self.test_sz_dict[(k2["Test_Framework_Type"], pf, testname_sz)] = sz

        return self.wall_time_dict, self.test_sz_dict

    def generate_df(self):
        """
        Generates dataframe of the log metrics by framework type, compiler, & platform.

        Args:
             None
            
        Return (pd.DataFrame, pd.DataFrame): Dataframes of the wall time & test size
        metrics featured across all relevant UFS-WM log files.

        Note:
        - As of 2024, the following features will be established to
        comply with the current UFS-WM RT & OpnReq. Test framework structure:
        ['Test_Framework_Type', 'Platform', 'Test_Compiler']

        """
        # Wall Time dataframe w/ Wall Time ascending
        self.wall_time_df = pd.Series(self.wall_time_dict).reset_index()
        self.wall_time_df.columns = ['Test_Framework_Type', 'Filename_Description', 'Test_Description', 'Wall Time (HH:MM:SS)']
        self.wall_time_df = self.wall_time_df.sort_values('Wall Time (HH:MM:SS)').reset_index(drop=True)

        # Regression Test Logs wall time
        self.wall_time_df.loc[self.wall_time_df['Test_Framework_Type']=='Regression Testing', 'Platform'] = self.wall_time_df['Filename_Description']
        self.wall_time_df.loc[self.wall_time_df['Test_Framework_Type']=='Regression Testing', 'Test'] = self.wall_time_df['Test_Description'].str.rsplit('_',1).str[0]
        self.wall_time_df.loc[self.wall_time_df['Test_Framework_Type']=='Regression Testing', 'Compiler'] = self.wall_time_df['Test_Description'].str.split('_').str[-1]
        
        # Regression Test Compiler per Test. 
        # *NOTE: Regression Test Logs only declares compiler per test within test status line
        self.wall_time_df['Platform_Compiler'] = self.wall_time_df['Filename_Description'] + ' + ' + self.wall_time_df['Compiler']

        # Operation Req. Test Logs wall time
        self.wall_time_df.loc[self.wall_time_df['Test_Framework_Type']=='Operation Requirement Test', 'Platform'] = self.wall_time_df['Filename_Description'].str.rsplit('_',1).str[1]
        self.wall_time_df.loc[self.wall_time_df['Test_Framework_Type']=='Operation Requirement Test', 'Test'] = self.wall_time_df['Filename_Description'].str.rsplit('_',1).str[0] + ' + ' + self.wall_time_df['Test_Description']
        self.wall_time_df.loc[self.wall_time_df['Test_Framework_Type']=='Operation Requirement Test', 'Test Case'] = self.wall_time_df['Test_Description']
        
        # Operation Req. Test's Compiler per Test will be empty. 
        # Reason: Operation Req. Test Logs no longer declares compiler per test within test status line & extracting it from a directory filename is undesirable.
        self.wall_time_df.loc[self.wall_time_df['Test_Framework_Type']=='Operation Requirement Test', 'Platform_Compiler'] = self.wall_time_df['Platform']
        
        # Convert to datetime to minutes
        self.wall_time_df['Wall Time (min)'] = self.wall_time_df['Wall Time (HH:MM:SS)'].apply(lambda t: (t.hour * 60) + t.minute + (t.second/60) + ((t.microsecond)/((10**6)*60)))

        # Max Resident Size dataframe w/ Max Resident Set Size (KB) ascending
        self.test_sz_df = pd.Series(self.test_sz_dict).reset_index()
        self.test_sz_df.columns = ['Test_Framework_Type', 'Filename_Description', 'Test_Description', 'Max Resident Set Size (bytes)']
        self.test_sz_df = self.test_sz_df.sort_values('Max Resident Set Size (bytes)').reset_index(drop=True)

        # Regression Test Logs test size
        self.test_sz_df.loc[self.test_sz_df['Test_Framework_Type']=='Regression Testing', 'Platform'] = self.test_sz_df['Filename_Description']
        self.test_sz_df.loc[self.test_sz_df['Test_Framework_Type']=='Regression Testing', 'Test'] = self.test_sz_df['Test_Description'].str.rsplit('_',1).str[0]
        self.test_sz_df.loc[self.test_sz_df['Test_Framework_Type']=='Regression Testing', 'Compiler'] = self.test_sz_df['Test_Description'].str.split('_').str[-1]

        # Regression Test Compiler per Test. 
        # *NOTE: Regression Test Logs only declares compiler per test within test status line
        self.test_sz_df['Platform_Compiler'] = self.test_sz_df['Filename_Description'] + ' + ' + self.test_sz_df['Compiler']

        # Operation Req. Test Logs test size
        self.test_sz_df.loc[self.test_sz_df['Test_Framework_Type']=='Operation Requirement Test', 'Platform'] = self.test_sz_df['Filename_Description'].str.rsplit('_',1).str[1]
        self.test_sz_df.loc[self.test_sz_df['Test_Framework_Type']=='Operation Requirement Test', 'Test'] = self.test_sz_df['Filename_Description'].str.rsplit('_',1).str[0] + ' + ' + self.test_sz_df['Test_Description']
        self.test_sz_df.loc[self.test_sz_df['Test_Framework_Type']=='Operation Requirement Test', 'Test Case'] = self.test_sz_df['Test_Description']

        # Operation Req. Test's Compiler per Test will be empty. 
        # Reason: Operation Req. Test Logs no longer declares compiler per test within test status line & extracting it from a directory filename is undesirable.
        self.test_sz_df.loc[self.test_sz_df['Test_Framework_Type']=='Operation Requirement Test', 'Platform_Compiler'] = self.test_sz_df['Platform']
        #self.test_sz_df = self.test_sz_df.replace(np.nan, np.nan)

        # Note: Scale is adjusted to obtain e test size in MB as set within new version of UFS-WM RT logs (as of 03/08)
        test_sz_scaled2mb = 2**20
        self.test_sz_df['Max Resident Set Size (MB)'] = self.test_sz_df['Max Resident Set Size (bytes)'].apply(lambda x: x/(test_sz_scaled2mb))
        
        self.save_as_pkl(self.wall_time_df, "wall_time_df")
        self.save_as_pkl(self.test_sz_df, "test_sz_df")

        return self.wall_time_df, self.test_sz_df

    def generate_pivot_df(self, df, independent_feature_name):
        """
        Generate the pivot tables.

        Args:
             df (pd.DataFrame): Dataframe of either the wall time & test size
                                metrics featured across all relevant UFS-WM 
                                log files.

              independent_feature_name (str): Name of the feature to set as the independent variable.
                                              If converting wall time dataframe to pivot,
                                              then set to 'Wall Time'. If converting test 
                                              size dataframe to pivot, then set to 
                                              'Max Resident Set Size (KB)'
            
        Return (pd.DataFrame): Pivot dataframe of either the wall time &
        test size metrics featured across all relevant UFS-WM test logs.

        """
        # Pivoted features
        indep_feat_dict = defaultdict(dict)
        test_type = defaultdict(dict)
        for test in set(df['Test']):
            for idx, row in df.iterrows():
                if row['Test'] == test:
                    indep_feat_dict[test][row['Platform_Compiler']] = row[independent_feature_name]
                    test_type[row['Platform_Compiler']] = row['Test_Framework_Type']
        df = pd.DataFrame.from_dict(indep_feat_dict)
        df.index.name, df.columns.name = 'pf_2_comp', 'test'
        
        # Generate & append test frequency as new feature
        df['freq'] = df.count(axis='columns')
        df = df.sort_values(by='freq',
                            axis=0, 
                            ascending=False)
        df.insert(0, 'freq', df.pop('freq'))
        df = pd.DataFrame(pd.Series(test_type)).join(df)
        df.rename(columns={df.columns[0]: "Test_Framework_Type" }, inplace=True)
        df.rename(columns={'freq': 'Number of Tests'}, inplace=True)

        for idx, row in df.T.items():
            # Applies to only the Regression test logs because the Operaion Req. Test logs no longer declares 
            # compiler within test status
            if ' + ' in idx:
                df.loc[idx,'Platform']=idx.split(' + ')[0]
                df.loc[idx,'Compiler']=idx.split(' + ')[-1]
            else:
                df.loc[idx,'Platform'] = idx
                df.loc[idx,'Compiler'] = ''

        print(f'{independent_feature_name} pivot table:\n', df)
        self.save_as_pkl(df, f"{independent_feature_name}_pivot_df")
        
        return df

    def save_as_pkl(self, df, fn):
        """
        Save dataframe as pickle file.

        Args:
             df (pd.DataFrame): Dataframe to save as a pickle file.

             fn (str): Filename to save pickle file as.
            
        Return: None
        
        """
        df.to_pickle(f"dataframes/{fn}.pkl")
        
        return
