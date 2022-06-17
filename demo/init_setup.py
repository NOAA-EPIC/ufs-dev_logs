import os
from git import Repo


class init_setup():
    """
    Establish a connection with GitHub for cloning GitHub repository of interest.
    
    ** NOTE: User will have to create a config.py file comprised of the username(str)
    and token(str) for GitHub login access.
    
    """
    def __init__(self, username, token, repo_abbrev, branch):
        """
        Args:
            username (str): GitHub username.
            token (str): GitHub token.
            repo_abbrev (str): GitHub repo of interest. for UFS-WM repo, set to 'ufs-wm'.
            branch(str): Name of the repo branch to clone. 
            
        ** TODO: This will change branch to "develop"
        
        """
        
        # Current working directory.
        self.current_dir = os.getcwd() 
        
        # Repo & branch of interest to clone.
        self.username = username
        self.token = token
        self.repo_abbrev = repo_abbrev
        self.branch = branch
        if self.repo_abbrev == 'ufs-wm':
            
            # Establish a local folder for the cloned repo
            self.local_repo_folder = '/ufs-repo'
            
            # Clone UFS-WM repository. ** TODO: This will change to f"https://{self.username}:{self.token}@github.com/ufs-community/ufs-weather-model.git"
            self.git_remote_url = f"https://{self.username}:{self.token}@github.com/NOAA-EPIC/ufs-dev_logs.git"
            
        # Setup UFS-WM repository on local folder
        self.local_repo_dir = self.current_dir + self.local_repo_folder
    
        if not os.path.exists(self.local_repo_dir):
            os.makedirs(self.local_repo_dir)
            print(f"Created Local Directory For {self.repo_abbrev} Repo:\n{self.local_repo_dir}")
        
        # Clone 'main' repo to local folder. ** TODO: This will change to "develop"
        print(f"Cloning GitHub Repository for {self.repo_abbrev}'s {self.branch}:\n")
        self.repo_handle = Repo.clone_from(self.git_remote_url, self.local_repo_dir, branch=self.branch)
        print(f"GitHub Repository for {self.repo_abbrev}'s {self.branch} Has Been Cloned to {self.local_repo_dir}")