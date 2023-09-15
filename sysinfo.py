import platform
import subprocess
import webbrowser
import psutil
import sys

def install_psutil():
    try:
        # Check if psutil is already installed
        import psutil
    except ImportError:
        # If not installed, attempt to install it using pip
        try:
            subprocess.check_call(['pip', 'install', 'psutil'])
        except subprocess.CalledProcessError as e:
            print(f"Error installing psutil: {e}")

def gather_network_info():
    # Get network information
    network_info = {
        "Hostname": platform.node(),
        "IP Address": psutil.net_if_addrs().get('Ethernet')[0].address,
        "Subnet Mask": psutil.net_if_addrs().get('Ethernet')[0].netmask,
    }
    return network_info

def gather_domain_info():
    # Get domain information (Windows-specific)
    domain_info = {}
    if platform.system() == "Windows":
        try:
            import wmi
            c = wmi.WMI()
            computer = c.Win32_ComputerSystem()[0]
            domain_info = {
                "Domain": computer.Domain,
                "Workgroup": computer.Workgroup,
            }

            # Check if joined to Azure AD
            azuread_status = subprocess.check_output(['dsregcmd', '/status']).decode()
            if "AzureAdJoined" in azuread_status:
                domain_info["Azure AD Joined"] = "Yes"
            else:
                domain_info["Azure AD Joined"] = "No"
        except ImportError:
            pass
    return domain_info

def gather_storage_info():
    # Get storage information
    partitions = psutil.disk_partitions()
    storage_info = {}
    for partition in partitions:
        partition_usage = psutil.disk_usage(partition.mountpoint)
        storage_info[partition.device] = {
            "Total Size (GB)": round(partition_usage.total / (1024 ** 3), 2),
            "Used Space (GB)": round(partition_usage.used / (1024 ** 3), 2),
            "Free Space (GB)": round(partition_usage.free / (1024 ** 3), 2),
            "Usage Percentage": partition_usage.percent,
        }
    return storage_info

def gather_hardware_info():
    # Get hardware information
    cpu_info = {
        "CPU Cores": psutil.cpu_count(logical=False),
        "Logical CPUs": psutil.cpu_count(logical=True),
        "CPU Usage (%)": psutil.cpu_percent(interval=1, percpu=True),
    }

    memory_info = {
        "Total Memory (GB)": round(psutil.virtual_memory().total / (1024 ** 3), 2),
        "Available Memory (GB)": round(psutil.virtual_memory().available / (1024 ** 3), 2),
    }

    return cpu_info, memory_info

def generate_html_report():
    # Create an HTML file and write system information to it
    with open("system_info.html", "w") as html_file:
        html_file.write("<html>\n")
        html_file.write("<head><title>System Information</title></head>\n")
        html_file.write("<body>\n")
        html_file.write("<h1>System Information</h1>\n")

        # Gather and write network information
        network_info = gather_network_info()
        html_file.write("<h2>Network Info</h2>\n")
        html_file.write("<ul>\n")
        for key, value in network_info.items():
            html_file.write(f"<li>{key}: {value}</li>\n")
        html_file.write("</ul>\n")

        # Gather and write domain information
        domain_info = gather_domain_info()
        html_file.write("<h2>Domain Info</h2>\n")
        html_file.write("<ul>\n")
        for key, value in domain_info.items():
            html_file.write(f"<li>{key}: {value}</li>\n")
        html_file.write("</ul>\n")

        # Gather and write storage information
        storage_info = gather_storage_info()
        html_file.write("<h2>Storage Info</h2>\n")
        html_file.write("<ul>\n")
        for device, device_info in storage_info.items():
            html_file.write(f"<li>{device}:\n")
            html_file.write("<ul>\n")
            for key, value in device_info.items():
                html_file.write(f"<li>{key}: {value}</li>\n")
            html_file.write("</ul>\n")
            html_file.write("</li>\n")
        html_file.write("</ul>\n")

        # Gather and write hardware information
        cpu_info, memory_info = gather_hardware_info()
        html_file.write("<h2>Hardware Info</h2>\n")
        html_file.write("<h3>CPU Info</h3>\n")
        html_file.write("<ul>\n")
        for key, value in cpu_info.items():
            html_file.write(f"<li>{key}: {value}</li>\n")
        html_file.write("</ul>\n")
        html_file.write("<h3>Memory Info</h3>\n")
        html_file.write("<ul>\n")
        for key, value in memory_info.items():
            html_file.write(f"<li>{key}: {value}</li>\n")
        html_file.write("</ul>\n")

        html_file.write("</body>\n")
        html_file.write("</html>\n")

    # Open the HTML file in the default web browser
    webbrowser.open("system_info.html")

if __name__ == "__main__":
    # If running as an executable, generate the HTML report
    if getattr(sys, 'frozen', False):
        generate_html_report()
    else:
        # If running as a script, install necessary dependencies and generate the report
        install_psutil()
        generate_html_report()