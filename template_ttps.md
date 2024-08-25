
## Tools used by **{{GROUPE_NAME}}**

This page contains a list of which tools [`{{GROUPE_NAME}}`](group/{{GROUPE_NAME}}) uses. 

> [!INFO]
> This information is provided by [Ransomware-Tool-Matrix](https://github.com/BushidoUK/Ransomware-Tool-Matrix)

<!-- tabs:start -->
#### **Remote Monitoring & Management (RMM)**

> [!TIP]
> An RMM (Remote Monitoring and Management) tool is a type of software used by IT professionals and managed service providers (MSPs) to remotely monitor, manage, and maintain IT systems, networks, and devices. These tools are designed to improve the efficiency of IT operations by enabling technicians to handle tasks from a centralized location without the need for physical access to client devices.

> [!WARNING]
> By operating through legitimate RMM channels, attackers can evade detection by blending in with regular IT activities and potentially bypass security measures due to the elevated privileges these tools provide.

{{RMM-Tools}}

#### **Exfiltration**

> [!TIP] 
> File synchronization and management tools are designed to facilitate the efficient transfer, backup, and synchronization of files across various platforms and cloud storage services.

> [!WARNING]
> These tools can be misused to upload stolen data to attacker-controlled cloud accounts or destination servers. By leveraging encrypted data transfers, attackers can conceal their activities from network monitoring systems, blending malicious actions with legitimate operations. The legitimate nature of these tools often prevents immediate detection by security systems.

{{Exfiltration}}

#### **Credential Theft**

> [!TIP] 
>  There are a number of free password recovery tools availbel that are designed to help users recover lost or forgotten passwords stored on their own systems. These tools can extract passwords saved in web browsers, email clients, and other applications. IT professionals can use these tools to recover credentials needed for system maintenance or troubleshooting.

> [!WARNING]
> If these tools are run on a computer without the owner's permission by an adversary, they can be used to harvest passwords illicitly, leading to unauthorized access to sensitive information.

{{CredentialTheft}}

#### **Defense Evasion**

> [!TIP] 
> Various freely available malware detection tools specialize in identifying and removing stealthy threats like rootkits. They offer capabilities such as scanning for hidden processes, files, and drivers, analyzing system memory for malicious modules, and monitoring system hooks for unauthorized modifications. These tools provide detailed insights into system internals, helping to uncover deeply embedded malware that standard antivirus programs might miss.

> [!WARNING]
> Malicious actors can abuse these rootkit detection tools to interfere with security tools, file and registry tampering to disrupt tool functionality, and memory corruption to prevent detection. By using these tools for privilege escalation, an adversary can disable or alter the operation of security software, removing the method systems use to detect or prevent threats.

{{DefenseEvasion}}

#### **Networking**

> [!TIP]
> There are a number of network tunneling tools available online for managing and interacting with systems across different environments. They allow users to securely connect to remote servers or services through encrypted channels that can bypass network restrictions and firewalls. These tools may also expose local development servers to the internet for testing and sharing. They are widely used for tasks like remote administration and development workflows, offering flexibility in network management.

> [!WARNING]
> Cybercriminals can utilize network tunneling tools to create encrypted tunnels, evade detection, and access restricted networks. These tools essentially facilitate command and control for an adversary, helping them to maintain a foothold and orchestrate further malicious activities.

{{Networking}}

#### **Discovery and Enumeration**

> [!TIP] 
> There are a number of network scanning and profiling tools available online that are designed to help administrators and IT professionals with tasks such as discovering and mapping network devices, performing detailed scans of IP addresses and open ports, and querying network services like Active Directory.

> [!WARNING]
> Malicious adversaries leverage these network management tools to perform reconnaissance and gather detailed information about a target network. They can use these tools to identify active devices, open ports, and vulnerabilities, which could then be exploited to gain entry. Additionally, querying tools for active directory services could allow them to harvest sensitive information about users, groups, and permissions, facilitating targeted attacks or insider threats. Essentially, these tools, while valuable for legitimate network management, can be misused to map out and exploit network infrastructures for nefarious purposes.

{{DiscoveryEnum}}

#### **Offensive Security**

> [!TIP]
> Offensive security tools are developed by professional ethical hackers to simulate cyber-attacks and evaluate an organization's defenses. These tools offer powerful features for post-exploitation activities, such as stealthy communications, lateral movement, and advanced command and control capabilities. Some tools focus on evasion techniques to bypass modern security defenses, allowing for realistic threat simulations and payload development.

> [!WARNING]
> Cybercriminals can obtain offensive security tools through various means, often exploiting legitimate channels or resorting to illegal methods to acquire them. These tools also allow attackers to automate parts of their attacks, making them more efficient and widespread.

{{Offsec}}

#### **Living-off-the-Land Binaries and Scripts**

> [!TIP] 
> Windows environments are equipped with a wide array of command-line utilities. These tools collectively provide robust support for efficient system management, troubleshooting, and optimization, helping administrators maintain secure, stable, and high-performing Windows environments.


> [!WARNING]
> Cybercriminals often exploit legitimate Windows administrative tools to execute malicious actions while evading detection. These tools, used for tasks such as remote execution, file transfers, and system management, allow attackers to move laterally across networks, download and execute malware, manipulate logs, and gather sensitive information. By leveraging these built-in utilities, attackers can conduct their activities stealthily, blending their actions with normal administrative operations.
    
{{LOLBAS}}

<!-- tabs:end -->

> [!NOTE]
> This is the list of tools that have been observed during various intrusions that lead to Akira ransomware deployment.