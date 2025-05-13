#!/usr/bin/env python3
import os
import subprocess
import readline
import random
import time
from datetime import datetime, timedelta
import shutil
import sys
import pwd
from faker import Faker
import threading
from enum import Enum

class UserProfile(Enum): # (Enum) means that UserProfile inherits from the Enum base class, which is how Python knows this is an enumeration, not a regular class.
    ADMIN = "admin"
    DEVELOPER = "developer"
    SYSADMIN = "sysadmin"
    GENERAL = "general"
    '''
    - An enum is a symbolic name for a set of values. Enumerations are used when you have a fixed set of related constants that are conceptually grouped together. 
    For example: roles, status codes, states, directions, etc.
    '''

class LinuxUserSimulator:
    def __init__(self, num_commands=50, num_sudo=10, num_cronjobs=3, user=None, profile=UserProfile.GENERAL):
        self.num_commands = num_commands
        self.num_sudo = num_sudo
        self.num_cronjobs = num_cronjobs
        self.fake = Faker()
        self.user = user or os.getenv('SUDO_USER', os.getenv('USER'))
        self.profile = profile if isinstance(profile, UserProfile) else UserProfile(profile)
        self.ensure_user_exists(self.user)
        self.home_dir = pwd.getpwnam(self.user).pw_dir
        self.bash_history = os.path.join(self.home_dir, '.bash_history')
        self.bashrc = os.path.join(self.home_dir, '.bashrc')
        self.auth_log = '/var/log/auth.log'
        self.crontab = '/etc/crontab'
        self.sudoers = '/etc/sudoers'
        self.commands_executed = []
        self.setup_directories()
        
        # Profile-specific adjustments
        if self.profile == UserProfile.ADMIN:
            self.num_sudo = max(self.num_sudo, int(self.num_commands * 0.4)) # It normalizes or boosts sudo usage numbers to match what’s expected for a user with elevated privileges like an ADMIN.
            self.num_cronjobs = max(self.num_cronjobs, 5) # It ensures that the user has at least 5 cron jobs (self.num_cronjobs).
        elif self.profile == UserProfile.DEVELOPER:
            self.num_sudo = max(3, int(self.num_sudo * 0.5))
        elif self.profile == UserProfile.SYSADMIN:
            self.num_sudo = max(self.num_sudo, int(self.num_commands * 0.3))

    def ensure_user_exists(self, username):
        try:
            pwd.getpwnam(username)
        except KeyError:
            print(f"User {username} not found - creating...")
            try:
                subprocess.run([
                    'sudo', 'useradd',
                    '-m',             # Create home directory
                    '-s', '/bin/bash', # Set default shell
                    username
                ], check=True)
                subprocess.run([
                    'sudo', 'chpasswd',
                ], input=f"{username}:password", encoding='ascii', check=True)
                print(f"Created user {username} with home directory /home/{username}")
            except subprocess.CalledProcessError as e:
                print(f"Failed to create user: {e}")
                sys.exit(1)

    def setup_directories(self):
        try:
            # Backup original files if they exist
            for f in [self.bash_history, self.bashrc]:
                if os.path.exists(f):
                    shutil.copy2(f, f + '.bak')
        except Exception as e:
            print(f"Warning: Could not backup files: {e}")

    def generate_plausible_command(self, use_sudo=False):
        # Base command sets, if the General user profile is selected.
        base_commands = {
            'file_ops': [
                f"vim {self.fake.file_name(extension='txt')}",
                f"nano {self.fake.file_name(extension='conf')}",
                f"cat {self.fake.file_path(depth=3)}",
                f"grep -r '{self.fake.word()}' {random.choice(['/etc', '/var/log', '/home'])}",
                f"tail -n 20 {random.choice(['/var/log/syslog', '/var/log/auth.log'])}",
                f"ls -la {random.choice(['~', '/tmp', '/etc'])}",
                f"cp {self.fake.file_path(depth=2)} {self.fake.file_path(depth=1)}",
                f"mv {self.fake.file_name()} {self.fake.file_name()}"
            ],
            'network': [
                "curl -I https://example.com",
                "wget https://example.com/file.zip",
                "ping -c 4 8.8.8.8",
                "netstat -tuln",
                "ss -tuln",
                "dig example.com",
                "nslookup google.com"
            ],
            'system': [
                "df -h",
                "free -m",
                "top -n 1 -b",
                "ps aux",
                "uname -a",
                "lsb_release -a",
                "systemctl status sshd",
                "journalctl -xe"
            ],
            'package': [
                "apt update",
                "apt list --upgradable",
                "dnf check-update",
                "yum update",
                "pip list --outdated",
                "snap refresh --list"
            ]
        }
        
        # Profile-specific commands
        profile_commands = {
            UserProfile.ADMIN: {
                'common': [
                    "vim /etc/ssh/sshd_config",
                    "nano /etc/nginx/nginx.conf",
                    "cat /etc/passwd",
                    "useradd " + self.fake.user_name(),
                    "usermod -aG sudo " + self.fake.user_name(),
                    "chown -R root:root /etc/"
                ],
                'sudo': [
                    "systemctl restart nginx",
                    "journalctl -u sshd -f",
                    "ufw allow 22/tcp",
                    "iptables -L -n -v",
                    "visudo",
                    "chmod 600 /etc/shadow"
                ]
            },
            UserProfile.DEVELOPER: {
                'common': [
                    "git pull origin main",
                    "git commit -am '" + self.fake.sentence() + "'",
                    "git push origin main",
                    "python3 setup.py install",
                    "pip install -r requirements.txt",
                    "docker build -t " + self.fake.word() + " .",
                    "docker-compose up -d",
                    "npm install " + self.fake.word(),
                    "mvn clean install"
                ],
                'sudo': [
                    "docker run -d -p 8080:80 nginx",
                    "systemctl restart docker",
                    "apt install -y " + random.choice(['python3-pip', 'nodejs', 'golang', 'openjdk-11-jdk'])
                ]
            },
            UserProfile.SYSADMIN: {
                'common': [
                    "ss -tuln",
                    "netstat -plant",
                    "df -h",
                    "free -m",
                    "uptime",
                    "who",
                    "last",
                    "cat /var/log/syslog | grep -i error",
                    "tail -f /var/log/nginx/access.log",
                    "du -sh /var/*"
                ],
                'sudo': [
                    "systemctl restart " + random.choice(['nginx', 'apache2', 'mysql', 'postgresql']),
                    "apt-get update && apt-get upgrade -y",
                    "ufw status verbose",
                    "smartctl -a /dev/sda",
                    "zpool status",
                    "virsh list --all"
                ]
            }
        }

        if use_sudo:
            if self.profile in profile_commands:
                sudo_commands = profile_commands[self.profile].get('sudo', [])
            else:
                sudo_commands = [
                    "apt install -y " + self.fake.word(),
                    "systemctl restart " + random.choice(['nginx', 'apache2', 'ssh', 'postgresql']),
                    "useradd " + self.fake.user_name(),
                    "usermod -aG " + random.choice(['sudo', 'docker', 'adm']) + " " + self.fake.user_name(),
                    "chown -R " + self.fake.user_name() + ":" + self.fake.user_name() + " " + self.fake.file_path(depth=1),
                    "chmod 755 " + self.fake.file_path(depth=2),
                    "visudo"
                ]
            return "sudo " + random.choice(sudo_commands)
        
        if self.profile in profile_commands:
            profile_specific = profile_commands[self.profile].get('common', [])
            if profile_specific and random.random() > 0.6:
                return random.choice(profile_specific)
        
        category = random.choice(list(base_commands.keys())) # If GENERAL was selected
        return random.choice(base_commands[category])

    def run_command(self, command):
        try:
            if random.random() > 0.2:
                if command.startswith('sudo'):
                    self.log_sudo_command(command)
                else:
                    try:
                        subprocess.run(command, shell=True, check=False, 
                                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    except:
                        pass
            
            self.commands_executed.append(command)
            return True
        except Exception as e:
            print(f"Error executing command: {e}")
            return False

    def log_sudo_command(self, command):
        sudo_log_entry = (
            f"{datetime.now().strftime('%b %d %H:%M:%S')} {os.uname().nodename} "
            f"sudo: {self.user} : TTY=pts/{random.randint(0,3)} ; "
            f"PWD={self.fake.file_path(depth=3)} ; USER=root ; "
            f"COMMAND={command[5:]}\n"
        )
        
        try:
            with open(self.auth_log, 'a') as f:
                f.write(sudo_log_entry)
        except PermissionError:
            print(f"Warning: Could not write to {self.auth_log} (run with sudo?)")

    def add_to_bash_history(self):
        try:
            with open(self.bash_history, 'a') as f:
                for cmd in self.commands_executed:
                    f.write(cmd + "\n")
        except Exception as e:
            print(f"Error writing to bash history: {e}")

    def add_cron_jobs(self):
        cron_jobs = []
        
        interpreters = [
            "/usr/bin/python3",
            "/usr/bin/python2",
            "/usr/bin/perl",
            "/usr/bin/bash",
            "/usr/bin/ruby",
            "/usr/bin/node",
            "/bin/bash"
        ]
        
        for _ in range(self.num_cronjobs):
            minute = random.randint(0, 59)
            hour = random.randint(0, 23)
            day_of_month = random.randint(1, 31)
            month = random.randint(1, 12)
            day_of_week = random.randint(0, 6)

            random_folder = self.fake.word()
            random_file_name = self.fake.word()
            file_extension = random.choice([".py", ".sh", ".bat", ".pl", ".php", ".js"])
            
            random_file_path = f"/home/{self.user}/{random_folder}/{random_file_name}{file_extension}"
            
            random_interpreter = random.choice(interpreters)
            
            cron_job = f"{minute} {hour} {day_of_month} {month} {day_of_week} {self.user} {random_interpreter} {random_file_path}\n"
            cron_jobs.append(cron_job)
        
        try:
            with open(self.crontab, 'a') as f:
                f.write("\n# Added by user activity simulator\n")
                for job in cron_jobs:
                    f.write(job)
        except PermissionError:
            print(f"Warning: Could not write to {self.crontab} (run with sudo?)")

    def modify_bashrc(self):
        alias_commands = [
            "ls -la", "cd ..", "git status", "top", "htop", "cat /etc/passwd",
            "find / -name 'test*'", "echo 'hello world'", "df -h", "ps aux", "free -m"
        ]
        
        path_additions = [
            "/home/" + self.user + "/.local/bin",
            "/usr/local/bin",
            "/opt/bin"
        ]
        
        ps1_formats = [
            "PS1='\\[\\033[01;32m\\]\\u@\\h\\[\\033[00m\\]:\\[\\033[01;34m\\]\\w\\[\\033[00m\\]\\$ '",
            "PS1='\\[\\033[01;31m\\]\\u@\\h\\[\\033[00m\\]:\\[\\033[01;33m\\]\\w\\[\\033[00m\\]\\$ '",
            "PS1='\\[\\033[01;36m\\]\\u@\\h\\[\\033[00m\\]:\\[\\033[01;35m\\]\\w\\[\\033[00m\\]\\$ '",
            "PS1='\\[\\033[01;34m\\]\\u@\\h\\[\\033[00m\\]:\\[\\033[01;37m\\]\\w\\[\\033[00m\\]\\$ '"
        ]
        
        random_alias_command = f"alias {self.fake.word()}='{random.choice(alias_commands)}'"
        random_path = random.choice(path_additions)
        random_ps1 = random.choice(ps1_formats)
        
        additions = [
            "\n# Custom aliases added by simulation\n",
            random_alias_command + "\n",
            f"export PATH=$PATH:{random_path}\n",
            random_ps1 + "\n"
        ]
        
        try:
            with open(self.bashrc, 'a') as f:
                f.writelines(additions)
            print(f"[*] Customizations added to {self.bashrc}")
        except Exception as e:
            print(f"Error modifying .bashrc: {e}")

    def create_temp_files(self):
        for _ in range(random.randint(3, 25)):
            filename = f"/tmp/{self.fake.file_name()}"
            content = self.fake.text(max_nb_chars=200)
            try:
                with open(filename, 'w') as f:
                    f.write(content)
            except Exception as e:
                print(f"Error creating temp file: {e}")

    def simulate(self):
        print(f"[*] Simulating {self.num_commands} commands for {self.profile.value} user {self.user}...")
        
        for _ in range(self.num_commands - self.num_sudo):
            cmd = self.generate_plausible_command()
            self.run_command(cmd)
        
        for _ in range(self.num_sudo):
            cmd = self.generate_plausible_command(use_sudo=True)
            self.run_command(cmd)
        
        self.add_to_bash_history()
        self.add_cron_jobs()
        self.modify_bashrc()
        self.create_temp_files()
        
        print("[*] Simulation complete. Artifacts generated:")
        print(f"     - {len(self.commands_executed)} commands added to {self.bash_history}")
        print(f"     - {self.num_sudo} sudo commands logged to {self.auth_log}")
        print(f"     - {self.num_cronjobs} cron jobs added to {self.crontab}")
        print(f"     - Customizations added to {self.bashrc}")
        print(f"     - Temporary files written to /tmp")

def simulate_concurrent_users(users_config):
    threads = [] # empty list threads is created to store all the threads that will be created in the function. This allows us to manage and wait for them to complete later.
    
    for config in users_config: # The function expects an argument users_config, which is presumably a list of configurations for different users.
        t = threading.Thread(target=run_single_simulation, args=(config,))
        threads.append(t)
        t.start() # starts the thread, meaning the simulation for the user begins executing concurrently in a separate thread.
        time.sleep(random.uniform(0.1, 1.5))
        '''
        After starting each thread, the function sleeps for a random duration between 0.1 and 1.5 seconds using random.uniform(0.1, 1.5). This simulates a delay 
        between starting each user's simulation, making the user actions less predictable and simulating real-world scenarios where users may not all start at 
        the exact same time.
        To ensure the threads don’t start simultaneously, a random sleep time between 0.1 and 1.5 seconds is added after each thread is started. This simulates 
        users starting at different times.
        '''
    
    for t in threads:
        t.join() # blocking call that makes the main program wait for the thread t to complete before continuing.
        # Finally, the t.join() method is called on each thread, ensuring the main program waits for all threads to finish before it proceeds.

def run_single_simulation(config):
    try:
        simulator = LinuxUserSimulator(
            num_commands=config.get('num_commands', 50),
            num_sudo=config.get('num_sudo', 10),
            num_cronjobs=config.get('num_cronjobs', 3),
            user=config.get('user'),
            profile=config.get('profile', UserProfile.GENERAL)
        )
        simulator.simulate()
    except Exception as e:
        print(f"Error simulating user {config.get('user')}: {e}")

def display_centered_ascii_art():
    ascii_art = r"""
 _________  ___  ___     ___    ___ _________  ________  ________  ________  _______      
|\___   ___\\  \|\  \   |\  \  /  /|\___   ___\\   __  \|\   __  \|\   ____\|\  ___ \     
\|___ \  \_\ \  \\\  \  \ \  \/  / ||___ \  \_\ \  \|\  \ \  \|\  \ \  \___|\ \   __/|    
     \ \  \ \ \  \\\  \  \ \    / /     \ \  \ \ \   _  _\ \   __  \ \  \    \ \  \_|/__  
      \ \  \ \ \  \\\  \  /     \/       \ \  \ \ \  \\  \\ \  \ \  \ \  \____\ \  \_|\ \ 
       \ \__\ \ \_______\/  /\   \        \ \__\ \ \__\\ _\\ \__\ \__\ \_______\ \_______\
        \|__|  \|_______/__/ /\ __\        \|__|  \|__|\|__|\|__|\|__|\|_______|\|_______|
                        |__|/ \|__|                                                       
    """
    terminal_width = shutil.get_terminal_size().columns
    centered_art = [line.center(terminal_width) for line in ascii_art.split('\n')]
    print('\n'.join(centered_art))

def main():
    display_centered_ascii_art()
    print("[*] This script simulates user activity and generates forensic artifacts.\n")
    print("--- --- --- ---\n")
    
    try:
        while True:  # Keep asking until we get valid input
            mode = input("==> Simulation mode (single/multi): ").lower() or "single"
            
            if mode == "single":
                num_commands = int(input("==> Number of commands to simulate (default 50): ") or 50)
                num_sudo = int(input("==> Number of sudo commands to simulate (default 10): ") or 10)
                num_cronjobs = int(input("==> Number of cron jobs to add (default 3): ") or 3)
                username = input(f"==> Username to simulate (default {os.getenv('SUDO_USER', os.getenv('USER'))}): ") or None
                profile = input("==> User profile (admin/developer/sysadmin/general): ").lower() or "general"
                
                simulator = LinuxUserSimulator(
                    num_commands=num_commands,
                    num_sudo=num_sudo,
                    num_cronjobs=num_cronjobs,
                    user=username,
                    profile=profile
                )
                
                print("\n[*] Note: Some operations require sudo privileges. You may be prompted for your password.")
                print("\n[*] Starting simulation...\n")
                simulator.simulate()
                break  # Exit the loop after successful simulation
                
            elif mode == "multi":
                num_users = int(input("==> Number of users to simulate (default 3): ") or 3)
                users_config = []
                
                for i in range(num_users):
                    print(f"\nConfiguring user #{i+1}:")
                    username = input(f"==> Username (leave blank for current): ") or None
                    profile = input("==> Profile (admin/developer/sysadmin/general): ").lower() or "general"
                    commands = int(input("==> Commands per user (default 30): ") or 30)
                    sudo = int(input("==> Sudo commands (default 5): ") or 5)
                    cronjobs = int(input("==> Cron jobs (default 1): ") or 1)
                    
                    users_config.append({
                        'user': username,
                        'profile': profile,
                        'num_commands': commands,
                        'num_sudo': sudo,
                        'num_cronjobs': cronjobs
                    })
                
                print("\n[*] Starting concurrent simulation...")
                simulate_concurrent_users(users_config)
                print("\n[*] All user simulations completed")
                break  # Exit the loop after successful simulation
                
            else:
                print("[!] Invalid mode. Please enter either 'single' or 'multi'.")
                continue  # Ask again
            
    except KeyboardInterrupt:
        print("\n[!] Simulation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"[!] Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if os.geteuid() == 0:
        main()
    else:
        print("[!] Warning: Some features require root privileges. Consider running with sudo.")
        main()