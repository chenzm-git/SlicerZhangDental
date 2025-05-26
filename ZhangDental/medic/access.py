import json
import requests
import uuid
import platform
import subprocess

url = "http://146.56.234.222:5000/"


class License:
    @staticmethod
    def get_cpu_id():

        # 尝试获取CPU信息（不同系统方法不同）
        cpu_info = None
        try:
            if platform.system() == "Windows":
                # Windows系统使用WMIC命令
                output = subprocess.check_output("wmic csproduct get UUID", shell=True).decode()
                cpu_info = output.strip().split("\n")[-1].strip()
            elif platform.system() == "Linux":
                # Linux系统读取/proc/cpuinfo
                with open("/proc/cpuinfo", "r") as f:
                    for line in f:
                        if "processor" in line or "model name" in line:
                            cpu_info += line.strip() + "_"
            elif platform.system() == "Darwin":  # macOS
                # macOS使用sysctl命令
                output = subprocess.check_output("sysctl -n machdep.cpu.brand_string", shell=True).decode()
                cpu_info = output.strip()
        except Exception as e:
            # 出错时使用默认值
            cpu_info = None

        if not cpu_info:
            mac = uuid.getnode()
            # 转换为标准MAC地址格式 (如: 00:11:22:33:44:55)
            return ':'.join(("%012X" % mac)[i:i+2] for i in range(0, 12, 2))
        else:
            return cpu_info

    @staticmethod
    def get_method(method):
        param = {
            "method": method
        }
        resp = requests.post(url + "method", json=param)
        data = json.loads(resp.text)
        if data.get("data"):
            return data.get("data")
        else:
            return None
