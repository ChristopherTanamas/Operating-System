import os  # Untuk operasi sistem seperti perubahan direktori
import subprocess  # Untuk menjalankan perintah shell

def execute_command(command):
    try:
        background = False
        if command.endswith('&'):  # Cek apakah perintah harus dijalankan di background
            background = True
            command = command[:-1].strip()  # Hapus '&' dari akhir perintah
        
        if os.name == 'nt':  # Cek apakah sistem operasi adalah Windows
            # Penanganan khusus untuk redirect output di Windows
            if '>' in command:
                command_parts = command.split('>')
                cmd = command_parts[0].strip()
                output_file = command_parts[1].strip()
                
                if cmd.startswith('ls'):
                    # Penanganan khusus untuk perintah 'ls' dengan redirect
                    dir_cmd = get_windows_ls_command(cmd)
                    with open(output_file, 'w') as f:
                        subprocess.run(dir_cmd, shell=True, stdout=f, text=True)
                    return False
                
            else:
                # Terjemahan perintah Unix ke Windows
                command_parts = command.split('|')
                for i, part in enumerate(command_parts):
                    cmd = part.strip().split()[0]
                    if cmd == 'ls':
                        command_parts[i] = get_windows_ls_command(part)
                    elif cmd == 'sleep':
                        # Ganti 'sleep' dengan 'timeout' tanpa countdown
                        sleep_time = part.split()[1]
                        command_parts[i] = f'timeout /t {sleep_time} /nobreak > nul'
                    elif cmd == 'grep':
                        command_parts[i] = part.replace('grep', 'findstr')
                    elif cmd == 'cat':
                        if '<' in part:
                            # Ganti 'cat < file' dengan 'type file'
                            _, file = part.split('<')
                            command_parts[i] = f'type {file.strip()}'
                        else:
                            command_parts[i] = part.replace('cat', 'type')
                command = ' | '.join(command_parts)
        
        if background:
            # Jalankan perintah di background
            subprocess.Popen(command, shell=True)
            return False
        else:
            # Jalankan perintah dan tangkap output
            result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
            if result.stdout:
                print(result.stdout.rstrip())
                return True
            if result.stderr:
                print(result.stderr.rstrip())
                return True
            return False

    except subprocess.CalledProcessError:
        print(f"shelly: invalid command: {command}")
        return True
    except Exception as e:
        print(f"shelly: error executing command: {e}")
        return True
    
def get_windows_ls_command(ls_command):
    # Terjemahkan perintah 'ls' Unix ke perintah Windows yang setara
    if '-l' in ls_command:
        # Untuk 'ls -l', gunakan PowerShell untuk output yang lebih mirip
        return f'powershell -Command "Get-ChildItem | Select-Object Mode, Length, LastWriteTime, Name | Format-Table -AutoSize | Out-String -Width 4096"'
    else:
        # Untuk 'ls' biasa, gunakan 'dir /B'
        return f'dir /B "{os.getcwd()}"'

def change_directory(path):
    try:
        os.chdir(os.path.abspath(path))  # Ubah direktori kerja
        return False
    except FileNotFoundError:
        print(f"shelly: directory not found: {path}")
        return True
    except Exception as e:
        print(f"shelly: error changing directory: {e}")
        return True

def shelly():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)  # Mulai dari direktori script
    output_produced = False

    while True:
        if output_produced:
            print()  # Tambah baris baru jika perintah sebelumnya menghasilkan output
        command = input(f"shelly$ ").strip()  # Tampilkan prompt dan terima input
        
        if command.lower() == "exit":
            break  # Keluar dari loop jika perintah adalah 'exit'
        
        if command.startswith("cd "):
            output_produced = change_directory(command[3:])  # Ubah direktori
        elif command == "pwd":
            print(os.getcwd())  # Tampilkan direktori kerja saat ini
            output_produced = True
        else:
            output_produced = execute_command(command)  # Jalankan perintah lainnya

if __name__ == "__main__":
    shelly()  # Jalankan shell jika script dijalankan langsung