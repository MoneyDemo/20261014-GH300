"""提供原有主控台執行入口；執行前請先同步專案環境。"""

from bmi_calculator.app import bmi_calculator


if __name__ == "__main__":
    bmi_calculator()